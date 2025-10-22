# -*- coding: UTF-8 -*-
# Copyright 2012-2025 Rumma & Ko Ltd
# License: GNU Affero General Public License v3 (see file COPYING for details)

from html import escape
from django.db import models
from django.conf import settings
from django.utils import translation
# from django.utils.translation import get_language
from lino.api import dd, rt, _
# from lino.utils import mti
from lino.utils.html import E, tostring, format_html, mark_safe
from lino.utils.instantiator import get_or_create
# from lino.core.renderer import add_user_language
# from lino.utils.mldbc.fields import LanguageField
from lino.mixins import Hierarchical, Sequenced, Referrable
# from lino.modlib.summaries.mixins import Summarized
from lino.modlib.comments.mixins import Commentable
from lino.modlib.linod.choicelists import schedule_daily
from lino.modlib.memo.mixins import Previewable
from lino.modlib.users.mixins import UserAuthored, PrivacyRelevant
from lino_xl.lib.topics.mixins import Taggable
from lino.modlib.bootstrap5 import PAGE_TITLE_TEMPLATE


from .choicelists import PublishingStates, SpecialPages
from .mixins import Publishable, TranslatableContent, PublishableContent, Illustrated
from .ui import *

child_node_depth = 1

# if dd.plugins.publisher.with_trees:
#
#     class Tree(UserAuthored, PrivacyRelevant, Referrable):
#
#         class Meta:
#             verbose_name = _("Tree")
#             verbose_name_plural = _("Trees")
#             abstract = dd.is_abstract_model(__name__, "Tree")
#             # unique_together = ["ref", "language"]
#
#         # ref = dd.CharField(_("Reference"), max_length=200, blank=True, null=True)
#         # root_page = dd.ForeignKey(
#         #     "publisher.Page", null=True, blank=True,
#         #     verbose_name=_("Root page"), related_name='+')
#
#         # @dd.virtualfield(dd.ForeignKey(
#         #     'publisher.Page', verbose_name=_("Root page")))
#         # def root_page(self, ar=None):
#         #     return self.get_root_page(get_language())
#
#         @dd.displayfield(_("Root pages"))
#         def root_pages(self, ar=None):
#             if not self.pk:
#                 return ""
#             chunks = []
#             for lng in settings.SITE.languages:
#                 qs = Page.objects.filter(
#                     # parent__isnull=True,
#                     publisher_tree=self,
#                     special_page=SpecialPages.home,
#                     language=lng.django_code)
#                 if qs.count() == 0:
#                     chunks.append(lng.django_code)
#                 elif qs.count() > 1:
#                     chunks.append("!?")
#                 else:
#                     chunks.append(ar.obj2htmls(qs.first(), text=lng.django_code))
#             return "<span>" + mark_safe(" ".join(chunks)) + "/<span>"
#
#         def get_root_page(self, language):
#             if self.pk is not None:
#                 qs = Page.objects.filter(
#                     parent__isnull=True, publisher_tree=self, language=language)
#                 return qs.first()
#                 # try:
#                 #     return Page.objects.get(parent=None, publisher_tree=self)
#                 # except Page.DoesNotExist:
#                 #     return None


class Page(
    Hierarchical, Sequenced, Previewable, Commentable,
    TranslatableContent, PublishableContent, Illustrated, Taggable
):
    class Meta:
        verbose_name = _("Page")
        verbose_name_plural = _("Pages")
        abstract = dd.is_abstract_model(__name__, "Page")
        # if dd.is_installed("groups"):
        #     unique_together = ["group", "ref", "language"]
        # else:
        #     unique_together = ["ref", "language"]
        # unique_together = ["publisher_tree", "language"]

    memo_command = "page"
    allow_cascaded_delete = ['parent']

    title = dd.CharField(_("Title"), max_length=250, blank=True)
    # child_node_depth = models.IntegerField(default=1)
    special_page = SpecialPages.field(blank=True)
    # if dd.get_plugin_setting('publisher', 'with_trees', False):
    # if dd.plugins.publisher.with_trees:
    #     # publisher_tree = dd.ForeignKey("publisher.Tree", null=True, blank=True)
    #     publisher_tree = dd.ForeignKey("publisher.Tree")
    # else:
    #     publisher_tree = dd.DummyField()

    previous_page = dd.ForeignKey(
        "self", null=True, blank=True, editable=False,
        verbose_name=_("Previous page"), related_name='+')
    root_page = dd.ForeignKey(
        "self", null=True, blank=True,
        verbose_name=_("Root page"), related_name='+')

    def __str__(self):
        return self.title or super().__str__()

    @classmethod
    def get_simple_parameters(cls):
        lst = list(super().get_simple_parameters())
        lst.append('root_page')
        lst.append('parent')
        lst.append('language')
        lst.append('album')
        lst.append('publishing_state')
        return lst

    # @classmethod
    # def param_defaults(self, ar, **kw):
    #     kw = super().param_defaults(ar, **kw)
    #     kw.update(language=get_language())
    #     return kw

    # def on_create(self, ar):
    #     self.page_type = self.get_page_type()
    #     super().on_create(ar)

    # def get_for_language(self, lng):
    #     # lng is a LanguageInfo object settings.SITE.get_language_info()
    #     if lng.prefix:
    #         qs = self.__class__.objects.filter(
    #             translated_from=self, language=lng.code)
    #         return qs.first()
    #     return self

    def full_clean(self):
        if self.root_page is None:
            if self.parent is not None:
                self.root_page = self.parent.root_page
        elif self.root_page == self:
            self.root_page = None
        super().full_clean()

    def get_root_page(self):
        return self.root_page or self

    def get_node_info(self, ar):
        return ""

    def is_public(self):
        if self.root_page and not self.root_page.is_public():
            return False
        # if dd.plugins.publisher.with_trees:
        #     return not self.publisher_tree.private
        return super().is_public()

    def mti_child(self):
        #     if self.page_type:
        #         return mti.get_child(self, self.page_type.nodes_table.model) or self
        return self

    def walk(self):
        yield self
        for c in self.children.all():
            for i in c.walk():
                yield i

    # def as_summary_row(self, ar, **kwargs):
    #     return ar.obj2htmls(self, **kwargs)

    # def as_story_item(self, ar, **kwargs):
    #     return "".join(self.as_page(ar, **kwargs))

    def as_paragraph(self, ar):
        title = format_html("<b>{}</b>", self.title)
        if (url := ar.obj2url(self)) is not None:
            title = format_html(
                '<a href="{url}" style="text-decoration:none;color:black;">{title}</a>',
                title=title, url=url)
        body = self.get_body_parsed(ar, short=True)
        if body:
            return format_html("{} &mdash; {}", title, body)
        return title

    def toc_html(self, ar, max_depth=1):
        def li(obj):
            # return "<li>{}</li>".format(obj.memo2html(ar, str(obj)))
            return "<li>{}</li>".format(tostring(ar.obj2html(obj)))

        html = "".join([li(obj) for obj in self.children.all()])
        return '<ul class="publisher-toc">{}</ul>'.format(html)

    def as_page(self, ar, display_mode="detail", hlevel=1, home=None):
        if home is None:
            home = self
        if display_mode == "detail" and hlevel == 1:
            breadcrumbs = list(self.get_parental_line())
            if len(breadcrumbs) > 1:
                breadcrumbs = [
                    """<a href="{0}">{1}</a>""".format(
                        ar.obj2url(p.mti_child()), p.title)
                    for p in breadcrumbs[:-1]
                ]
                yield "<p>{}</p>".format(" &raquo; ".join(breadcrumbs))
        if display_mode in ("detail", "story"):
            # title = "<h{0}>{1}</h{0}>".format(hlevel, escape(self.title))
            title = format_html(PAGE_TITLE_TEMPLATE, self.title)
        else:
            title = "<b>{}</b> — ".format(escape(self.title))
            title += self.get_body_parsed(ar, short=True)
            title = "<li>{}</li>".format(title)
        # edit_url = ar.renderer.obj2url(ar, self)
        # url = self.publisher_url(ar)
        # print("20231029", ar.renderer)
        # url = ar.obj2url(self.mti_child())
        url = ar.obj2url(self)
        if url is None:
            yield title
        else:
            yield """<a href="{}"
            style="text-decoration:none; color: black;">{}</a>
            """.format(escape(url), title)

        # if not self.is_public():
        #     return

        if display_mode in ("detail",):
            info = self.get_node_info(ar)
            if info:
                yield """<p class="small">{}</p>""".format(info)
                # https://getbootstrap.com/docs/3.4/css/#small-text

        if display_mode == "story":
            yield self.get_body_parsed(ar, short=True)

        # if display_mode in ("detail", "story"):
        if display_mode == "detail":
            # if hlevel == 1 and not dd.plugins.memo.use_markup and self.parent_id:
            #     yield self.toc_html(ar)

            if hlevel == 1 and self.main_image:
                yield f"""
                <div class="row">
                    <div class="center-block">
                        <a href="#" class="thumbnail">
                            <img src="{self.main_image.get_media_file().get_image_url()}">
                        </a>
                    </div>
                </div>
                """

            # yield self.body_full_preview
            yield self.get_body_parsed(ar, short=False)

            # if self.filler:
            #     if hlevel == 1:
            #         yield self.filler.get_dynamic_story(ar, self)
            #     else:
            #         yield self.filler.get_dynamic_paragraph(ar, self)

            # if dd.plugins.memo.use_markup:
            #     return

            if not self.children.exists():
                return

            # yield "<p><b>{}</b></p>".format(_("Children:"))

            if hlevel > child_node_depth:
                yield " (...)"
                return
            if hlevel == child_node_depth:
                display_mode = "list"
                yield "<ul>"
            children = self.children.order_by("seqno")
            for obj in children:
                for i in obj.as_page(ar, display_mode, hlevel=hlevel + 1, home=home):
                    yield i
            if hlevel == child_node_depth:
                yield "</ul>"
        # else:
        #     yield " — "
        #     yield self.body_short_preview
        #     for obj in self.children.order_by('seqno'):
        #         for i in obj.as_page(ar, "list", hlevel+1):
        #             yield i

    # @classmethod
    # def lookup_page(cls, ref):
    #     try:
    #         return cls.objects.get(ref=ref, language=get_language())
    #     except cls.DoesNotExist:
    #         pass

    # if dd.plugins.publisher.with_trees:
    #
    #     def full_clean(self):
    #         if self.publisher_tree is None and self.parent is not None:
    #             self.publisher_tree = self.parent.publisher_tree
    #         super().full_clean()

    def update_page(self, prev, root):
        save = False
        if self.previous_page != prev:
            self.previous_page = prev
            save = True
        if self == root:
            root = None
        if self.root_page != root:
            self.root_page = root
            save = True
        # if dd.plugins.publisher.with_trees:
        #     if self.publisher_tree != tree:
        #         self.publisher_tree = tree
        #         save = True
        if save:
            self.save()

    def get_prev_page(self, ar):
        return self.previous_page

    def get_next_page(self, ar):
        return self.__class__.objects.filter(previous_page=self).first()

    @classmethod
    def get_dashboard_objects(cls, user):
        # print("20210114 get_dashboard_objects()", get_language())
        # qs = cls.objects.filter(parent__isnull=True, language=get_language())
        qs = cls.objects.filter(parent__isnull=True)
        for obj in qs.order_by("seqno"):
            yield obj

    # def get_page_type(self):
    #     return PageTypes.pages

    # def is_public(self):
    #     return True

    def get_absolute_url(self, **kwargs):
        raise Exception("20251018")
        # parts = []
        # # if self.group is not None:
        # #     if self.group.ref is not None:
        # #         parts.append(self.group.ref)
        # if self.root_page and self.root_page.special_page == SpecialPages.home:
        #     if self.publisher_tree.ref != "main":
        #         parts.append(self.publisher_tree.ref)
        # if dd.plugins.publisher.with_trees:
        #     if self.publisher_tree.ref:
        #         if self.publisher_tree.ref != "index":
        #             parts.append(self.publisher_tree.ref)
        # return dd.plugins.publisher.build_plain_url(*parts, **kwargs)


if dd.plugins.memo.use_markup:
    dd.update_field(Page, "body", format="plain")


@schedule_daily()
def update_publisher_pages(ar):
    # BaseRequest(parent=ar).run(settings.SITE.site_config.check_all_summaries)
    # rt.login().run(settings.SITE.site_config.check_all_summaries)
    Page = rt.models.publisher.Page
    # for pv in PublisherViews.get_list_items():
    # for m in rt.models_by_base(Published, toplevel_only=True):
    ar.logger.info("Create special pages...")
    # trees = []
    # if dd.plugins.publisher.with_trees:
    #     Tree = rt.models.publisher.Tree
    #     for tree in Tree.objects.all():
    #         trees.append(dict(publisher_tree=tree))
    # else:
    #     trees.append(dict())
    # for tree in trees:
    for sp in SpecialPages.get_list_items():
        translated_from = None
        obj = None
        for lng in settings.SITE.languages:
            with translation.override(lng.django_code):
                # kwargs = dict(special_page=sp, **tree)
                kwargs = dict(special_page=sp)
                kwargs.update(language=lng.django_code)
                qs = Page.objects.filter(**kwargs)
                if qs.count() == 0:
                    ar.logger.info("Created special page %s", kwargs)
                    kwargs.update(publishing_state="published")
                    if lng.suffix:
                        kwargs.update(translated_from=translated_from)
                    obj = Page(**kwargs)
                    sp.on_page_created(obj)
                    obj.full_clean()
                    obj.save()
                elif qs.count() > 1:
                    raise Exception(f"Multiple pages for {kwargs}")
                    # ar.logger.warning("Multiple pages for %s", kwargs)
                # else:
                #     ar.logger.info("Special page %s exists", kwargs)
                if not lng.suffix:
                    translated_from = obj

    count = 0
    ar.logger.info("Update publisher pages...")
    for root in Page.objects.filter(parent__isnull=True):
        prev = None
        for obj in root.walk():
            # obj.update_page(prev, root.publisher_tree)
            obj.update_page(prev, root)
            prev = obj
            count += 1
    ar.logger.info("%d pages have been updated.", count)


def make_demo_pages(pages_desc, root_ref, group=None):
    from lorem import get_paragraph
    # if dd.plugins.publisher.with_trees:
    #     # user = rt.models.users.User(username=root_ref, user_type=UserTypes.)
    #     # yield user
    #     user = dd.plugins.users.get_demo_user()
    #     get_or_create(rt.models.groups.Membership, group=group, user=user)
    #     tree = dict(publisher_tree=get_or_create(
    #         rt.models.publisher.Tree, ref=root_ref, group=group, user=user))
    # else:
    #     tree = dict()
    # Translation = rt.models.pages.Translation
    # for lc in settings.SITE.LANGUAGE_CHOICES:
    #     language = lc[0]
    #     kwargs = dict(language=language, ref='index')
    #     with translation.override(language):

    parent_nodes = []
    for lng in settings.SITE.languages:
        counter = {None: 0}
        # count = 0
        # home_page = Page.objects.get(
        #     special_page=SpecialPages.home, language=lng.django_code)

        with translation.override(lng.django_code):

            def make_pages(pages, parent=None, root_ref=None):
                root_page = None
                for page in pages:
                    if len(page) != 3:
                        raise Exception(f"Oops {page}")
                    title, body, children = page
                    kwargs = dict(title=title, language=lng.django_code)
                    if body is None:
                        kwargs.update(body=get_paragraph())
                    else:
                        kwargs.update(body=body)
                    if parent is not None:
                        kwargs.update(parent=parent)
                    if root_page is not None:
                        kwargs.update(root_page=root_page)
                    if lng.suffix:
                        kwargs.update(
                            translated_from=parent_nodes[counter[None]])
                    if dd.is_installed("publisher"):
                        kwargs.update(publishing_state='published')
                    obj = Page(**kwargs)
                    yield obj
                    if root_ref is not None:
                        root_page = obj
                    if not lng.suffix:
                        parent_nodes.append(obj)
                    counter[None] += 1
                    # print("20230324", title, kwargs)
                    yield make_pages(children, obj)

            # yield make_pages(pages_desc, parent=home_page)
            yield make_pages(pages_desc, None, root_ref)
