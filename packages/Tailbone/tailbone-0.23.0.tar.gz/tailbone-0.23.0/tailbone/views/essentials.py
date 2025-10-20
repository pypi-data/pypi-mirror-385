# -*- coding: utf-8; -*-
################################################################################
#
#  Rattail -- Retail Software Framework
#  Copyright © 2010-2023 Lance Edgar
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
Essential views for convenient includes
"""


def defaults(config, **kwargs):
    mod = lambda spec: kwargs.get(spec, spec)

    config.include(mod('tailbone.views.auth'))
    config.include(mod('tailbone.views.common'))
    config.include(mod('tailbone.views.datasync'))
    config.include(mod('tailbone.views.email'))
    config.include(mod('tailbone.views.importing'))
    config.include(mod('tailbone.views.luigi'))
    config.include(mod('tailbone.views.menus'))
    config.include(mod('tailbone.views.people'))
    config.include(mod('tailbone.views.permissions'))
    config.include(mod('tailbone.views.progress'))
    config.include(mod('tailbone.views.reports'))
    config.include(mod('tailbone.views.roles'))
    config.include(mod('tailbone.views.settings'))
    config.include(mod('tailbone.views.tables'))
    config.include(mod('tailbone.views.upgrades'))
    config.include(mod('tailbone.views.users'))
    config.include(mod('tailbone.views.views'))

    # include project views by default, but let caller avoid that by
    # passing False
    projects = kwargs.get('tailbone.views.projects', True)
    if projects:
        if projects is True:
            projects = 'tailbone.views.projects'
        config.include(projects)


def includeme(config):
    defaults(config)
