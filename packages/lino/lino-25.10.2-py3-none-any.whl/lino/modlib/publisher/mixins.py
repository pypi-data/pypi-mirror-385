# -*- coding: UTF-8 -*-
# Copyright 2020-2025 Rumma & Ko Ltd
# License: GNU Affero General Public License v3 (see file COPYING for details)

# from inspect import isclass
from django import http
from django.db import models
from django.conf import settings
# from django.utils.translation import get_language
# from lino.core.renderer import add_user_language
# from lino.core.utils import full_model_name
# from lino.utils import buildurl
from lino.mixins.periods import CombinedDateTime
from lino.utils.html import tostring, mark_safe
from lino.modlib.printing.mixins import Printable
from lino.api import dd, rt, _
from .choicelists import PublishingStates, SpecialPages
# from .choicelists import PublisherViews, PublishingStates

# WITH_TREES = dd.get_plugin_setting('publisher', 'with_trees', False)


class PreviewPublication(dd.Action):
    label = _("Preview")
    button_text = "🌐"  # 1F310

    select_rows = True

    def run_from_ui(self, ar, **kw):
        # sr_selected = not isclass(self)
        # if sr_selected:
        #     ar.success(open_url=self.publisher_url())
        # else:
        #     ar.success(open_url=self.publisher_url(self, not sr_selected))
        obj = ar.selected_rows[0]
        # ar.success(open_url=obj.publisher_url(ar))
        ar.success(open_url=dd.plugins.publisher.renderer.obj2url(ar, obj))

    # def get_view_permission(self, user_type):
    #     return super().get_view_permission(user_type)


class Publishable(Printable):

    class Meta:
        abstract = True
        app_label = "publisher"

    publisher_template = "publisher/{skin}/page.pub.html"

    if dd.is_installed("publisher"):

        @dd.htmlbox()
        def full_page(self, ar):
            if ar is None:
                return ""
            return mark_safe("".join(self.as_page(ar)))

        # previous_page = dd.ForeignKey("self", null=True, blank=True,
        #     verbose_name=_("Previous page"))

        # previous_page_view = PublisherViews.field(blank=True, null=True,
        #     verbose_name=_("Previous page (view)"))
        # previous_page_id = IntegerField(blank=True, null=True,
        #     verbose_name=_("Previous page (key)"))

        preview_publication = PreviewPublication()

    # def get_publisher_tree(self):
    #     return todo

    def is_public(self):
        return True

    def get_preview_context(self, ar):
        return ar.get_printable_context(obj=self)

    def get_publisher_response(self, ar):
        # if not self.is_public():
        #     return http.HttpResponseNotFound(
        #         f"{self.__class__} {self.pk} is not public")
        context = self.get_preview_context(ar)
        # html = ''.join(self.as_page(ar))
        # # context.update(content=html, admin_site_prefix=dd.plugins.publisher.admin_location)
        # context.update(content=html)
        tplname = self.publisher_template.format(skin=dd.plugins.publisher.skin)
        tpl = dd.plugins.jinja.renderer.jinja_env.get_template(tplname)
        # print(f"20251018 {tplname}")
        return http.HttpResponse(
            tpl.render(**context), content_type='text/html;charset="utf-8"')

    def get_root_page(self):
        return SpecialPages.home.get_object()

    def home_and_children(self, ar):
        # home = self.publisher_tree.root_page
        Page = rt.models.publisher.Page
        # flt = dict()
        # if WITH_TREES:
        #     flt.update(publisher_tree=self.publisher_tree)
        # qs = Page.objects.filter(parent__isnull=True, **flt)
        # home = qs.first()
        home = self.get_root_page()
        # if home is None:
        #     try:
        #         home = SpecialPages.home.get_object(**flt)
        #     except Page.DoesNotExist:
        #         raise Page.DoesNotExist(f"No home page for {flt}")
        return home, Page.objects.filter(parent=home)
        # return dv.model.objects.filter(models.Q(parent=index_node) | models.Q(ref='index'), language=language)

    def get_prev_page(self, ar):
        return None

    def get_next_page(self, ar):
        return None

    def get_prev_link(self, ar, text="◄"):  # "◄" 0x25c4
        if (obj := self.get_prev_page(ar)) is None:
            return text
        return tostring(ar.obj2html(obj, text))

    def get_next_link(self, ar, text="►"):  # ► (0x25BA)
        if (obj := self.get_next_page(ar)) is None:
            return text
        return tostring(ar.obj2html(obj, text))


class Illustrated(dd.Model):

    class Meta:
        abstract = True

    album = dd.ForeignKey('albums.Album', blank=True, null=True)

    @property
    def main_image(self):
        if self.album:
            if (ai := self.album.items.first()) is not None:
                return ai.upload

    # @dd.htmlbox()
    # def preview(self, ar):
    #     if (upload := self.main_image) is not None:
    #         return upload.preview.__call__(ar)

    @dd.htmlbox()
    def thumbnail(self, ar):
        if (upload := self.main_image) is not None:
            fld = rt.models.uploads.Upload._meta.get_field('thumbnail')
            return fld.value_from_object(upload, ar)


class PublishableContent(Publishable, CombinedDateTime):

    class Meta:
        abstract = True

    pub_date = models.DateField(_("Publication date"), blank=True, null=True)
    pub_time = dd.TimeField(_("Publication time"), blank=True, null=True)
    publishing_state = PublishingStates.field(default="draft")
    # main_image = dd.ForeignKey('uploads.Upload', blank=True,
    #                            null=True, verbose_name=_("Main image"))

    def on_create(self, ar):
        # Sets the :attr:`pub_date` and :attr:`pub_time` to now.
        if not settings.SITE.loading_from_dump:
            self.set_datetime('pub', dd.now())
        super().on_create(ar)

    def on_duplicate(self, ar, master):
        self.publishing_state = PublishingStates.draft
        super().on_duplicate(ar, master)

    def is_public(self):
        # if WITH_TREES:
        #     if self.publisher_tree.private:
        #         return False
        return self.publishing_state.is_public


class TranslatableContent(Printable):

    class Meta:
        abstract = True
        app_label = "publisher"

    language = dd.LanguageField()
    translated_from = dd.ForeignKey(
        "self", verbose_name=_("Translated from"),
        null=True, blank=True,
        related_name="translated_to")

    def get_print_language(self):
        return self.language

    def on_create(self, ar):
        self.language = ar.get_user().language
        super().on_create(ar)

    def get_publisher_response(self, ar):
        if ar and ar.request and self.language != ar.request.LANGUAGE_CODE:
            rqlang = ar.request.LANGUAGE_CODE
            # tt = rt.models.pages.Translation.objects.filter(
            #     parent=self, language=ar.request.LANGUAGE_CODE).first()
            obj = None
            if self.translated_from_id and self.translated_from.language == rqlang:
                obj = self.translated_from
            else:
                sources = set([self.id])
                p = self.translated_from
                while p is not None:
                    sources.add(p.id)
                    p = p.translated_from
                qs = self.__class__.objects.filter(
                    language=rqlang, translated_from__in=sources)
                obj = qs.first()
                # obj = self.translated_to.filter(language=rqlang).first()
            # print("20231027 redirect to translation", tt.language, ar.request.LANGUAGE_CODE)
            if obj is not None:
                # print("20231028", self.language, "!=", ar.request.LANGUAGE_CODE, tt)
                ar.selected_rows = [obj]
                url = ar.get_request_url()
                return http.HttpResponseRedirect(url)
        return super().get_publisher_response(ar)
