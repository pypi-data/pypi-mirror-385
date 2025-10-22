# -*- coding: UTF-8 -*-
# Copyright 2020-2025 Rumma & Ko Ltd
# License: GNU Affero General Public License v3 (see file COPYING for details)

from lino.api.ad import Plugin


class Plugin(Plugin):
    needs_plugins = [
        "lino.modlib.system",  # 'lino.modlib.memo',
        "lino.modlib.linod",
        "lino.modlib.jinja",
        "lino.modlib.bootstrap5"
    ]
    locations: list[tuple[str, str]] = []
    skin = 'boots'
    # with_trees = False

    def get_requirements(self, site):
        yield "python-lorem"

    def post_site_startup(self, site):
        from lino.core.actors import Actor
        from .renderer import Renderer
        from .mixins import Publishable

        super().post_site_startup(site)
        self.renderer = Renderer(self)
        self.cls2loc = {}

        locations = []
        for loc, view in self.locations:
            app_label, model_name = view.split(".")
            app = site.models.get(app_label)
            cls = getattr(app, model_name, None)
            if not isinstance(cls, type) or not issubclass(cls, Actor):
                raise Exception(f"location {loc}: {cls} is not an Actor")
            if not issubclass(cls.model, Publishable):
                raise Exception(
                    f"location {loc},{view}: "
                    f"model {type(cls.model)} is not Publishable")
            cls._lino_publisher_location = loc
            locations.append((loc, cls))
            self.cls2loc[cls] = loc
        self.locations = tuple(locations)

    def get_patterns(self):
        from django.urls import re_path as url
        from . import views

        for location, table_class in self.locations:
            yield url(
                f"^{location}/(?P<pk>.+)$",
                # f"^{location}/<int:pk>$",
                views.Element.as_view(table_class=table_class))

            yield url(
                f"^{location}$",
                # f"^{location}/<int:pk>$",
                views.List.as_view(table_class=table_class))

        # Only if this is the primary front end:
        if self.site.kernel.primary_front_end is self:

            yield url("^$", views.Index.as_view())

            # if self.with_trees:
            #     # yield url("^(?P<ref>.*)$", views.Index.as_view())
            #     Tree = self.site.models.publisher.Tree
            #     from django.db.utils import OperationalError, ProgrammingError
            #     # language=self.site.DEFAULT_LANGUAGE.django_code
            #     try:
            #         for t in Tree.objects.filter(ref__isnull=False):
            #             yield url(f"^{t.ref}$", views.Index.as_view(ref=t.ref))
            #     except (OperationalError, ProgrammingError):
            #         pass

        yield url('^login$', views.Login.as_view())
        yield url('^logout$', views.Logout.as_view())

    def setup_main_menu(self, site, user_type, m, ar=None):
        mg = self.get_menu_group()
        m = m.add_menu(mg.app_label, mg.verbose_name)
        m.add_action("publisher.Pages")

    def setup_config_menu(self, site, user_type, m, ar=None):
        mg = self.get_menu_group()
        m = m.add_menu(mg.app_label, mg.verbose_name)
        m.add_action("publisher.SpecialPages")
        # if self.with_trees:
        #     m.add_action("publisher.Trees")
