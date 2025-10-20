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
Base class for Config Views
"""

import json

import sqlalchemy as sa

from tailbone.views import View
from tailbone.db import Session


class MenuConfigView(View):
    """
    View for configuring the main menu.
    """

    def configure(self):
        """
        Main entry point to menu config views.
        """
        if self.request.method == 'POST':
            if self.request.POST.get('remove_settings'):
                self.configure_remove_settings()
                self.request.session.flash("All settings for Menus have been removed.",
                                           'warning')
                return self.redirect(self.request.current_route_url())
            else:
                data = self.request.POST

                # gather/save settings
                settings = self.configure_gather_settings(data)
                self.configure_remove_settings()
                self.configure_save_settings(settings)
                self.request.session.flash("Settings have been saved.")
                return self.redirect(self.request.current_route_url())

        context = {
            'config_title': "Menus",
            'index_title': "App Details",
            'index_url': self.request.route_url('appinfo'),
        }

        possible_index_options = sorted(
            self.request.registry.settings['tailbone_index_pages'],
            key=lambda p: p['label'])

        index_options = []
        for option in possible_index_options:
            perm = option['permission']
            option['perm'] = perm
            option['url'] = self.request.route_url(option['route'])
            index_options.append(option)

        context['index_route_options'] = index_options
        return context

    def configure_gather_settings(self, data):
        app = self.get_rattail_app()
        web = app.get_web_handler()
        menus = web.get_menu_handler()

        settings = [{'name': 'tailbone.menu.from_settings',
                     'value': 'true'}]

        main_keys = []
        for topitem in json.loads(data['menus']):
            key = menus._make_menu_key(self.rattail_config, topitem['title'])
            main_keys.append(key)

            settings.extend([
                {'name': 'tailbone.menu.menu.{}.label'.format(key),
                 'value': topitem['title']},
            ])

            item_keys = []
            for item in topitem['items']:
                item_type = item.get('type', 'item')
                if item_type == 'item':
                    if item.get('route'):
                        item_key = item['route']
                    else:
                        item_key = menus._make_menu_key(self.rattail_config, item['title'])
                    item_keys.append(item_key)

                    settings.extend([
                        {'name': 'tailbone.menu.menu.{}.item.{}.label'.format(key, item_key),
                         'value': item['title']},
                    ])

                    if item.get('route'):
                        settings.extend([
                            {'name': 'tailbone.menu.menu.{}.item.{}.route'.format(key, item_key),
                             'value': item['route']},
                        ])

                    elif item.get('url'):
                        settings.extend([
                            {'name': 'tailbone.menu.menu.{}.item.{}.url'.format(key, item_key),
                             'value': item['url']},
                        ])

                    if item.get('perm'):
                        settings.extend([
                            {'name': 'tailbone.menu.menu.{}.item.{}.perm'.format(key, item_key),
                             'value': item['perm']},
                        ])

                elif item_type == 'sep':
                    item_keys.append('SEP')

            settings.extend([
                {'name': 'tailbone.menu.menu.{}.items'.format(key),
                 'value': ' '.join(item_keys)},
            ])

        settings.append({'name': 'tailbone.menu.menus',
                         'value': ' '.join(main_keys)})
        return settings

    def configure_remove_settings(self):
        model = self.model
        Session.query(model.Setting)\
               .filter(sa.or_(
                   model.Setting.name == 'tailbone.menu.from_settings',
                   model.Setting.name == 'tailbone.menu.menus',
                   model.Setting.name.like('tailbone.menu.menu.%.label'),
                   model.Setting.name.like('tailbone.menu.menu.%.items'),
                   model.Setting.name.like('tailbone.menu.menu.%.item.%.label'),
                   model.Setting.name.like('tailbone.menu.menu.%.item.%.route'),
                   model.Setting.name.like('tailbone.menu.menu.%.item.%.perm'),
                   model.Setting.name.like('tailbone.menu.menu.%.item.%.url')))\
               .delete(synchronize_session=False)

    def configure_save_settings(self, settings):
        model = self.model
        session = Session()
        for setting in settings:
            session.add(model.Setting(name=setting['name'],
                                      value=setting['value']))

    @classmethod
    def defaults(cls, config):
        cls._defaults(config)

    @classmethod
    def _defaults(cls, config):

        # configure menus
        config.add_route('configure_menus',
                         '/configure-menus')
        config.add_view(cls, attr='configure',
                        route_name='configure_menus',
                        permission='appinfo.configure',
                        renderer='/configure-menus.mako')
        config.add_tailbone_config_page('configure_menus', "Menus", 'admin')


def defaults(config, **kwargs):
    base = globals()

    MenuConfigView = kwargs.get('MenuConfigView', base['MenuConfigView'])
    MenuConfigView.defaults(config)


def includeme(config):
    defaults(config)
