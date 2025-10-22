# -*- coding: UTF-8 -*-
# Copyright 2012-2025 Rumma & Ko Ltd
# License: GNU Affero General Public License v3 (see file COPYING for details)

from django.db import models
from django.utils.translation import get_language

# from django.utils.translation import get_language
# from django.utils.html import format_html

from lino.api import dd, rt, _
from lino.utils.html import E
from lino.utils.soup import MORE_MARKER
from lino.core import constants
# from lino.core.renderer import add_user_language
from lino.modlib.office.roles import OfficeUser

from .choicelists import SpecialPages


VARTABS = ""

if dd.is_installed("topics"):
    VARTABS += " topics.TagsByOwner:20"
if dd.is_installed("comments"):
    VARTABS += " comments.CommentsByRFC:60"


class PageDetail(dd.DetailLayout):
    # main = "general first_panel more"
    main = f"general first_panel {VARTABS} more"

    first_panel = dd.Panel(
        """
        treeview_panel:20 preview:60
        """, label=_("Preview"))

    general = dd.Panel(
        """
    content_panel:60 right_panel:20
    """,
        label=_("General"),
        required_roles=dd.login_required(OfficeUser),
    )

    # more = dd.Panel(
    #     VARTABS,
    #     label=_("Discussion"),
    #     required_roles=dd.login_required(OfficeUser),
    # )

    content_panel = """
    title id
    body
    """

    # right_panel = """
    # parent seqno
    # child_node_depth
    # page_type
    # filler
    # """

    right_panel = """
    parent seqno
    publisher.PagesByParent
    """

    more = dd.Panel("""
    root_page language
    special_page album
    # filler child_node_depth
    publishing_state
    publisher.TranslationsByPage
    """, label=_("More"))


class Pages(dd.Table):
    model = "publisher.Page"
    column_names = "title root_page id *"
    detail_layout = "publisher.PageDetail"
    insert_layout = """
    title
    root_page
    language #filler
    """
    default_display_modes = {None: constants.DISPLAY_MODE_LIST}


class PagesByParent(Pages):
    master_key = "parent"
    label = _("Children")
    # ~ column_names = "title user *"
    order_by = ["seqno"]
    column_names = "seqno title *"
    # default_display_modes = {None: constants.DISPLAY_MODE_LIST}


class RootPages(Pages):
    filter = models.Q(parent=None)
    label = _("Root pages")
    # ~ column_names = "title user *"
    order_by = ["language", "id"]
    column_names = "id language title *"

    @classmethod
    def param_defaults(self, ar, **kw):
        kw = super().param_defaults(ar, **kw)
        kw.update(language=get_language())
        return kw

    # @classmethod
    # def get_title_tags(self, ar):
    #     return []


# PublisherViews.add_item_lazy("p", Pages)
# PublisherViews.add_item_lazy("n", Nodes)

# PageTypes.add_item(Pages, 'pages')


class TranslationsByPage(Pages):
    master_key = "translated_from"
    label = _("Translations")
    column_names = "title language id *"
    default_display_modes = {None: constants.DISPLAY_MODE_SUMMARY}

    @classmethod
    def row_as_summary(cls, ar, obj, text=None, **kwargs):
        # return format_html("({}) {}", obj.language, obj.as_summary_row(ar, **kwargs))
        return E.span("({}) ".format(obj.language), obj.as_summary_item(ar, text, **kwargs))


# if dd.plugins.publisher.with_trees:
#
#     class Trees(dd.Table):
#         model = "publisher.Tree"
#         column_names = "ref root_pages user group private id *"
#         insert_layout = """
#         ref group
#         private
#         """
#         detail_layout = """
#         ref user group id
#         private
#         root_pages
#         """

# SpecialPages.add_item(
#     "pages",  # filler=filler,
#     body=_("List of trees on this site.") + MORE_MARKER + " [show publisher.Trees]",
#     title=_("Publisher trees"),
#     parent='home')

SpecialPages.add_item(
    "roots",  # filler=filler,
    body=_("List of root pages on this site.") +
    MORE_MARKER + " [show publisher.RootPages]",
    title=_("Root pages"),
    parent='home')
