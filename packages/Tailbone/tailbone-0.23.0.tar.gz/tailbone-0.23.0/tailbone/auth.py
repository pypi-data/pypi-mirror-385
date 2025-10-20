# -*- coding: utf-8; -*-
################################################################################
#
#  Rattail -- Retail Software Framework
#  Copyright © 2010-2024 Lance Edgar
#
#  This file is part of Rattail.
#
#  Rattail is free software: you can redistribute it and/or modify it under the
#  terms of the GNU General Public License as published by the Free Software
#  Foundation, either version 3 of the License, or (at your option) any later
#  version.
#
#  Rattail is distributed in the hope that it will be useful, but WITHOUT ANY
#  WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
#  FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more
#  details.
#
#  You should have received a copy of the GNU General Public License along with
#  Rattail.  If not, see <http://www.gnu.org/licenses/>.
#
################################################################################
"""
Authentication & Authorization
"""

import logging
import re

from wuttjamaican.util import UNSPECIFIED

from pyramid.security import remember, forget

from wuttaweb.auth import WuttaSecurityPolicy
from tailbone.db import Session


log = logging.getLogger(__name__)


def login_user(request, user, timeout=UNSPECIFIED):
    """
    Perform the steps necessary to login the given user.  Note that this
    returns a ``headers`` dict which you should pass to the redirect.
    """
    config = request.rattail_config
    app = config.get_app()
    user.record_event(app.enum.USER_EVENT_LOGIN)
    headers = remember(request, user.uuid)
    if timeout is UNSPECIFIED:
        timeout = session_timeout_for_user(config, user)
    log.debug("setting session timeout for '{}' to {}".format(user.username, timeout))
    set_session_timeout(request, timeout)
    return headers


def logout_user(request):
    """
    Perform the logout action for the given request.  Note that this returns a
    ``headers`` dict which you should pass to the redirect.
    """
    app = request.rattail_config.get_app()
    user = request.user
    if user:
        user.record_event(app.enum.USER_EVENT_LOGOUT)
    request.session.delete()
    request.session.invalidate()
    headers = forget(request)
    return headers


def session_timeout_for_user(config, user):
    """
    Returns the "max" session timeout for the user, according to roles
    """
    app = config.get_app()
    auth = app.get_auth_handler()

    authenticated = auth.get_role_authenticated(Session())
    roles = user.roles + [authenticated]
    timeouts = [role.session_timeout for role in roles
                if role.session_timeout is not None]

    if timeouts and 0 not in timeouts:
        return max(timeouts)


def set_session_timeout(request, timeout):
    """
    Set the server-side session timeout to the given value.
    """
    request.session['_timeout'] = timeout or None


class TailboneSecurityPolicy(WuttaSecurityPolicy):

    def __init__(self, db_session=None, api_mode=False, **kwargs):
        kwargs['db_session'] = db_session or Session()
        super().__init__(**kwargs)
        self.api_mode = api_mode

    def load_identity(self, request):
        config = request.registry.settings.get('rattail_config')
        app = config.get_app()
        user = None

        if self.api_mode:

            # determine/load user from header token if present
            credentials = request.headers.get('Authorization')
            if credentials:
                match = re.match(r'^Bearer (\S+)$', credentials)
                if match:
                    token = match.group(1)
                    auth = app.get_auth_handler()
                    user = auth.authenticate_user_token(self.db_session, token)

        if not user:

            # fetch user uuid from current session
            uuid = self.session_helper.authenticated_userid(request)
            if not uuid:
                return

            # fetch user object from db
            model = app.model
            user = self.db_session.get(model.User, uuid)
            if not user:
                return

        # this user is responsible for data changes in current request
        self.db_session.set_continuum_user(user)
        return user
