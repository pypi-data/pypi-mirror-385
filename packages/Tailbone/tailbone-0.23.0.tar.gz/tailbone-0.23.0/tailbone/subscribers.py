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
Event Subscribers
"""

import datetime
import logging
import warnings
from collections import OrderedDict

import rattail

import colander
import deform
from pyramid import threadlocal
from webhelpers2.html import tags

from wuttaweb import subscribers as base

import tailbone
from tailbone import helpers
from tailbone.db import Session
from tailbone.config import csrf_header_name, should_expose_websockets
from tailbone.util import get_available_themes, get_global_search_options


log = logging.getLogger(__name__)


def new_request(event, session=None):
    """
    Event hook called when processing a new request.

    This first invokes the upstream hooks:

    * :func:`wuttaweb:wuttaweb.subscribers.new_request()`
    * :func:`wuttaweb:wuttaweb.subscribers.new_request_set_user()`

    It then adds more things to the request object; among them:

    .. attribute:: request.rattail_config

       Reference to the app :term:`config object`.  Note that this
       will be the same as :attr:`wuttaweb:request.wutta_config`.

    .. method:: request.register_component(tagname, classname)

       Function to register a Vue component for use with the app.

       This can be called from wherever a component is defined, and
       then in the base template all registered components will be
       properly loaded.
    """
    request = event.request

    # invoke main upstream logic
    # nb. this sets request.wutta_config
    base.new_request(event)

    config = request.wutta_config
    app = config.get_app()
    auth = app.get_auth_handler()
    session = session or Session()

    # compatibility
    rattail_config = config
    request.rattail_config = rattail_config

    def user_getter(request, db_session=None):
        user = base.default_user_getter(request, db_session=db_session)
        if user:
            # nb. we also assign continuum user to session
            session = db_session or Session()
            session.set_continuum_user(user)
            return user

    # invoke upstream hook to set user
    base.new_request_set_user(event, user_getter=user_getter, db_session=session)

    # assign client IP address to the session, for sake of versioning
    if hasattr(request, 'client_addr'):
        session.continuum_remote_addr = request.client_addr

    # request.register_component()
    def register_component(tagname, classname):
        """
        Register a Vue 3 component, so the base template knows to
        declare it for use within the app (page).
        """
        if not hasattr(request, '_tailbone_registered_components'):
            request._tailbone_registered_components = OrderedDict()

        if tagname in request._tailbone_registered_components:
            log.warning("component with tagname '%s' already registered "
                        "with class '%s' but we are replacing that with "
                        "class '%s'",
                        tagname,
                        request._tailbone_registered_components[tagname],
                        classname)

        request._tailbone_registered_components[tagname] = classname
    request.register_component = register_component


def before_render(event):
    """
    Adds goodies to the global template renderer context.
    """
    # log.debug("before_render: %s", event)

    # invoke upstream logic
    base.before_render(event)

    request = event.get('request') or threadlocal.get_current_request()
    config = request.wutta_config
    app = config.get_app()

    renderer_globals = event

    # overrides
    renderer_globals['h'] = helpers

    # misc.
    renderer_globals['datetime'] = datetime
    renderer_globals['colander'] = colander
    renderer_globals['deform'] = deform
    renderer_globals['csrf_header_name'] = csrf_header_name(config)

    # TODO: deprecate / remove these
    renderer_globals['rattail_app'] = app
    renderer_globals['app_title'] = app.get_title()
    renderer_globals['app_version'] = app.get_version()
    renderer_globals['rattail'] = rattail
    renderer_globals['tailbone'] = tailbone
    renderer_globals['model'] = app.model
    renderer_globals['enum'] = app.enum

    # theme  - we only want do this for classic web app, *not* API
    # TODO: so, clearly we need a better way to distinguish the two
    if 'tailbone.theme' in request.registry.settings:
        renderer_globals['theme'] = request.registry.settings['tailbone.theme']
        # note, this is just a global flag; user still needs permission to see picker
        expose_picker = config.get_bool('tailbone.themes.expose_picker',
                                        default=False)
        renderer_globals['expose_theme_picker'] = expose_picker
        if expose_picker:

            # TODO: should remove 'falafel' option altogether
            available = get_available_themes(config)

            options = [tags.Option(theme, value=theme) for theme in available]
            renderer_globals['theme_picker_options'] = options

        # TODO: ugh, same deal here
        renderer_globals['messaging_enabled'] = config.get_bool('tailbone.messaging.enabled',
                                                                default=False)

        # background color may be set per-request, by some apps
        if hasattr(request, 'background_color') and request.background_color:
            renderer_globals['background_color'] = request.background_color
        else: # otherwise we use the one from config
            renderer_globals['background_color'] = config.get('tailbone.background_color')

        # maybe set custom stylesheet
        css = None
        if request.user:
            css = config.get(f'tailbone.{request.user.uuid}', 'user_css')
            if not css:
                css = config.get(f'tailbone.{request.user.uuid}', 'buefy_css')
                if css:
                    warnings.warn(f"setting 'tailbone.{request.user.uuid}.buefy_css' should be"
                                  f"changed to 'tailbone.{request.user.uuid}.user_css'",
                                  DeprecationWarning)
        renderer_globals['user_css'] = css

        # add global search data for quick access
        renderer_globals['global_search_data'] = get_global_search_options(request)

        # here we globally declare widths for grid filter pseudo-columns
        widths = config.get('tailbone.grids.filters.column_widths')
        if widths:
            widths = widths.split(';')
            if len(widths) < 2:
                widths = None
        if not widths:
            widths = ['15em', '15em']
        renderer_globals['filter_fieldname_width'] = widths[0]
        renderer_globals['filter_verb_width'] = widths[1]

        # declare global support for websockets, or lack thereof
        renderer_globals['expose_websockets'] = should_expose_websockets(config)


def add_inbox_count(event):
    """
    Adds the current user's inbox message count to the global renderer context.

    Note that this is not enabled by default; to turn it on you must do this:

       config.add_subscriber('tailbone.subscribers.add_inbox_count', 'pyramid.events.BeforeRender')
    """
    request = event.get('request') or threadlocal.get_current_request()
    if request.user:
        renderer_globals = event
        app = request.rattail_config.get_app()
        model = app.model
        enum = request.rattail_config.get_enum()
        renderer_globals['inbox_count'] = Session.query(model.Message)\
                                                 .outerjoin(model.MessageRecipient)\
                                                 .filter(model.MessageRecipient.recipient == Session.merge(request.user))\
                                                 .filter(model.MessageRecipient.status == enum.MESSAGE_STATUS_INBOX)\
                                                 .count()


def context_found(event):
    """
    Attach some more goodies to the request object:

    The following is attached to the request:

    * ``get_session_timeout()`` function
    """
    request = event.request

    def get_session_timeout():
        """
        Returns the timeout in effect for the current session
        """
        return request.session.get('_timeout')
    request.get_session_timeout = get_session_timeout


def includeme(config):
    config.add_subscriber(new_request, 'pyramid.events.NewRequest')
    config.add_subscriber(before_render, 'pyramid.events.BeforeRender')
    config.add_subscriber(context_found, 'pyramid.events.ContextFound')
