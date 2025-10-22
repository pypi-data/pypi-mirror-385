# -*- coding: UTF-8 -*-
# Copyright 2009-2024 Rumma & Ko Ltd
# License: GNU Affero General Public License v3 (see file COPYING for details)
"""
Defines the model mixins :class:`Sequenced` and :class:`Hierarchical`.

A `Sequenced` is something which has a sequence number and thus a sort
order which can be manipulated by the :term:`end user` using actions
:class:`MoveUp` and :class:`MoveDown`.

:class:`Hierarchical` is a :class:`Sequenced` with a `parent` field.

"""

from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError

from lino.core import actions
from lino.core import fields
from lino.core.inject import update_field
from lino.core.utils import navinfo
from lino.utils.html import E
from lino.utils import AttrDict
from lino.utils import join_elems

from lino.mixins.clonable import Clonable, CloneRow


class MoveByN(actions.Action):
    """Move this row N rows upwards or downwards.

    This action is available on any :class:`Sequenced` object as
    :attr:`Sequenced.move_by_n`.

    It is currently only used by React to allow for drag and drop reordering.

    """

    # label = _("Up")
    # label = "\u2191" thin arrow up
    # label = "\u25b2" # triangular arrow up
    # label = "\u25B2"  # ▲ Black up-pointing triangle
    # label = "↑"  #
    custom_handler = True
    # icon_name = 'arrow_up'
    # ~ icon_file = 'arrow_up.png'
    readonly = False
    show_in_toolbar = False

    def get_action_permission(self, ar, obj, state):
        if ar.data_iterator is None:
            return False
        if not super().get_action_permission(ar, obj, state):
            return False
        if ar.get_total_count() == 0:
            return False
        return True

    def run_from_ui(self, ar, **kw):
        obj = ar.selected_rows[0]
        obj.seqno += int(ar.request.GET["seqno"])
        obj.seqno_changed(ar)
        # obj.full_clean()
        obj.save()
        kw = dict()
        kw.update(refresh_all=True)
        kw.update(message=_("Reordered."))
        ar.success(**kw)


class MoveUp(actions.Action):
    """Move this row one row upwards.

    This action is available on any :class:`Sequenced` object as
    :attr:`Sequenced.move_up`.

    """

    # label = _("Up")
    # label = "\u2191" thin arrow up
    # label = "\u25b2" # triangular arrow up
    label = _("Move up")
    # button_text = "\u25B2"  # ▲ Black up-pointing triangle
    button_text = "↑"
    custom_handler = True
    callable_from = "t"
    # icon_name = 'arrow_up'
    # ~ icon_file = 'arrow_up.png'
    readonly = False

    def get_action_permission(self, ar, obj, state):
        if ar.data_iterator is None:
            return False
        if not super().get_action_permission(ar, obj, state):
            return False
        # if ar.order_by is None or "seqno" not in ar.order_by:
        #     return False
        if ar.get_total_count() == 0:
            return False
        if ar.data_iterator[0] == obj:
            # print(f"20250305 first of {ar.data_iterator}")
            return False
        # print("20161128", obj.seqno, ar.data_iterator.count())
        return True

    def run_from_ui(self, ar, **kw):
        obj = ar.selected_rows[0]
        obj.seqno -= 1
        obj.seqno_changed(ar)
        # obj.full_clean()
        obj.save()
        kw = dict()
        kw.update(refresh_all=True)
        kw.update(message=_("Moved up."))
        ar.success(**kw)


class MoveDown(actions.Action):
    """Move this row one row downwards.

    This action is available on any :class:`Sequenced` object as
    :attr:`Sequenced.move_down`.

    """

    label = _("Move down")
    # label = _("Down")
    button_text = "↓"
    # label = "\u25bc" # triangular arrow down
    # label = "\u2193"
    # button_text = "\u25BC"  # ▼ Black down-pointing triangle
    # icon_name = 'arrow_down'
    custom_handler = True
    # ~ icon_file = 'arrow_down.png'
    callable_from = "t"
    readonly = False

    def get_action_permission(self, ar, obj, state):
        if ar.data_iterator is None:
            return False
        if not super().get_action_permission(ar, obj, state):
            return False
        # if ar.order_by is None or "seqno" not in ar.order_by:
        #     return False
        n = ar.get_total_count()
        if n == 0:
            return False
        if ar.data_iterator[n - 1] == obj:
            # print(f"20250305 last of {ar.data_iterator}")
            return False
        # ~ if obj.__class__.__name__=='Entry' and obj.seqno == 25:
        # ~ print 20130706, ar.data_iterator.count(), ar.data_iterator
        return True

    def run_from_ui(self, ar, **kw):
        obj = ar.selected_rows[0]
        obj.seqno += 1
        # obj.seqno = obj.seqno + 1
        obj.seqno_changed(ar)
        # obj.full_clean()
        obj.save()
        kw = dict()
        # ~ kw.update(refresh=True)
        kw.update(refresh_all=True)
        kw.update(message=_("Moved down."))
        ar.success(**kw)


class CloneSequenced(CloneRow):

    def run_from_code(self, ar, **kw):
        obj = ar.selected_rows[0]

        # ~ print '20120605 duplicate', self.seqno, self.account
        seqno = obj.seqno
        qs = obj.get_siblings().filter(seqno__gt=seqno).order_by("-seqno")
        for s in qs:
            # ~ print '20120605 duplicate inc', s.seqno, s.account
            s.seqno += 1
            s.save()
        kw.update(seqno=seqno + 1)
        return super().run_from_code(ar, **kw)


class Sequenced(Clonable):
    """Mixin for models that have a field :attr:`seqno` containing a
    "sequence number".

    .. attribute:: seqno

        The sequence number of this item with its parent.

    .. method:: clone_row

        Create a duplicate of this row and insert the new row below this one.

        Implemented by :class:`CloneSequenced`

    .. attribute:: move_up

        Exchange the :attr:`seqno` of this item and the previous item.

    .. attribute:: move_down

        Exchange the :attr:`seqno` of this item and the next item.

    .. attribute:: move_buttons

        Displays buttons for certain actions on this row:

        - :attr:`move_up` and :attr:`move_down`
        - clone_row

    .. attribute:: move_by_n

    """

    move_action_names = ("move_up", "move_down", "clone_row")
    """The names of the actions to display in the `move_buttons`
    column.

    Overridden by :class:`lino.modlib.dashboard.Widget` where the
    clone_row button would be irritating.

    """

    class Meta:
        abstract = True
        ordering = ["seqno"]

    seqno = models.IntegerField(_("No."), blank=True, null=False)

    clone_row = CloneSequenced()

    move_up = MoveUp()
    move_down = MoveDown()
    move_by_n = MoveByN()

    def __str__(self):
        return str(_("Row # %s") % self.seqno)

    def get_siblings(self):
        """Return a Django Queryset with all siblings of this, or `None` if
        this is a root element which cannot have any siblings.

        Siblings are all objects that belong to a same sequence.
        This is needed for automatic management of the `seqno` field.

        The queryset will of course include `self`.

        The default implementation uses a global sequencing by
        returning all objects of `self`'s model.

        A common case for overriding this method is when numbering
        restarts for each master.  For example if you have a master
        model `Product` and a sequenced slave model `Property` with a
        ForeignKey field `product` which points to the Product, then
        you'll define::

          class Property(dd.Sequenced):

              def get_siblings(self):
                  return Property.objects.filter(
                      product=self.product)

        Overridden e.g. in
        :class:`lino_xl.lib.thirds.models.Third`
        or
        :class:`lino_welfare.modlib.debts.models.Entry`.

        """
        return self.__class__.objects.order_by("seqno")

    def set_seqno(self):
        """
        Initialize `seqno` to the `seqno` of eldest sibling + 1.
        """
        qs = self.get_siblings().order_by("seqno")
        if (count := qs.count()) == 0:
            self.seqno = 1
        else:
            last = qs[count - 1]
            self.seqno = last.seqno + 1

    def full_clean(self, *args, **kw):
        if not self.seqno:
            self.set_seqno()
        super().full_clean(*args, **kw)

        # if hasattr(self, 'amount'):
        #     logger.info("20151117 Sequenced.full_clean a %s", self.amount)
        #     logger.info("20151117  %s", self.__class__.mro())
        # if hasattr(self, 'amount'):
        #     logger.info("20151117 Sequenced.full_clean b %s", self.amount)

    def seqno_changed(self, ar):
        """If the user manually assigns a seqno."""
        # get siblings list
        qs = self.get_siblings().order_by("seqno").exclude(id=self.id)

        # print("20170615 qs is", qs)
        # old_self = qs.get(id=self.id)
        # qs = qs.exclude(id=self.id)

        # if old_self.seqno != self.seqno:
        seq_no = 1
        n = 0

        for i in qs:
            if seq_no == self.seqno:
                seq_no += 1

            if i.seqno != seq_no:
                i.seqno = seq_no
                # if diff
                i.save()
                n += 1

            seq_no += 1

        ar.success(
            message=_("Renumbered {} of {} siblings.").format(n, qs.count()))
        ar.set_response(refresh_all=True)

    @fields.displayfield("⇵", wildcard_data_elem=True)
    def dndreorder(self, ar):
        """A place holder column for drag and drop row reorder on :term:`React front end`

        CAUTION: Do NOT rename this field, for react works on checking the name as dndreorder.
        """
        return None

    @fields.displayfield(_("Move"))
    def move_buttons(obj, ar):
        if ar is None:
            return ""
        actor = ar.actor
        l = []
        state = None  # TODO: support a possible state?
        for n in obj.move_action_names:
            ba = actor.get_action_by_name(n)
            if ba.get_row_permission(ar, obj, state):
                l.append(ar.renderer.action_button(obj, ar, ba))
                l.append(" ")
        return E.p(*l)


Sequenced.set_widget_options("move_buttons", width=5)
Sequenced.set_widget_options("seqno", hide_sum=True)


class Hierarchical(Clonable):
    """Model mixin for things that have a "parent" and "siblings".

    Pronounciation: [hai'ra:kikl]

    .. attribute:: children_summary

        A comma-separated list of the children.

    """

    class Meta(object):
        abstract = True

    parent = fields.ForeignKey(
        "self", verbose_name=_("Parent"), null=True, blank=True, related_name="children"
    )

    @fields.displayfield(_("Children"))
    def children_summary(self, ar):
        if ar is None:
            return ""
        elems = [ar.obj2html(ch) for ch in self.children.all()]
        elems = join_elems(elems, sep=", ")
        return E.p(*elems)

    def get_siblings(self):
        if self.parent:
            return self.parent.children.all()
        return self.__class__.objects.filter(parent__isnull=True)

    # ~ def save(self, *args, **kwargs):
    # ~ super(Hierarchical, self).save(*args, **kwargs)
    def full_clean(self, *args, **kwargs):
        p = self.parent
        while p is not None:
            if p == self:
                raise ValidationError("Cannot be your own ancestor")
            p = p.parent
        super().full_clean(*args, **kwargs)

    def is_parented(self, other):
        if self == other:
            return True
        p = self.parent
        while p is not None:
            if p == other:
                return True
            p = p.parent

    def get_ancestor(self):
        p = self
        while p.parent is not None:
            p = p.parent
        return p
        # return self.get_parental_line()[0]

    def get_parents(self):
        rv = []
        p = self.parent
        while p is not None:
            rv.insert(p)
            p = p.parent
        return rv

    def get_parental_line(self):
        """Return an ordered list of all ancestors of this instance.

        The last element of the list is this.
        A top-level project is its own root.

        """
        obj = self
        tree = [obj]
        while obj.parent is not None:
            obj = obj.parent
            if obj in tree:
                raise Exception("Circular parent")
            tree.insert(0, obj)
        return tree

    def whole_clan(self):
        """Return a set of this instance and all children and grandchildren."""
        # TODO: go deeper but check for circular references
        clan = set([self])
        l1 = self.__class__.objects.filter(parent=self)
        if l1.count() == 0:
            return clan
        clan |= set(l1)
        l2 = self.__class__.objects.filter(parent__in=l1)
        if l2.count() == 0:
            return clan
        clan |= set(l2)
        l3 = self.__class__.objects.filter(parent__in=l2)
        if l3.count() == 0:
            return clan
        clan |= set(l3)
        # print 20150421, projects
        return clan

    def whole_tree(self):
        """
        Returns a tuple with two items `(obj, children)` representing the whole tree.

        The first item is the top-most ancestor and the second item is a tuple
        of all the children of the ancestor.
        A child is wrappend inside another tuple where the first item is the
        child and second item is None when the child itself has no children
        otherwise the second item will be another tuple of children
        and so on.
        """
        items = []
        parent = self.get_ancestor()
        items.append(parent)
        child = parent.children.all()

        def append_to_tree(parent, child, tree):
            if child.count() == 0:
                return
            else:
                t = tree
                for c in child:
                    if c in items:
                        continue
                    items.append(c)
                    t = t + ((c, append_to_tree(c, c.children.all(), tree)),)
                return t

        return (parent, append_to_tree(parent, child, tuple()))

    @fields.htmlbox()
    def treeview_panel(self, ar):
        if ar is None:
            return None
        openned = self.get_parental_line()
        ancestor = openned[0]
        # tab = "» "
        tab = " ⸱ "  # U+2e31

        # folder_closed = "🗀 " # U+1F5C0
        folder_closed = "⌾ "  # U+233e
        # folder_open = "🗁 " # U+1F5C1
        folder_open = "⌾ "  # U+233e
        folder_with_child_closed = "📁 "  # U+1F4C1 "🗂 "
        folder_with_child_open = "📂 "  # U+1F4C2

        et = E.div()

        def append_to_et(child, i=0):
            def get_text(child):
                return (
                    (tab * i)
                    + (
                        folder_open
                        if child in openned and child.children.count() == 0
                        else folder_with_child_open
                        if child in openned
                        else folder_closed
                        if child.children.count() == 0
                        else folder_with_child_closed
                    )
                    + str(child)
                )

            et.append(ar.goto_pk(child.id, get_text(child)))
            if child.children.count() > 0:
                i += 1
                for c in child.children.all():
                    if c in openned:
                        et.append(E.br())
                        append_to_et(c, i)
                    else:
                        et.append(E.br())
                        et.append(ar.goto_pk(c.id, get_text(c)))
                i -= 1
            if child == self:
                sar = ar.actor.create_request(
                    parent=ar, master_instance=self, is_on_main_actor=False
                )
                # sar = ar.spawn_request(master_instance=self, is_on_main_actor=False)
                if ar.actor.insert_action is not None:
                    ir = ar.actor.insert_action.request_from(sar)
                    if ir.get_permission():
                        btn = ir.ar2button()
                        if len(et):
                            et.append(E.br())
                        et.append(btn)

        append_to_et(ancestor)
        return ar.html_text(et)
