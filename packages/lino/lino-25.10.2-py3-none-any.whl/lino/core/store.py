# Copyright 2009-2021 Rumma & Ko Ltd
# License: GNU Affero General Public License v3 (see file COPYING for details)
"""Defines the "store" and its "fields" .

During startup, Lino instantiates a "store" and its "fields" (aka
"atomizers") for every table.  These were used originally for dealing
with Sencha ExtJS GridPanels and FormPanels, but the concept turned
out useful for other features.

Some usages specific to Sencha ExtJS:

- for generating the JS code of the GridPanel definition
- for generating an "atomized" JSON representation when
  rendering data for that GridPanel
- for parsing the JSON sent by GridPanel and FormPanel

Other usages:

- remote fields (:class:`lino.core.fields.RemoteField`)

- render tables as text
  (:meth:`lino.core.renderer.TextRenderer.show_table` and
  :meth:`lino.core.requests.ActionRequest.row2text`)

"""

from lino import logger

import datetime

from django.conf import settings
from django.db import models
# from django.db.models.fields import Field
from django.core import exceptions
from django.utils.translation import gettext_lazy as _
from django.utils.encoding import force_str
# from lino import AFTER17

from lino.utils.jsgen import py2js
from lino.utils.quantities import parse_decimal
from lino.core.utils import getrqdata
from lino.core.gfks import GenericForeignKey
from lino.core import constants
from lino.core import fields
# from lino.core import actors
from lino.core import actions
from lino.core import frames
from lino.core import atomizer
from lino.core.utils import PhantomRow
# from lino.utils import choosers
from lino.utils import curry
from lino.utils import iif
from lino.utils.format_date import fds
from lino.utils import IncompleteDate
from lino.core.utils import DelayedValue

FIELD_TYPES = {}


class StoreField(object):
    """
    Base class for the fields of a :class:`Store`.

    .. attribute:: field

        The database field (a subclass of
        `django.db.models.fields.Field`)

    .. attribute:: options

        A `dict` with options to be used by :meth:`as_js`.


    Note: `value_from_object` and `full_value_from_object` are
    similar, but for ForeignKeyStoreField and GenericForeignKeyField
    one returns the primary key while the latter returns the full
    instance.
    """

    form2obj_default = None
    "because checkboxes are not submitted when they are off"

    list_values_count = 1
    "Necessary to compute :attr:`Store.pk_index`."

    delayed_value = False

    def __init__(self, field, name, **options):
        # if not isinstance(field, (fields.FakeField, Field, GenericForeignKey)):
        #     raise Exception("20210623 {} is not a field".format(field))
        self.field = field
        self.name = str(name)  # TypeError 20160425
        self.options = options
        # if settings.SITE.kernel.default_ui.support_async:
        # if settings.SITE.default_ui == "lino_react.react":
        editing_wf = settings.SITE.kernel.editing_front_end
        if editing_wf and editing_wf.support_async:
            if isinstance(field, fields.FakeField) and field.delayed_value:
                self.delayed_value = True
                # print("20210619 StoreField.delayedValue is True", name)
            # else:
            #     print("20210619 StoreField.delayedValue is False", name)

    def as_js(self, name):
        """
        Return a Javascript string which defines this atomizer as an
        object. This is used by :mod:`lino.modlib.extjs.ext_renderer`.
        and in case of virtual remote fields they use the
        virtual field's delegate as_js method but with their own name.

        """
        self.options.update(name=name)
        return py2js(self.options)

    def __repr__(self):
        return "%s '%s'" % (self.__class__.__name__, self.name)

    def column_names(self):
        # if not self.options.has_key('name'):
        # raise Exception("20130719 %s has no option 'name'" % self)
        # yield self.options['name']
        yield self.name

    def value_from_object(self, obj, ar=None):
        return self.full_value_from_object(obj, ar)

    def full_value_from_object(self, obj, ar=None):
        return self.field.value_from_object(obj)

    def value2list(self, ar, v, l, row):
        return l.append(v)

    def value2dict(self, ar, k, v, d, row):
        d[k] = v

    # def value2odt(self,ar,v,tc,**params):
    # """
    # Add the necessary :term:`odfpy` element(s) to the containing element `tc`.
    # """
    # params.update(text=force_str(v))
    # tc.addElement(odf.text.P(**params))

    def parse_form_value(self, v, obj, ar=None):
        # if v == '' and not self.field.empty_strings_allowed:
        #     return None
        return self.field.to_python(v)

    def extract_form_data(self, obj, post_data, ar=None):
        # logger.info("20130128 StoreField.extract_form_data %s",self.name)
        return post_data.get(self.name, None)

    def form2obj(self, ar, instance, post_data, is_new):
        """Test cases:

        - setting a CharField to '' will store either '' or None,
          depending on whether the field is nullable or not.
        - trading.Invoice.number may be blank
        - setting a Person.city to blank must not create a new Place "Select a Place..."

        """
        v = self.extract_form_data(instance, post_data, ar)
        # if self.name in 'nationality city':
        #     logger.info("20210213 %s.form2obj() %s = %r from %s",
        #                 self.__class__.__name__, self.name, v, post_data)
        if v is None:
            # means that the field wasn't part of the submitted form. don't
            # touch it.
            return
        if v == "":
            # print(20160611, self.field.empty_strings_allowed,
            #       self.field.name, self.form2obj_default)
            if not isinstance(self.field, (models.Field, fields.FakeField)):
                v = None  # e.g. GenericForeignKey
            elif self.field.null:
                v = None
            elif self.field.empty_strings_allowed:
                v = self.parse_form_value(v, instance, ar)

                # If a field has been posted with empty string, we
                # don't want it to get the field's default value!
                # Otherwise checkboxes with default value True can
                # never be unset!

                # Charfields have empty_strings_allowed (e.g. id field
                # may be empty), but don't do this for other cases.
            else:
                v = self.form2obj_default
            # print("20160611 {0} = {1}".format(self.field.name, v))
        else:
            v = self.parse_form_value(v, instance, ar)
        # logger.info("20180712 %s %s", self, v)
        if not is_new and self.field.primary_key and instance.pk is not None:
            if instance.pk == v:
                return
            raise exceptions.ValidationError(
                {
                    self.field.name: _(
                        "Existing primary key value %r " "may not be modified."
                    )
                    % instance.pk
                }
            )

        return self.set_value_in_object(ar, instance, v)

    def set_value_in_object(self, ar, instance, v):
        # logger.info("20180712 super set_value_in_object() %s", v)
        old_value = self.value_from_object(instance, ar.request)
        # old_value = getattr(instance,self.field.attname)
        if old_value != v:
            setattr(instance, self.name, v)
            return True

    @classmethod
    def register_for_field(cls, dftype, elemtype):
        if dftype in FIELD_TYPES:
            raise Exception(f"Duplicate field type {dftype}")
        FIELD_TYPES[dftype] = cls
        from lino.core.elems import _FIELD2ELEM
        _FIELD2ELEM.append((dftype, elemtype))

    def format_value(self, ar, v):
        """
        Return a plain textual representation as a unicode string
        of the given value `v`.   Note that `v` might be `None`.
        """
        return force_str(v)


class RelatedMixin(object):
    """
    Common methods for :class:`ForeignKeyStoreField` and
    :class:`OneToOneStoreField`.
    """

    def get_rel_to(self, obj):
        # if self.field.rel is None:
        # return None
        return self.field.remote_field.model

    def full_value_from_object(self, obj, ar=None):
        # here we don't want the pk (stored in field's attname)
        # but the full object this field refers to
        relto_model = self.get_rel_to(obj)
        if not relto_model:
            # logger.warning("%s get_rel_to returned None",self.field)
            return None
        try:
            return getattr(obj, self.name)
        except relto_model.DoesNotExist:
            return None

    def format_value(self, ar, v):
        if ar is None:
            return v.get_choices_text(None, None, self.field)
        return v.get_choices_text(ar, ar.actor, self.field)


class ComboStoreField(StoreField):
    """
    An atomizer for all kinds of fields which use a ComboBox.
    """

    list_values_count = 2

    def as_js(self, name):
        s = StoreField.as_js(self, name)
        # s += "," + repr(self.field.name+constants.CHOICES_HIDDEN_SUFFIX)
        s += ", '%s'" % (name + constants.CHOICES_HIDDEN_SUFFIX)
        return s

    def column_names(self):
        # yield self.options['name']
        # yield self.options['name'] + constants.CHOICES_HIDDEN_SUFFIX
        yield self.name
        yield self.name + constants.CHOICES_HIDDEN_SUFFIX

    def extract_form_data(self, obj, post_data, ar=None):
        return post_data.get(self.name + constants.CHOICES_HIDDEN_SUFFIX, None)

    # def obj2list(self,request,obj):
    def value2list(self, ar, v, l, row):
        value, text = self.get_value_text(ar, v, row)
        l += [text, value]

    # def obj2dict(self,request,obj,d):
    def value2dict(self, ar, k, v, d, row):
        value, text = self.get_value_text(ar, v, row)
        d[k] = text
        d[k + constants.CHOICES_HIDDEN_SUFFIX] = value

    def get_value_text(self, ar, v, obj):
        # v = self.full_value_from_object(None,obj)
        if v is None or v == "":
            return (None, None)
        # print("20250518", obj, obj.__class__, ar.actor, self.field.name)
        if obj is not None:
            # ch = obj.__class__.get_chooser_for_field(self.field.name)
            # if ch is not None:
            #     return (v, ch.get_text_for_value(v, obj))
            ch = ar.actor.get_chooser_for_field(self.field.name)
            if ch is not None:
                return (v, ch.get_text_for_value(v, obj))
        for i in self.field.choices:
            if i[0] == v:
                # return (v, i[1].encode('utf8'))
                return (getattr(v, "value", v), i[1])
        return (v, _("%r (invalid choice)") % v)


class ForeignKeyStoreField(RelatedMixin, ComboStoreField):
    """An atomizer used for all ForeignKey fields."""

    # def cell_html(self,req,row):
    # obj = self.full_value_from_object(req,row)
    # if obj is None:
    # return ''
    # return req.ui.obj2html(obj)

    def get_value_text(self, ar, v, obj):
        # v = self.full_value_from_object(None,obj)
        # if isinstance(v,basestring):
        # logger.info("20120109 %s -> %s -> %r",obj,self,v)
        if v is None:
            return (None, None)
        elif v == constants.CHOICES_BLANK_FILTER_VALUE:
            return (v, _("Blank"))
        elif v == constants.CHOICES_NOT_BLANK_FILTER_VALUE:
            return (v, _("Not Blank"))
        else:
            return (v.pk, self.format_value(ar, v))
            # return (v.pk, str(v))

    def extract_form_data(self, obj, post_data, ar=None):
        # logger.info("20130128 ComboStoreField.extract_form_data %s",self.name)
        pk = post_data.get(self.name + constants.CHOICES_HIDDEN_SUFFIX, None)
        if pk is None:
            # for FK fields the fooHidden must be provided by
            # the form, otherwise we consider the field as not included in the form.
            # This is not an error because not all forms submit all fields.
            # logger.info("20210214 incomplete form data for %s", self)
            # raise Exception("20210214 incomplete form data for %s" % self)
            return

        if not pk:
            return ""
            # return an empty string because None would mean to not touch the
            # field. Field.blank and Field.none are handled later.

        relto_model = self.get_rel_to(obj)
        if not relto_model:
            raise Warning(
                "extract_form_data found no relto_model for %s" % self)
            # logger.info("20111209 get_value_text: no relto_model")
            # return

        # print("20200901 parse_form_value", v, obj)
        try:
            return relto_model.objects.get(pk=pk)
        except (ValueError, relto_model.DoesNotExist):
            # For learning comboboxes, extjs sets fooHidden to contain the
            # text that did not find a matching pk.

            if obj is not None:
                ch = obj.__class__.get_chooser_for_field(self.field.name)
                if ch and ch.can_create_choice:
                    # print("20200901 can_create_choice", obj, v)
                    return ch.create_choice(obj, pk, ar)

        raise Warning("Got invalid non-empty pk {} for {}".format(pk, self))

    def parse_form_value(self, v, obj, ar=None):
        """Convert the form field value (expected to contain a primary key)
        into the corresponding database object. If it is an invalid
        primary key, return None.

        If this comes from a *learning* ComboBox
        (i.e. :attr:`can_create_choice
        <lino.core.choosers.Chooser.can_create_choice>` is True) the
        value will be the text entered by the user. In that case, call
        :meth:`create_choice
        <lino.core.choosers.Chooser.create_choice>`.

        """
        if not isinstance(v, str):
            return v
        relto_model = self.get_rel_to(obj)
        if not relto_model:
            # logger.info("20111209 get_value_text: no relto_model")
            return

        # print("20200901 parse_form_value", v, obj)
        try:
            return relto_model.objects.get(pk=v)
        except ValueError:
            pass
        except relto_model.DoesNotExist:
            pass

        if obj is not None:
            ch = obj.__class__.get_chooser_for_field(self.field.name)
            if ch and ch.can_create_choice:
                # print("20200901 can_create_choice", obj, v)
                return ch.create_choice(obj, v, ar)
        return None


# class OneToOneStoreField(ForeignKeyStoreField):
#     pass


class OneToOneStoreField(RelatedMixin, StoreField):
    def value_from_object(self, obj, ar=None):
        v = self.full_value_from_object(obj, ar)
        if v is None:
            return ""
        if ar is None:
            return str(v)
        return v.as_summary_item(ar)


class PreviewTextStoreField(StoreField):
    list_values_count = 3

    def column_names(self):
        yield self.name
        yield self.name + "_short_preview"
        yield self.name + "_full_preview"

    def value2list(self, ar, v, l, row):
        if ar.renderer.front_end.media_name.startswith("ext"):
            super().value2list(ar, v, l, row)
        else:
            if isinstance(row, PhantomRow):
                l.extend([None for _ in range(self.list_values_count)])
            else:
                l.extend([getattr(row, name) for name in self.column_names()])

    def value2dict(self, ar, k, v, d, row):
        if not isinstance(row, PhantomRow):
            for name in self.column_names():
                d[name] = getattr(row, name)

# class LinkedForeignKeyField(ForeignKeyStoreField):

# def get_rel_to(self,obj):
# ct = self.field.get_content_type(obj)
# if ct is None:
# return None
# return ct.model_class()


class VirtStoreField(StoreField):
    def __init__(self, vf, delegate, name):
        self.vf = vf
        super().__init__(vf.return_type, name)
        self.as_js = delegate.as_js
        self.column_names = delegate.column_names
        self.list_values_count = delegate.list_values_count
        self.form2obj_default = delegate.form2obj_default
        # 20130130 self.value2num = delegate.value2num
        # 20130130 self.value2html = delegate.value2html
        self.value2list = delegate.value2list
        self.value2dict = delegate.value2dict  # 20210516
        self.format_value = delegate.format_value
        self.extract_form_data = delegate.extract_form_data
        # 20130130 self.format_sum = delegate.format_sum
        # 20130130 self.sum2html = delegate.sum2html
        # self.form2obj = delegate.form2obj
        # as long as http://code.djangoproject.com/ticket/15497 is open:
        self.parse_form_value = delegate.parse_form_value
        self.set_value_in_object = vf.set_value_in_object
        # 20130130 self.apply_cell_format = delegate.apply_cell_format
        # self.value_from_object = vf.value_from_object

        self.delegate = delegate

    def __repr__(self):
        return "(virtual){} '{}'".format(self.delegate.__class__.__name__, self.name)

    def full_value_from_object(self, obj, ar=None):
        # 20150218 : added new rule that virtual fields are never
        # computed for unsaved instances. This is because
        # `ShowInsert.get_status` otherwise generated lots of useless
        # slave summaries which furthermore caused an endless
        # recursion problem. See test case in
        # :ref:`welfare.tested.pcsw`. Note that `obj` does not need to
        # be a database object. See
        # e.g. :doc:`/tutorials/vtables/index`.
        if ar is not None and ar.bound_action.action.hide_virtual_fields:
            # if isinstance(obj, models.Model) and not obj.pk:
            return None
        return self.vf.value_from_object(obj, ar)

    # 20210516
    # def value2dict(self, ar, v, d, row):
    #     d[self.name] = v
    # def value2dict(self, ar, v, d, row):
    #     d2 = {}
    #     self.delegate.value2dict(ar, v, d2, row)
    #     for k, v in d2.items():
    #         d[self.name + k] = v


class RequestStoreField(StoreField):
    """
    StoreField for :class:`lino.core.fields.RequestField`.
    """

    def __init__(self, vf, delegate, name):
        self.vf = vf
        StoreField.__init__(self, vf.return_type, name)
        # self.editable = False
        self.as_js = delegate.as_js
        self.column_names = delegate.column_names
        self.list_values_count = delegate.list_values_count

    def full_value_from_object(self, obj, ar=None):
        return self.vf.value_from_object(obj, ar)

    def value2list(self, ar, v, l, row):
        return l.append(self.format_value(ar, v))

    def value2dict(self, ar, k, v, d, row):
        d[k] = self.format_value(ar, v)
        # d[self.options['name']] = self.format_value(ui,v)
        # d[self.field.name] = v

    def format_value(self, ar, v):
        if v is None:
            return ""
        return str(v.get_total_count())

    # def sum2html(self,ar,sums,i,**cellattrs):
    # cellattrs.update(align="right")
    # return super(RequestStoreField,self).sum2html(ar,sums,i,**cellattrs)

    # def value2odt(self,ar,v,tc,**params):
    # params.update(text=self.format_value(ar,v))
    # tc.addElement(odf.text.P(**params))


class PasswordStoreField(StoreField):
    def value_from_object(self, obj, request=None):
        v = super().value_from_object(obj, request)
        if v:
            return "*" * len(v)
        return v


class SpecialStoreField(StoreField):
    field = None
    name = None
    editable = False

    def __init__(self, store):
        self.options = dict(name=self.name)
        self.store = store

    def parse_form_value(self, v, instance, ar=None):
        pass

    def form2obj(self, ar, instance, post_data, is_new):
        pass
        # raise NotImplementedError
        # return instance


class DisabledFieldsStoreField(SpecialStoreField):
    """
    See also blog entries 20100803, 20111003, 20120901

    Note some special cases:

    - :attr:`lino.modlib.vat.VatDocument.total_incl` (readonly virtual
      PriceField) must be disabled and may not get submitted.  ExtJS
      requires us to set this dynamically each time.

    - JobsOverview.body (a virtual HtmlBox) or Model.workflow_buttons
      (a displayfield) must *not* have the 'disabled' css class.

    - after submitting a Lockable, the

    """

    name = "disabled_fields"

    def __init__(self, store):
        # from lino.core.gfks import GenericForeignKey
        super().__init__(store)
        self.always_disabled = set()
        for f in self.store.all_fields:
            if f.field is not None:
                if isinstance(f, VirtStoreField):
                    if not f.vf.editable:
                        if not isinstance(f.vf.return_type, fields.DisplayField):
                            self.always_disabled.add(f.name)
                            # print "20121010 always disabled:", f
                elif not isinstance(f.field, GenericForeignKey):
                    if not f.field.editable:
                        self.always_disabled.add(f.name)

    def full_value_from_object(self, obj, ar=None):
        d = dict()
        for name in self.store.actor.get_disabled_fields(obj, ar):
            if name is not None:
                d[str(name)] = True

        for name in self.always_disabled:
            d[str(name)] = True

        # disable the primary key field of a saved instance. Note that
        # pk might be set also on an unsaved instance and that

        if (
            ar
            and ar.bound_action.action.disable_primary_key
            and self.store.pk is not None
        ):
            for pk in self.store.primary_keys:
                d[str(pk.attname)] = True
            # if self.store.pk.attname is None:
            #     raise Exception('20130322b')
            # d[self.store.pk.attname] = True
            # # MTI children have an additional "primary key" for every
            # # parent:
            # pk = self.store.pk
            # while isinstance(pk, models.OneToOneField):
            #     if pk.rel.field_name is None:
            #         raise Exception('20130322c')
            #     d[pk.rel.field_name] = True
            #     pk = None
        return d


# no longer used since 20170909
# class DisabledActionsStoreField(SpecialStoreField):

#     """
#     """
#     name = str('disabled_actions')

#     def full_value_from_object(self, obj, ar):
#         return self.store.actor.disabled_actions(ar, obj)

# class RecnoStoreField(SpecialStoreField):
# name = 'recno'
# def full_value_from_object(self,request,obj):
# return


class RowClassStoreField(SpecialStoreField):
    name = "row_class"

    def full_value_from_object(self, obj, ar=None):
        lst = [
                ar.renderer.row_classes_map.get(s, s)
                for s in self.store.actor.get_row_classes(obj, ar)
            ]
        # print(f"20250509x {obj} -> {lst}")
        return " ".join(lst)


class DisableEditingStoreField(SpecialStoreField):
    """
    A field whose value is the result of the `get_row_permission`
    method on that row.
    New feature since `/blog/2011/0830`
    """

    name = "disable_editing"

    def full_value_from_object(self, obj, ar=None):
        # import pdb; pdb.set_trace()
        actor = self.store.actor
        if ar is None:
            return True
        # if actor.update_action is None:
        if actor.hide_editing(ar.get_user().user_type):
            # print 20120601, self.store.actor, "update_action is None"
            return True  # disable editing if there's no update_action
        v = actor.get_row_permission(
            obj, ar, actor.get_row_state(obj), actor.update_action
        )
        # if str(actor).endswith('.RegisterNewUser'):
        #     logger.info("20161216 store.py %s %s value=%s",
        #                 actor, actor.update_action, v)
        return not v


class BooleanStoreField(StoreField):
    """A :class:`StoreField` for
    `BooleanField <https://docs.djangoproject.com/en/5.2/ref/models/fields/#booleanfield>`__.

    """

    form2obj_default = False  # 'off'

    def __init__(self, field, name, **kw):
        kw["type"] = "boolean"
        StoreField.__init__(self, field, name, **kw)
        if not field.editable:

            def full_value_from_object(self, obj, ar=None):
                # return self.value2html(ar,self.field.value_from_object(obj))
                return self.format_value(ar, self.field.value_from_object(obj))

            self.full_value_from_object = curry(full_value_from_object, self)

    def parse_form_value(self, v, obj, ar=None):
        """
        Ext.ensible CalendarPanel sends boolean values as
        """
        return constants.parse_boolean(v)

    def format_value(self, ar, v):
        return force_str(iif(v, _("Yes"), _("No")))


# class SlaveTableStoreField(StoreField):
#     def full_value_from_object(self, obj, ar=None):
#         return DelayedValue(self.field, str(self.field), obj)


class DisplayStoreField(StoreField):
    pass


class GenericForeignKeyField(DisplayStoreField):
    def full_value_from_object(self, obj, ar=None):
        v = getattr(obj, self.name, None)
        # logger.info("20130611 full_value_from_object() %s",v)
        if v is None:
            return ""
        if ar is None:
            return str(v)
        if getattr(ar, "renderer", None) is None:
            return str(v)
        return ar.obj2html(v)

    def parse_form_value(self, v, obj, ar=None):
        v = getattr(obj, self.name, None)
        return v


class GenericRelField(RelatedMixin, DisplayStoreField):
    def full_value_from_object(self, obj, ar=None):
        v = getattr(obj, self.name, None)
        if v is None:
            return None
        return v.first()
        # v = v(manager='objects')
        # raise Exception("20191126 full_value_from_object(%s, %s) --> %s" % (obj, self.name, v))
        # return v(manager='objects').first()
        # return v
        # return v.first()
        # raise Exception("20191126 full_value_from_object(%s, %s) --> %s" % (obj, self.name, v))
        # return v.get_user_queryset().first()
        # raise Exception("20191126 full_value_from_object() %s" % v.instance)
        # return v.instance
        # if v is None:
        #     return ''
        # if ar is None:
        #     return str(v)
        # if ar.renderer is None:
        #     return str(v)
        # return ar.obj2html(v)


class DecimalStoreField(StoreField):
    # def __init__(self,field,name,**kw):
    # kw['type'] = 'float'
    # StoreField.__init__(self,field,name,**kw)

    def parse_form_value(self, v, obj, ar=None):
        return parse_decimal(v)

    # def value2num(self,v):
    # ~ # print "20120426 %s value2num(%s)" % (self,v)
    # return v

    def format_value(self, ar, v):
        if not v:
            return ""
        return settings.SITE.decfmt(v, places=self.field.decimal_places)

    # def value2html(self,ar,v,**cellattrs):
    # cellattrs.update(align="right")
    # return E.td(self.format_value(ar,v),**cellattrs)


class IntegerStoreField(StoreField):
    def __init__(self, field, name, **kw):
        kw["type"] = "int"
        kw["useNull"] = True
        StoreField.__init__(self, field, name, **kw)


class AutoStoreField(StoreField):
    """A :class:`StoreField` for
    `AutoField <https://docs.djangoproject.com/en/5.2/ref/models/fields/#autofield>`__

    """

    def __init__(self, field, name, **kw):
        kw["type"] = "int"
        StoreField.__init__(self, field, name, **kw)

    def form2obj(self, ar, obj, post_data, is_new):
        # logger.info("20121022 AutoStoreField.form2obj(%r)",ar.bound_action.full_name())
        if isinstance(ar.bound_action.action, actions.ShowInsert):
            return super(AutoStoreField, self).form2obj(ar, obj, post_data, is_new)


class DateStoreField(StoreField):
    def __init__(self, field, name, **kw):
        kw["type"] = "date"
        # date_format # 'Y-m-d'
        kw["dateFormat"] = settings.SITE.date_format_extjs
        StoreField.__init__(self, field, name, **kw)

    def parse_form_value(self, v, obj, ar=None):
        if v:
            try:
                return datetime.date(*settings.SITE.parse_date(v))
            except Exception as e:
                # The front end is responsible for validating before submitting.
                # Here it's too late to complain.
                return None
                # raise Warning("Invalid date '{}'' : {}".format(v, e))

    def format_value(self, ar, v):
        """Return a plain textual representation of this value as a unicode
        string.

        """
        return fds(v)


class IncompleteDateStoreField(StoreField):
    def parse_form_value(self, v, obj, ar=None):
        if v:
            v = IncompleteDate(*settings.SITE.parse_date(v))
            # v = datetime.date(*settings.SITE.parse_date(v))
        return v


class DateTimeStoreField(StoreField):
    def parse_form_value(self, v, obj, ar=None):
        if v:
            return settings.SITE.parse_datetime(v)
        return None


class TimeStoreField(StoreField):
    def parse_form_value(self, v, obj, ar=None):
        if v:
            return settings.SITE.parse_time(v)
        return None


class FileFieldStoreField(StoreField):
    def full_value_from_object(self, obj, ar=None):
        ff = self.field.value_from_object(obj)
        return ff.name


class MethodStoreField(StoreField):
    """
    Still used for DISPLAY_MODE_HTML and writable virtual fields.
    """

    def full_value_from_object(self, obj, ar=None):
        unbound_meth = self.field._return_type_for_method
        assert unbound_meth.__code__.co_argcount >= 2, (
            self.name,
            unbound_meth.__code__.co_varnames,
        )
        # print(f"20241003 {self.field.name} {ar} full_value_from_object()")
        return unbound_meth(obj, ar)

    def value_from_object(self, obj, request=None):
        unbound_meth = self.field._return_type_for_method
        assert unbound_meth.__code__.co_argcount >= 2, (
            self.name,
            unbound_meth.__code__.co_varnames,
        )
        # print(f"20241003 {self.field.name} value_from_object()")
        return unbound_meth(obj, request)

    # def obj2list(self,request,obj):
    # return [self.value_from_object(request,obj)]

    # def obj2dict(self,request,obj,d):
    #  logger.debug('MethodStoreField.obj2dict() %s',self.field.name)
    # d[self.field.name] = self.value_from_object(request,obj)

    # def get_from_form(self,instance,post_data):
    # pass

    def form2obj(self, request, instance, post_data, is_new):
        # print("20250726", self, post_data)
        pass
        # return instance
        # raise Exception("Cannot update a virtual field")


# class ComputedColumnField(StoreField):

# def value_from_object(self,ar,obj):
# m = self.field.func
# ~ # assert m.func_code.co_argcount >= 2, (self.field.name, m.func_code.co_varnames)
# ~ # print self.field.name
# return m(obj,ar)[0]

# def form2obj(self,request,instance,post_data,is_new):
# pass

# class SlaveSummaryField(MethodStoreField):
# def obj2dict(self,request,obj,d):
# meth = getattr(obj,self.field.name)
# ~ #logger.debug('MethodStoreField.obj2dict() %s',self.field.name)
# d[self.field.name] = self.slave_report.()


# class OneToOneRelStoreField(RelatedMixin, StoreField):
class OneToOneRelStoreField(StoreField):
    def full_value_from_object(self, obj, ar=None):
        try:
            return getattr(obj, self.field.name)
        except self.field.remote_field.model.DoesNotExist:
            return None


class BaseStore(object):
    pass


class ParameterStore(BaseStore):
    # Lazily instantiated in `lino.core.layouts`
    def __init__(self, params_layout_handle, url_param):
        param_fields = []

        holder = params_layout_handle.layout.get_chooser_holder()
        # print(f"20250121e {holder}")
        # debug = False
        for pf in params_layout_handle._data_elems:
            sf = atomizer.create_atomizer(holder, pf, pf.name)
            if sf is not None:
                # if "__" in pf.name:
                #     print("20200423 ParameterStore", pf.name, sf)
                #     debug  = True
                param_fields.append(sf)

        # if debug:
        #     print("20200423 ParameterStore2", self.param_fields)

        self.param_fields = tuple(param_fields)
        self.url_param = url_param
        self.params_layout_handle = params_layout_handle

    def __str__(self):
        return "%s of %s" % (self.__class__.__name__, self.params_layout_handle)

    def pv2dict(self, ar, pv, **d):
        # debug = False
        for fld in self.param_fields:
            #     debug = True
            if fld.delayed_value and len(ar.selected_rows) == 1:
                v = DelayedValue(ar, fld.name, ar.selected_rows[0])
            else:
                v = pv.get(fld.name, None)
            # if "__" in fld.name:
            #     print("20200430", fld, v)
            fld.value2dict(ar, fld.name, v, d, None)
            # try:
            #     v = pv.get(fld.name, None)
            #     fld.value2dict(ar, v, d, None)
            # except Exception as e:
            #     raise e.__class__("{} : {}".format(fld, e))
        # if debug:
        #     print("20200423", d)
        return d

    def pv2list(self, ar, apv):  # new since 20140930
        l = []
        for fld in self.param_fields:
            v = apv.get(fld.name, None)
            l.append(v)
        return l

    def parse_params(self, request, **kw):
        data = getrqdata(request)
        # print(20160329, data)
        # assert 'pv' in data
        pv = data.getlist(self.url_param)  # 'fv', 'pv', post[fn] post[fv][fn]

        # logger.info("20120221 ParameterStore.parse_params(%s) --> %s",self.url_param,pv)

        def parse(sf, form_value):
            if form_value == "" and not sf.field.empty_strings_allowed:
                return sf.form2obj_default
                # When a field has been posted with empty string, we
                # don't want it to get the field's default value
                # because otherwise checkboxes with default value True
                # can never be unset.  charfields have
                # empty_strings_allowed e.g. id field may be empty.
                # But don't do this for other cases.
            elif form_value in (
                constants.CHOICES_BLANK_FILTER_VALUE,
                constants.CHOICES_NOT_BLANK_FILTER_VALUE,
            ):
                return form_value
            else:
                return sf.parse_form_value(form_value, None)

        if len(pv) > 0:
            if len(self.param_fields) != len(pv):
                raise Exception(
                    "%s expects a list of %d values but got %d: %s"
                    % (self, len(self.param_fields), len(pv), pv)
                )
            for i, f in enumerate(self.param_fields):
                # kw[f.field.name] = parse(f, pv[i])
                kw[f.name] = parse(
                    f, pv[i]
                )  # 20200423 support remote fields in parameters
        elif self.url_param == "fv":
            # try to get data from dict style in main body of request
            for i, f in enumerate(self.param_fields):
                if f.name + "Hidden" in data:
                    kw[f.name] = parse(f, data[f.name + "Hidden"])
                elif f.name in data:
                    kw[f.name] = parse(f, data[f.name])
        # print(20160329, kw)
        return kw


class Store(BaseStore):
    """
    A Store is the collection of StoreFields for a given actor.
    Instantiated in kernel
    """

    pk = None
    _disabled_fields_storefield = None

    def __init__(self, rh, **options):
        self.rh = rh
        self.actor = rh.actor
        # temporary dict used by collect_fields and add_field_for
        # self.df2sf = {}
        self.all_fields = []
        self.grid_fields = []
        self.detail_fields = []
        self.card_fields = []
        self.item_fields = []
        self.primary_keys = set([])

    def init_store(self):

        rh = self.rh

        def addfield(sf):
            if not isinstance(sf, StoreField):
                raise Exception("20210623 {} is not a StoreField".format(sf))
            self.all_fields.append(sf)
            self.grid_fields.append(sf)
            self.detail_fields.append(sf)

        if not issubclass(rh.actor, frames.Frame):
            self.collect_fields(self.grid_fields, rh.get_grid_layout())

        form = rh.actor.detail_layout
        if form:
            dh = form.get_layout_handle()
            self.collect_fields(self.detail_fields, dh)

        for form in rh.actor.extra_layouts.values():
            dh = form.get_layout_handle()
            self.collect_fields(self.detail_fields, dh)

        form = rh.actor.insert_layout
        if form:
            if isinstance(form, str):
                raise Exception(f"20250306 insert_layout {repr(rh.actor)} is a str!")
            dh = form.get_layout_handle()
            self.collect_fields(self.detail_fields, dh)

        form = rh.actor.card_layout
        if form:
            dh = form.get_layout_handle()
            self.collect_fields(self.card_fields, dh)

        # form = rh.actor.list_layout
        # if form:
        #     dh = form.get_layout_handle()
        #     self.collect_fields(self.item_fields, dh)

        if self.pk is not None:
            self.pk_index = 0
            found = False
            for fld in self.grid_fields:
                """
                Django's Field.__cmp__() does::

                  return cmp(self.creation_counter, other.creation_counter)

                which causes an exception when trying to compare a field
                with an object of other type.
                """
                if (fld.field.__class__ is self.pk.__class__) and fld.field == self.pk:
                    # self.pk = fld.field
                    found = True
                    break
                self.pk_index += fld.list_values_count
            if not found:
                raise Exception(
                    "Primary key %r not found in grid_fields %s"
                    % (self.pk, [f.field for f in self.grid_fields])
                )

        actor_editable = True  # not rh.actor.hide_editing(None)
        if actor_editable:
            self._disabled_fields_storefield = DisabledFieldsStoreField(self)
            addfield(self._disabled_fields_storefield)
            # NB what about disabled actions on non-editable actor?

        if actor_editable:
            addfield(DisableEditingStoreField(self))

        if rh.actor.get_row_classes is not None:
            addfield(RowClassStoreField(self))

        # virtual fields must come last so that Store.form2obj()
        # processes "real" fields first.
        self.all_fields = [
            f for f in self.all_fields if not isinstance(f, VirtStoreField)
        ] + [f for f in self.all_fields if isinstance(f, VirtStoreField)]
        self.all_fields = tuple(self.all_fields)
        self.grid_fields = tuple(self.grid_fields)
        self.detail_fields = tuple(self.detail_fields)
        self.card_fields = tuple(self.card_fields)
        self.item_fields = tuple(self.item_fields)

    def collect_fields(self, fields, *layouts):
        """`fields` is a pointer to either `self.detail_fields` or
        `self.grid_fields`.  Each of these must contain a primary key
        field.

        """
        pk_found = False
        for layout in layouts:
            for df in layout._data_elems:
                assert df is not None
                self.add_field_for(fields, df)
                if df.primary_key:
                    self.primary_keys.add(df)
                    pk_found = True
                    if self.pk is None:
                        self.pk = df

        if self.pk is None:
            self.pk = self.actor.get_pk_field()
        if self.pk is not None:
            if not pk_found:
                self.add_field_for(fields, self.pk)

    def add_field_for(self, field_list, df):
        sf = atomizer.get_atomizer(self.actor, df, df.name)
        # if df.name == 'humanlinks_LinksByHuman':
        #     raise Exception("20181023 {} ({}) {}".format(
        #         self, df, sf))
        if sf is None:
            if isinstance(df, fields.DummyField):
                return
            return
            # raise Exception("20181023 No atomizer for {} in {}".format(
            #     repr(df), self.actor))
        if not isinstance(sf, StoreField):
            raise Exception("20210623 {} is not a StoreField".format(sf))
        # if not self.rh.actor.editable and isinstance(sf, ForeignKeyStoreField):
        #     sf = StoreField(df, df.name)
        #     raise Exception(20160907)
        if sf not in self.all_fields:
            self.all_fields.append(sf)

        # sf = self.df2sf.get(df,None)
        # if sf is None:
        # sf = self.create_atomizer(df,df.name)
        # self.all_fields.append(sf)
        # self.df2sf[df] = sf
        field_list.append(sf)

    def form2obj(self, ar, form_values, instance, is_new):
        """
        Store the `form_values` into the `instance` by calling
        :meth:`form2obj` for every store field.
        """
        disabled_fields = set(self.actor.get_disabled_fields(instance, ar))
        # logger.info("20210213 form2obj %s %s", disabled_fields, [f.name for f in self.all_fields])
        changed_triggers = []
        for f in self.all_fields:
            if f.name not in disabled_fields:
                try:
                    if f.form2obj(ar, instance, form_values, is_new):
                        # Check whether FOO_changed exists
                        m = getattr(instance, f.name + "_changed", None)
                        if m is not None:
                            changed_triggers.append(m)
                except exceptions.ValidationError as e:
                    # logger.warning("20150127 store (field %s) : %s",
                    #                f.name, e)
                    raise exceptions.ValidationError({f.name: e.messages})
                # except ValueError as e:
                #     # logger.warning("20150127 store (field %s) : %s",
                #     #                f.name, e)
                #     raise exceptions.ValidationError(
                #         {f.name: _("Invalid value for this field (%s).") % e})
                except Exception as e:
                    # Example: submit "31.02.2024" in a date field
                    if False:
                        logger.warning(
                            "Exception during Store.form2obj (field %s) : %s", f.name, e
                        )
                        logger.exception(e)
                    raise exceptions.ValidationError(
                        # {f.name: _("Invalid value (%s).") % e})
                        {f.name: str(e)}
                    )
                # logger.info("20120228 Store.form2obj %s -> %s",
                # f, dd.obj2str(instance))
        for m in changed_triggers:
            m(ar)

    def column_names(self):
        l = []
        for fld in self.grid_fields:
            l += fld.column_names()
        return l

    def column_index(self, name):
        """
        Used to set `disabled_actions_index`.
        Was used to write definition of Ext.ensible.cal.CalendarMappings
        and Ext.ensible.cal.EventMappings
        """
        # logger.info("20111214 column_names: %s",list(self.column_names()))
        return list(self.column_names()).index(name)

    def row2list(self, ar, row):
        # assert isinstance(ar, dbtables.AbstractTableRequest)
        # if not isinstance(ar, dbtables.ListActionRequest):
        # raise Exception()
        # logger.info("20120107 Store %s row2list(%s)", self.report.model, dd.obj2str(row))
        l = []
        if isinstance(row, PhantomRow):
            for fld in self.grid_fields:
                fld.value2list(ar, None, l, row)
            # instead of calling ar.scrap_row_meta, add independently the meta item
            l.append({'meta': True, 'phantom': True})
        else:
            for fld in self.grid_fields:
                if fld.delayed_value:
                    # self.actor.collect_extra_fields(fld)
                    v = DelayedValue(ar, fld.name, row)
                else:
                    v = fld.full_value_from_object(row, ar)
                fld.value2list(ar, v, l, row)

            ar.scrap_row_meta(row, l)
        # logger.info("20130611 Store row2list() --> %r", l)
        return l

    def row2dict(self, ar, row, fields=None, **d):
        # assert isinstance(ar,dbtables.AbstractTableRequest)
        # logger.info("20111209 Store.row2dict(%s)", dd.obj2str(row))
        if fields is None:
            fields = self.detail_fields
        for fld in fields:
            if fld is None:
                continue
            # logger.info("20241003 Store.row2dict %s", fld)
            if fld.delayed_value:
                # self.actor.collect_extra_fields(fld)
                v = DelayedValue(ar, fld.name, row)
            else:
                v = fld.full_value_from_object(row, ar)
            fld.value2dict(ar, fld.name, v, d, row)
            # logger.info("20140429 Store.row2dict %s -> %s", fld, v)
        #     if "households_" in fld.name:
        #         print("20181023 {}".format(fld))
        # print("20181023 row2dict {}".format(fields))
        return d

    # def file2url(self, ar, row):
    #     return settings.SITE.build_media_url(row.file.name)

    # def row2odt(self,request,fields,row,sums):
    # for i,fld in enumerate(fields):
    # if fld.field is not None:
    # v = fld.full_value_from_object(request,row)
    # if v is None:
    # yield ''
    # else:
    # sums[i] += fld.value2num(v)
    # yield fld.value2odt(request,v)
