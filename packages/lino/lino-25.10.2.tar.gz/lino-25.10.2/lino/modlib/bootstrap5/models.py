# -*- coding: UTF-8 -*-
# Copyright 2014-2023 Rumma & Ko Ltd
# License: GNU Affero General Public License v3 (see file COPYING for details)

# from django.conf import settings
# from lino.core.tables import AbstractTable
# from lino.core.roles import Expert
#
# from lino.api import dd, _


# class ShowAsHtml(dd.Action):
#     label = _("HTML")
#     help_text = _("Show this table in Bootstrap3 interface")
#     icon_name = "html"
#     ui5_icon_name = "sap-icon://attachment-html"
#     sort_index = -15
#     select_rows = False
#     default_format = "ajax"
#     preprocessor = "Lino.get_current_grid_config"
#     callable_from = "t"
#     required_roles = dd.login_required(Expert)
#
#     def run_from_ui(self, ar, **kw):
#         url = dd.plugins.bootstrap5.renderer.get_request_url(ar)
#         ar.success(open_url=url)
#

# if settings.SITE.default_ui != "lino.modlib.bootstrap5":
#     AbstractTable.show_as_html = ShowAsHtml()
