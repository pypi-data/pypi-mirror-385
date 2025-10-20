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
Tailbone Web API
"""

import simplejson

from cornice.renderer import CorniceRenderer
from pyramid.config import Configurator

from tailbone import app
from tailbone.auth import TailboneSecurityPolicy
from tailbone.providers import get_all_providers


def make_rattail_config(settings):
    """
    Make a Rattail config object from the given settings.
    """
    rattail_config = app.make_rattail_config(settings)
    return rattail_config


def make_pyramid_config(settings):
    """
    Make a Pyramid config object from the given settings.
    """
    rattail_config = settings['rattail_config']
    pyramid_config = Configurator(settings=settings, root_factory=app.Root)

    # configure user authorization / authentication
    pyramid_config.set_security_policy(TailboneSecurityPolicy(api_mode=True))

    # always require CSRF token protection
    pyramid_config.set_default_csrf_options(require_csrf=True,
                                            token='_csrf',
                                            header='X-XSRF-TOKEN')

    # bring in some Pyramid goodies
    pyramid_config.include('tailbone.beaker')
    pyramid_config.include('pyramid_tm')
    pyramid_config.include('cornice')

    # use simplejson to serialize cornice view context; cf.
    # https://cornice.readthedocs.io/en/latest/upgrading.html#x-to-5-x
    # https://docs.pylonsproject.org/projects/pyramid/en/latest/narr/renderers.html
    json_renderer = CorniceRenderer(serializer=simplejson.dumps)
    pyramid_config.add_renderer('cornicejson', json_renderer)

    # bring in the pyramid_retry logic, if available
    # TODO: pretty soon we can require this package, hopefully..
    try:
        import pyramid_retry
    except ImportError:
        pass
    else:
        pyramid_config.include('pyramid_retry')

    # fetch all tailbone providers
    providers = get_all_providers(rattail_config)
    for provider in providers.values():

        # configure DB sessions associated with transaction manager
        provider.configure_db_sessions(rattail_config, pyramid_config)

    # add some permissions magic
    pyramid_config.add_directive('add_wutta_permission_group',
                                 'wuttaweb.auth.add_permission_group')
    pyramid_config.add_directive('add_wutta_permission',
                                 'wuttaweb.auth.add_permission')
    # TODO: deprecate / remove these
    pyramid_config.add_directive('add_tailbone_permission_group',
                                 'wuttaweb.auth.add_permission_group')
    pyramid_config.add_directive('add_tailbone_permission',
                                 'wuttaweb.auth.add_permission')

    return pyramid_config


def main(global_config, views='tailbone.api', **settings):
    """
    This function returns a Pyramid WSGI application.
    """
    rattail_config = make_rattail_config(settings)
    pyramid_config = make_pyramid_config(settings)

    # event hooks
    pyramid_config.add_subscriber('tailbone.subscribers.new_request',
                                  'pyramid.events.NewRequest')
    # TODO: is this really needed?
    pyramid_config.add_subscriber('tailbone.subscribers.context_found',
                                  'pyramid.events.ContextFound')

    # views
    pyramid_config.include(views)

    return pyramid_config.make_wsgi_app()
