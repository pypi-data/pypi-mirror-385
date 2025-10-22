# -*- coding: UTF-8 -*-
# Copyright 2012-2021 Rumma & Ko Ltd
# License: GNU Affero General Public License v3 (see file COPYING for details)
"""Defines the model mixins :class:`BabelNamed` and :class:`BabelDesignation`.

"""

from django.conf import settings
from django.utils.translation import gettext_lazy as _

from lino.core import model

from .fields import BabelCharField


class BabelNamed(model.Model):
    """
    Mixin for models that have a babel field `name` (labelled
    "Designation" by default) for each language.

    This mixin is deprecated (but without any planned expiry date so far). For
    new applications we recommend to use :class:`BabelDesignated` instead.
    Because the term "name" is used in programming to refer to something (which
    we implement as Referrable). So we don't recommend to use a database field
    having "name" as name.

    .. attribute:: name

        The translatable name of this :term:`database row`.

    """

    class Meta:
        abstract = True

    name = BabelCharField(max_length=200, verbose_name=_("Designation"))

    def __str__(self):
        return self.get_designation()

    def get_designation(self):
        return settings.SITE.babelattr(self, "name")


class BabelDesignated(model.Model):
    """
    Mixin for models that have a babel field "Designation" (i.e. one
    designation for each language defined in the site's
    :attr:`languages <lino.core.site.Site.languages>`.

    This is the same as :class:`BabelNamed` but the internal field
    name matches the label.

    .. attribute:: designation

        The translatable name of this :term:`database row`.


    """

    class Meta:
        abstract = True

    designation = BabelCharField(max_length=200, verbose_name=_("Designation"))

    def __str__(self):
        return self.get_designation()

    def get_designation(self):
        return settings.SITE.babelattr(self, "designation")
