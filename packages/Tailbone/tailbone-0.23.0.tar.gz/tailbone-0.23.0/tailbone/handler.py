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
Tailbone Handler
"""

import warnings

from mako.lookup import TemplateLookup

from rattail.app import GenericHandler
from rattail.files import resource_path

from tailbone.providers import get_all_providers


class TailboneHandler(GenericHandler):
    """
    Base class and default implementation for Tailbone handler.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # TODO: make templates dir configurable?
        templates = [resource_path('rattail:templates/web')]
        self.templates = TemplateLookup(directories=templates)

    def get_menu_handler(self, **kwargs):
        """
        DEPRECATED; use
        :meth:`wuttaweb.handler.WebHandler.get_menu_handler()`
        instead.
        """
        warnings.warn("TailboneHandler.get_menu_handler() is deprecated; "
                      "please use WebHandler.get_menu_handler() instead",
                      DeprecationWarning, stacklevel=2)

        if not hasattr(self, 'menu_handler'):
            spec = self.config.get('tailbone.menus', 'handler',
                                   default='tailbone.menus:MenuHandler')
            Handler = self.app.load_object(spec)
            self.menu_handler = Handler(self.config)
            self.menu_handler.tb = self
        return self.menu_handler

    def iter_providers(self):
        """
        Returns an iterator over all registered Tailbone providers.
        """
        providers = get_all_providers(self.config)
        return providers.values()

    def write_model_view(self, data, path, **kwargs):
        """
        Write code for a new model view, based on the given data dict,
        to the given path.
        """
        template = self.templates.get_template('/new-model-view.mako')
        content = template.render(**data)
        with open(path, 'wt') as f:
            f.write(content)
