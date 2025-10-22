# -*- coding: UTF-8 -*-
# Copyright 2009-2025 Rumma & Ko Ltd
# License: GNU Affero General Public License v3 (see file COPYING for details)

import os
import warnings

from django.conf import settings

from lino import logger
from lino.utils import curry
# from .actions import Action

from lino.core.permissions import (
    make_permission_handler,
    make_static_permission_handler,
)


class BoundAction:
    """An action that is bound to an actor.  If an actor has subclasses,
    each subclass "inherits" its actions.

    """
    help_text = None  # install_help_text() tests if hasattr(fld, "help_text")
    # _started = False

    def __init__(self, actor, action):
        # the following test would require us to import Action, which
        # would trigger a circular import Action -> BoundAction ->
        # BaseRequest -> InstanceAction -> Action
        # if not isinstance(action, Action):
        #     raise Exception("%s : %r is not an Action" % (actor, action))
        self.action = action
        self.actor = actor

        # take care of not accidentally modifying ther actor's
        # requirements!
        required = set(action.get_required_roles(actor))
        # required = set(actor.required_roles)
        # if action.defining_actor is None:
        #     required = set(actor.required_roles)
        # else:
        #     required = set(action.defining_actor.required_roles)
        # required = set()
        # required |= actor.required_roles
        required |= action.required_roles

        # Needed by WrappedAction. Useful for debugging.
        self.required = required

        debug_permissions = actor.debug_permissions and action.debug_permissions

        if debug_permissions:
            if settings.DEBUG:
                logger.info(
                    "debug_permissions active for %r (required=%s)", self, required
                )
            else:
                raise Exception(
                    "settings.DEBUG is False, but `debug_permissions` "
                    "for %r (required=%s) is active (settings=%s)."
                    % (self, required, os.environ["DJANGO_SETTINGS_MODULE"])
                )

        self.allow_view = curry(
            make_static_permission_handler(
                self, action.readonly, debug_permissions, required
            ),
            action,
        )
        self._allow = curry(
            make_permission_handler(
                action, actor, action.readonly, debug_permissions, required
            ),
            action,
        )
        # allowed_states=action.required_states), action)
        # ~ if debug_permissions:
        # ~ logger.info("20130424 _allow is %s",self._allow)
        # ~ actor.actions.define(a.action_name,ba)

    # def __setattr__(self, name, value):
    #     if name == "help_text" and self.action.action_name == 'update_guests':
    #         old = getattr(self, name, None)
    #         if value is None and old is not None:
    #             raise Exception(f"20250622 set to None {hash(self)} {name} was {old}")
    #     super().__setattr__(name, value)

    # @property
    # def help_text(self):
    #     return self.action.get_help_text(self)

    def get_window_layout(self):
        return self.action.get_window_layout(self.actor)

    def get_layout_handel(self):
        if (layout := self.get_window_layout()) is not None:
            try:
                return layout.get_layout_handle()
            except Exception as e:
                raise Exception(
                    f"20250523 get_layout_handle for {self} failed ({e})")

    def get_window_size(self):
        return self.action.get_window_size(self.actor)

    def get_help_text(self):
        return self.help_text

    def full_name(self):
        return self.action.full_name(self.actor)

    def create_request(self, *args, **kw):
        # print("20170116 BoundAction.create_request()", args, kw)
        kw.update(action=self)
        return self.actor.create_request(*args, **kw)

    def request(self, *args, **kwargs):
        """
        Old name for :meth:`create_request`. Still does the same but with a
        deprecation warning.
        """
        warnings.warn(
            "Please call create_request() instead of request()", DeprecationWarning)
        return self.create_request(*args, **kwargs)

    def request_from(self, ar, *args, **kw):
        """Create a request of this action from parent request `ar`."""
        kw.update(parent=ar)
        return self.create_request(*args, **kw)

    def run_from_session(self, ses, **kw):
        ar = self.request_from(ses, **kw)
        self.action.run_from_code(ar)
        return ar.response

    def get_button_label(self, *args):
        return self.action.get_button_label(self.actor, *args)

    def setup_action_request(self, *args):
        return self.action.setup_action_request(self.actor, *args)

    def get_row_permission(self, ar, obj, state):
        """Checks whether this bound action has permission to run on the given
        database object.

        This will check requirements specified on the *actor*, which
        by default checks those defined on the *model*, which in turn
        checks those defined on the *action* by calling
        :meth:`get_bound_action_permission`.

        """
        # ~ if self.actor is None: return False
        return self.actor.get_row_permission(obj, ar, state, self)

    def get_bound_action_permission(self, ar, obj=None, state=None):
        """Checks whether the bound action gives permission to run.

        If this is a list action, `obj` is None.  If this is a row
        action, then `obj` is the current row.

        Note that this method does not (again) call any custom permission
        handler defined on the model.

        This is done in two steps: first we check the requirements
        specified in `required_roles` and `required_states`, then (if
        these pass) we check any custom permissions defined on the
        action via :meth:`get_action_permission
        <lino.core.actions.Action.get_action_permission>`.

        The order of these is important since a custom permission
        handler of an action with default `required_roles` can make
        database queries based on `ar.get_user()`, which would cause
        errors like :message:`Cannot assign
        "<lino.core.auth.utils.AnonymousUser object at
        0x7f562512f210>": "Upload.user" must be a "User" instance`
        when called by anonymous.

        """
        u = ar.get_user()

        if not self.action.get_action_view_permission(self.actor, u.user_type):
            return False
        if not self._allow(u, obj, state):
            return False
        if obj is not None or not self.action.select_rows:
            if not self.action.get_action_permission(ar, obj, state):
                return False
        return True
        # return self._allow(ar.get_user(), obj, state)

    def get_view_permission(self, user_type):
        """
        Return True if this bound action is visible for users of this
        user_type.
        """
        if not self.actor.get_view_permission(user_type):
            return False
        # # 20170902
        # if self.action.defining_actor is None:
        #     if not self.actor.get_view_permission(user_type):
        #         return False
        # elif not self.action.defining_actor.get_view_permission(user_type):
        #     return False
        if not self.action.get_action_view_permission(self.actor, user_type):
            return False
        return self.allow_view(user_type)

    def __repr__(self):
        return "<%s(%s, %r)>" % (self.__class__.__name__, self.actor, self.action)

    def __str__(self):
        return f"{self.action.__class__.__name__} on {self.actor}"
