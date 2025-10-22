# -*- coding: UTF-8 -*-
# Copyright 2009-2025 Rumma & Ko Ltd
# License: GNU Affero General Public License v3 (see file COPYING for details)
"""

Summary from <http://en.wikipedia.org/wiki/Restful>:

    On an element:

    - GET : Retrieve a representation of the addressed member of the collection expressed in an appropriate MIME type.
    - PUT : Update the addressed member of the collection or create it with the specified ID.
    - POST : Treats the addressed member as a collection and creates a new subordinate of it.
    - DELETE : Delete the addressed member of the collection.

    On a list:

    - GET : List the members of the collection.
    - PUT : Replace the entire collection with another collection.
    - POST : Create a new entry in the collection where the ID is assigned automatically by the collection.
      The ID created is included as part of the data returned by this operation.
    - DELETE : Delete the entire collection.

"""
import json
import os

from django import http
from django.db import models
from django.conf import settings
from django.core.cache import cache
from django.core.exceptions import PermissionDenied
from django.views.generic import View
from django.views.generic.base import TemplateView
from django.views.decorators.cache import never_cache
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import ensure_csrf_cookie, csrf_protect
from django.utils.translation import gettext as _
from django.utils.encoding import force_str
from django.utils.html import mark_safe

from lino.core.signals import pre_ui_delete
from lino.core.utils import obj2unicode

# from etgen import html as xghtml
from lino.utils.html import E, tostring, escape
from etgen.html import Document

from lino.utils import ucsv
from lino import logger
# from lino.utils import dblogger
from lino.core import constants
from lino.core import actions
from lino.core.fields import choices_for_field
from lino.core.views import requested_actor, action_request
from lino.core.views import json_response
from lino.core.views import choices_response
from lino.core.requests import BaseRequest
from lino.core.utils import is_devserver

MAX_ROW_COUNT = 300


class HttpResponseDeleted(http.HttpResponse):
    status_code = 204


def elem2rec_empty(ar, ah, elem, **rec):
    """
    Returns a dict of this record, designed for usage by an EmptyTable.
    """
    # ~ rec.update(data=rh.store.row2dict(ar,elem))
    rec.update(data=elem._data)
    # ~ rec = elem2rec1(ar,ah,elem)
    # ~ rec.update(title=_("Insert into %s...") % ar.get_title())
    rec.update(title=ar.get_action_title())
    rec.update(id=-99998)
    # ~ rec.update(id=elem.pk) or -99999)
    if ar.actor.parameters:
        rec.update(
            param_values=ar.actor.params_layout.params_store.pv2dict(
                ar, ar.param_values
            )
        )
    return rec


def delete_element(ar, elem):
    if elem is None:
        raise Warning("Cannot delete None")
    msg = ar.actor.disable_delete(elem, ar)
    if msg is not None:
        ar.error(None, msg, alert=True)
        return settings.SITE.kernel.default_renderer.render_action_response(ar)

    # ~ dblogger.log_deleted(ar.request,elem)

    # ~ changes.log_delete(ar.request,elem)

    pre_ui_delete.send(sender=elem, request=ar.request)

    try:
        elem.delete()
    except Exception as e:
        logger.exception(e)
        msg = _("Failed to delete %(record)s : %(error)s.") % dict(
            record=obj2unicode(elem), error=e
        )
        # ~ msg = "Failed to delete %s." % element_name(elem)
        ar.error(None, msg)
        return settings.SITE.kernel.default_renderer.render_action_response(ar)
        # ~ raise Http404(msg)

    return HttpResponseDeleted()


@method_decorator(never_cache, name="dispatch")
class AdminIndex(View):
    """
    Similar to PlainIndex
    """

    @method_decorator(ensure_csrf_cookie)
    def get(self, request, *args, **kw):
        # logger.info("20150427 AdminIndex.get()")
        # settings.SITE.startup()
        renderer = settings.SITE.plugins.extjs.renderer
        # if settings.SITE.user_model is not None:
        #     user = request.subst_user or request.user
        #     a = settings.SITE.get_main_action(user)
        #     if a is not None and a.get_view_permission(user.user_type):
        #         kw.update(on_ready=renderer.action_call(request, a, {}))
        # raise Exception("20230331 {}".format(request.user))
        # if request.subst_user:
        #     raise(Exception("20230331 {}".format(request.subst_user)))
        return http.HttpResponse(renderer.html_page(request, **kw))


def test_version_mismatch(request):
    if os.environ.get("PYCHARM_HOSTED", False):
        return {}
    lv = request.GET.get(constants.URL_PARAM_LINO_VERSION)
    if lv is None or float(lv) == settings.SITE.kernel.lino_version:
        return {}
    # print("20201217", lv, settings.SITE.kernel.code_mtime)
    cache.clear()
    if settings.SITE.kernel.editing_front_end.app_label == "react":
        return {"version_mismatch": True}
    return dict(
        alert=_("Version mismatch"),
        message=_(
            "Your browser is using a previous version of the site, press OK to reload the site"
        ),
        alert_eval_js="window.location.reload(true);",
    )


class MainHtml(View):
    def get(self, request, *args, **kw):
        # ~ logger.info("20130719 MainHtml")
        settings.SITE.startup()
        # ~ raise Exception("20131023")
        front_end = settings.SITE.plugins.extjs
        ar = BaseRequest(request, renderer=front_end.renderer)
        # renderer=settings.SITE.kernel.default_renderer)
        html = settings.SITE.get_main_html(ar, front_end=front_end)
        html = front_end.renderer.html_text(html)
        ar.success(html=html)
        ar.set_response(**test_version_mismatch(request))
        # return settings.SITE.kernel.default_renderer.render_action_response(ar)
        return front_end.renderer.render_action_response(ar)


class SWView(TemplateView):
    template_name = "extjs/service-worker.js"
    content_type = "application/javascript"


class RunJasmine(View):
    def get(self, request, *args, **kw):
        return http.HttpResponse(
            settings.SITE.kernel.extjs_renderer.html_page(
                request, run_jasmine=True)
        )


class EidAppletService(View):
    def post(self, request, *args, **kw):
        return settings.SITE.kernel.success(html="Hallo?")


# class Callbacks(View):
#     def get(self, request, thread_id, button_id):
#         return callbacks.run_callback(request, thread_id, button_id)


class ActionParamChoices(View):
    # Examples: `welfare.pcsw.CreateCoachingVisit`
    def get(self, request, app_label=None, actor=None, an=None, field=None, **kw):
        actor = requested_actor(app_label, actor)
        ba = actor.get_url_action(an)
        if ba is None:
            raise Exception("Unknown action %r for %s" % (an, actor))
        field = ba.action.get_param_elem(field)
        qs, row2dict = choices_for_field(
            ba.create_request(request=request), ba.action, field)
        if field.blank:
            emptyValue = "<br/>"
        else:
            emptyValue = None
        return choices_response(actor, request, qs, row2dict, emptyValue)


class Choices(View):
    def get(self, request, app_label=None, rptname=None, fldname=None, **kw):
        """If `fldname` is specified, return a JSON object with two
        attributes `count` and `rows`, where `rows` is a list of
        `(display_text, value)` tuples.  Used by ComboBoxes or similar
        widgets.

        If `fldname` is not specified, returns the choices for the
        `record_selector` widget.

        """
        rpt = requested_actor(app_label, rptname)
        emptyValue = None
        if fldname is None:
            ar = rpt.create_request(request=request)
            qs = ar.data_iterator

            def row2dict(obj, d):
                d[constants.CHOICES_TEXT_FIELD] = str(obj)
                # getattr(obj,'pk')
                d[constants.CHOICES_VALUE_FIELD] = obj.pk
                return d
        else:
            # NOTE: if you define a *parameter* with the same name as
            # some existing *data element* name, then the parameter
            # will override the data element here in choices view.
            field = rpt.get_param_elem(fldname)
            if field is None:
                field = rpt.get_data_elem(fldname)
            if field.blank:
                # logger.info("views.Choices: %r is blank",field)
                emptyValue = "<br/>"
            ar = rpt.create_request(request=request)
            # if str(rpt) == 'comments.CommentsByRFC':
            #     print("20230426", ar.master_instance)
            qs, row2dict = choices_for_field(ar, rpt, field)

        return choices_response(rpt, request, qs, row2dict, emptyValue)


class Restful(View):
    """
    Used to collaborate with a restful Ext.data.Store.
    """

    @method_decorator(csrf_protect)
    def post(self, request, app_label=None, actor=None, pk=None):
        rpt = requested_actor(app_label, actor)
        ar = rpt.create_request(request=request)

        instance = ar.create_instance()
        # store uploaded files.
        # html forms cannot send files with PUT or GET, only with POST
        if ar.actor.handle_uploaded_files is not None:
            ar.actor.handle_uploaded_files(instance, request)

        data = request.POST.get("rows")
        data = json.loads(data)
        ar.form2obj_and_save(data, instance, True)

        # Ext.ensible needs grid_fields, not detail_fields
        ar.set_response(
            rows=[ar.ah.store.row2dict(ar, instance, ar.ah.store.grid_fields)]
        )
        return json_response(ar.response)

    @method_decorator(csrf_protect)
    def delete(self, request, app_label=None, actor=None, pk=None):
        rpt = requested_actor(app_label, actor)
        ar = rpt.create_request(request=request)
        ar.set_selected_pks(pk)
        return delete_element(ar, ar.selected_rows[0])

    def get(self, request, app_label=None, actor=None, pk=None):
        rpt = requested_actor(app_label, actor)
        assert pk is None, 20120814
        ar = rpt.create_request(request=request)
        rh = ar.ah
        rows = [
            rh.store.row2dict(ar, row, rh.store.grid_fields)
            for row in ar.sliced_data_iterator
        ]
        kw = dict(count=ar.get_total_count(), rows=rows)
        kw.update(title=str(ar.get_title()))
        return json_response(kw)

    @method_decorator(csrf_protect)
    def put(self, request, app_label=None, actor=None, pk=None):
        rpt = requested_actor(app_label, actor)
        ar = rpt.create_request(request=request)
        ar.set_selected_pks(pk)
        elem = ar.selected_rows[0]
        rh = ar.ah

        data = http.QueryDict(request.body).get("rows")
        data = json.loads(data)
        # 20240404 a = rpt.get_url_action(rpt.default_list_action_name)
        a = rpt.default_action
        ar = rpt.create_request(request=request, action=a)
        ar.renderer = settings.SITE.kernel.extjs_renderer
        ar.form2obj_and_save(data, elem, False)
        # Ext.ensible needs grid_fields, not detail_fields
        ar.set_response(rows=[rh.store.row2dict(
            ar, elem, rh.store.grid_fields)])
        return json_response(ar.response)


NOT_FOUND = "%s has no row with primary key %r"


class ApiElement(View):
    """
    The view that responds to ``api/app_label/actor/pk``.
    """

    @method_decorator(ensure_csrf_cookie)
    def get(self, request, app_label=None, actor=None, pk=None):
        vm = test_version_mismatch(request)
        if vm and settings.SITE.kernel.editing_front_end.app_label == "react":
            return json_response(vm)

        # this is also used by the react front end
        rpt = requested_actor(app_label, actor)
        # if not rpt.get_view_permission(request.user.user_type):
        #     raise PermissionDenied("{} has permission to view {}".format(
        #         request.user.user_type, rpt))
        # raise Exception(f"20241001 {rpt} {request.user.user_type}")

        action_name = request.GET.get(constants.URL_PARAM_ACTION_NAME, None)
        if action_name:
            ba = rpt.get_url_action(action_name)
            if ba is None:
                msg = f"{rpt} has no action {action_name}"
                print(msg)
                raise http.Http404(msg)
        else:
            ba = rpt.detail_action
            if ba is None:
                msg = f"{rpt} has no detail_action"
                print(msg)
                raise http.Http404(msg)

        # print(f"20250608 {rpt} {action_name}")
        fmt = request.GET.get(constants.URL_PARAM_FORMAT,
                              ba.action.default_format)

        try:
            ar = ba.create_request(
                request=request, renderer=settings.SITE.kernel.default_renderer)
            if pk and pk != "-99999" and pk != "-99998":
                if rpt.model is not None and issubclass(rpt.model, models.Model):
                    try:
                        ar.set_selected_pks(pk)
                    except rpt.model.DoesNotExist:
                        if fmt == constants.URL_FORMAT_JSON:
                            # rescue_ar: without sr and even request, to render
                            # a table request (grid view action) on breadcrumb
                            safe_kw = dict(
                                user=request.user,
                                renderer=settings.SITE.kernel.default_renderer)
                            rescue_ar = rpt.create_request(**safe_kw)
                            title = tostring(rescue_ar.href_to_request(
                                rescue_ar, icon_name=None))
                            datarec = dict(alert=False, success=False,
                                           title=title, **vm)
                            msg = _("Row {pk} is not visible here.").format(pk=pk)
                            default_table = rpt.model.get_default_table()
                            if default_table is rpt:
                                datarec.update(message=mark_safe(msg))
                                return json_response(datarec)
                            ar = default_table.detail_action.create_request(parent=ar)
                            try:
                                # take default table and try to show the row
                                ar.set_selected_pks(pk)
                            except default_table.model.DoesNotExist:
                                msg += " " + _("Neither is it visible in {table}.").format(
                                    table=ar.get_title())
                                datarec.update(message=mark_safe(msg))
                                return json_response(datarec)

                            lnk = ar.obj2htmls(ar.selected_rows[0], ar.get_title())
                            s = escape(_("But you can see it in {}.")).format(lnk)
                            msg += "<br>" + s
                            # msg = format_html("{}<br>{}", )
                            # msg = format_html("{}<br>{}", _("But you can see it in {link}"))
                            # url = ar.obj2url(dtar.selected_rows[0])
                            # msg += "<br>" + _('But you can see it in <a href="{url}">{table}</a>.').format(
                            #     url=url, table=ar.get_title())
                            datarec.update(message=mark_safe(msg))
                            return json_response(datarec)
                        raise http.Http404(f"Row {pk} does not exist on {rpt}")
                else:
                    ar.set_selected_pks(pk)
                # ar = ba.create_request(request=request, selected_pks=sr)
                elem = ar.selected_rows[0]
                # print(
                #     "20170116 views.ApiElement.get", ba,
                #     ar.action_param_values)
                # if len(ar.selected_rows):
                #     elem = ar.selected_rows[0]
                # else:
                #     raise http.Http404(
                #         "No permission to see {} {}.".format(rpt, action_name))
            else:
                elem = None
        except Exception as e:

            # Instantiating an action request can cause all kinds of errors,
            # ranging from invalid primary key to subtle bugs like #5924 (Menu
            # "My invoicing plan" fails), which was caused by the custom
            # invoicing.MyPlans.get_row_by_pk() method, which raised a
            # RelatedObjectDoesNotExist when accessing a non-nullable field.

            # On a production site we turn every exception into a 400 response
            # because otherwise every GET with a wrong pk would cause an email
            # to ADMINS.

            # logger.exception(e)
            msg = f"Invalid request for {repr(pk)} on {rpt} ({e})"
            logger.info("Error during ApiElement.get(): %s", msg)
            if is_devserver():
                # can be interesting during development but disturbs on a
                # production server
                logger.exception(e)
            raise http.Http404(msg) from None

        ar.renderer = settings.SITE.kernel.default_renderer

        if not ar.get_permission():
            msg = f"{ar.get_user()} has no permission to run {ar}"
            # raise Exception(msg)
            raise PermissionDenied(msg)

        # print("20240402 permission", ar, "granted to", ar.get_user(), ar.bound_action.action.select_rows, ar.selected_rows)

        if ba.action.opens_a_window:
            if fmt == constants.URL_FORMAT_JSON:
                # datarec = ba.action.get_datarec(pk)
                if pk == "-99999":
                    elem = ar.create_instance()
                    datarec = ar.elem2rec_insert(ar.ah, elem)
                elif pk == "-99998":
                    elem = ar.create_instance()
                    datarec = elem2rec_empty(ar, ar.ah, elem)
                elif elem is None:
                    datarec = dict(
                        success=False, message=NOT_FOUND % (rpt, pk))
                elif isinstance(ba.action, actions.ShowInsert):
                    elem = ar.create_instance()
                    datarec = ar.elem2rec_insert(ar.ah, elem)
                else:
                    datarec = ar.elem2rec_detailed(elem)
                datarec.update(**vm)

                fa = dict()
                for k, lst in rpt._field_actions.items():
                    fa[k] = [ar.row_action_button(elem, ba) for ba in lst]
                if fa:
                    datarec.update(field_actions=fa)

                return json_response(datarec)

            after_show = ar.get_status(record_id=pk)
            tab = request.GET.get(constants.URL_PARAM_TAB, None)
            if tab is not None:
                tab = int(tab)
                after_show.update(active_tab=tab)

            return http.HttpResponse(
                ar.renderer.html_page(
                    request,
                    ba.action.label,
                    on_ready=ar.renderer.action_call(request, ba, after_show),
                )
            )

        if pk == "-99998":
            assert elem is None
            elem = ar.create_instance()
            ar.selected_rows = [elem]
        elif elem is None:
            raise http.Http404(NOT_FOUND % (rpt, pk))

        return settings.SITE.kernel.run_action(ar)

    @method_decorator(csrf_protect)
    def post(self, request, app_label=None, actor=None, pk=None):
        ar = action_request(
            app_label,
            actor,
            request,
            request.POST,
            True,
            renderer=settings.SITE.kernel.extjs_renderer,
        )
        if pk == "-99998":
            elem = ar.create_instance()
            ar.selected_rows = [elem]
        else:
            ar.set_selected_pks(pk)
        # print("20210212 ApiElement.post()", ar, pk, ar.selected_rows)
        # print("20210212 ApiElement.post()", request.POST)
        return settings.SITE.kernel.run_action(ar)

    @method_decorator(csrf_protect)
    def put(self, request, app_label=None, actor=None, pk=None):
        data = http.QueryDict(request.body)  # raw_post_data before Django 1.4
        # print("20180712 ApiElement.put() %s" % data)
        ar = action_request(
            app_label,
            actor,
            request,
            data,
            False,
            renderer=settings.SITE.kernel.extjs_renderer,
        )
        ar.set_selected_pks(pk)
        return settings.SITE.kernel.run_action(ar)

    @method_decorator(csrf_protect)
    def delete(self, request, app_label=None, actor=None, pk=None):
        data = http.QueryDict(request.body)
        ar = action_request(
            app_label,
            actor,
            request,
            data,
            False,
            renderer=settings.SITE.kernel.extjs_renderer,
        )
        ar.set_selected_pks(pk)
        return settings.SITE.kernel.run_action(ar)


class ApiList(View):
    @method_decorator(csrf_protect)
    def post(self, request, app_label=None, actor=None):
        ar = action_request(app_label, actor, request, request.POST, True)
        ar.renderer = settings.SITE.kernel.extjs_renderer
        response = settings.SITE.kernel.run_action(ar)
        if (
            request.POST.get("_document_domain", None)
            and response["Content-Type"] == "text/html"
        ):
            # Have same-origin policy work for iframe of file upload. see ticket #2885
            # https://stackoverflow.com/questions/22627392/extjs-fileuplaod-cross-origin-frame
            response.content = """<html><head><script type="text/javascript">document.domain="{}";</script></head><body>{}</body></html>""".format(
                request.POST["_document_domain"], response.content.decode(
                    "utf-8")
            )
        return response

    @method_decorator(ensure_csrf_cookie)
    def get(self, request, app_label=None, actor=None):
        vm = test_version_mismatch(request)
        if vm and settings.SITE.kernel.editing_front_end.app_label == "react":
            return json_response(vm)
        ar = action_request(app_label, actor, request, request.GET, True)
        ar.renderer = settings.SITE.kernel.extjs_renderer
        rh = ar.ah

        fmt = request.GET.get(
            constants.URL_PARAM_FORMAT, ar.bound_action.action.default_format
        )
        # print(20170921, fmt)

        if fmt == constants.URL_FORMAT_JSON:
            rows = [rh.store.row2list(ar, row)
                    for row in ar.sliced_data_iterator]
            total_count = ar.get_total_count()
            # raise Exception("20171208 {}".format(ar.data_iterator.query))
            for row in ar.create_phantom_rows():
                if (
                    ar.limit is None
                    or len(rows) + 1 < ar.limit
                    or ar.limit == total_count + 1
                ):
                    d = rh.store.row2list(ar, row)
                    rows.append(d)
                total_count += 1

            kw = dict(
                count=total_count, rows=rows, success=True, no_data_text=ar.no_data_text
            )

            if True:
                kw.update(title=str(ar.get_title()))
                # kw.update(title=str(ar.get_breadcrumbs()))
            else:
                # 20190704 work in progress.
                # add open_in_own_window button after title of slave panel
                kw.update(
                    title=str(ar.get_title())
                    # title=str(ar.get_breadcrumbs())
                    + " "
                    + tostring(ar.open_in_own_window_button())
                )

            if ar.actor.parameters:
                kw.update(
                    param_values=ar.actor.params_layout.params_store.pv2dict(
                        ar, ar.param_values
                    )
                )
            kw.update(**vm)
            return json_response(kw)

        if fmt == constants.URL_FORMAT_HTML:
            after_show = ar.get_status()

            sp = request.GET.get(constants.URL_PARAM_SHOW_PARAMS_PANEL, None)
            if sp is not None:
                # ~ after_show.update(show_params_panel=sp)
                after_show.update(
                    show_params_panel=constants.parse_boolean(sp))

            # if isinstance(ar.bound_action.action, actions.ShowInsert):
            #     elem = ar.create_instance()
            #     rec = ar.elem2rec_insert(rh, elem)
            #     after_show.update(data_record=rec)

            kw = dict(
                on_ready=ar.renderer.action_call(
                    ar.request, ar.bound_action, after_show
                )
            )
            # ~ print '20110714 on_ready', params
            kw.update(title=ar.get_title())
            return http.HttpResponse(ar.renderer.html_page(request, **kw))

        if fmt == "csv":
            # ~ response = HttpResponse(mimetype='text/csv')
            charset = settings.SITE.csv_params.get("encoding", "utf-8")
            response = http.HttpResponse(
                content_type='text/csv;charset="%s"' % charset)
            if False:
                response["Content-Disposition"] = (
                    'attachment; filename="%s.csv"' % ar.actor
                )
            else:
                # ~ response = HttpResponse(content_type='application/csv')
                response["Content-Disposition"] = 'inline; filename="%s.csv"' % ar.actor

            # ~ response['Content-Disposition'] = 'attachment; filename=%s.csv' % ar.get_base_filename()
            w = ucsv.UnicodeWriter(response, **settings.SITE.csv_params)
            w.writerow(ar.ah.store.column_names())
            if True:  # 20130418 : also column headers, not only internal names
                column_names = None
                fields, headers, cellwidths = ar.get_field_info(column_names)
                w.writerow(headers)

            for row in ar.data_iterator:
                w.writerow([str(v) for v in rh.store.row2list(ar, row)])
            return response

        if fmt == constants.URL_FORMAT_PRINTER:
            if ar.get_total_count() > MAX_ROW_COUNT:
                raise Exception(
                    _("List contains more than %d rows") % MAX_ROW_COUNT)
            response = http.HttpResponse(
                content_type='text/html;charset="utf-8"')
            doc = Document(force_str(ar.get_title()))
            doc.body.append(E.h1(doc.title))
            t = doc.add_table()
            # ~ settings.SITE.kernel.ar2html(ar,t,ar.data_iterator)
            ar.dump2html(t, ar.data_iterator)
            doc.write(response, encoding="utf-8")
            return response

        return settings.SITE.kernel.run_action(ar)
