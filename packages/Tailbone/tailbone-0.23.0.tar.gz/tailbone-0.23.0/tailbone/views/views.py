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
Views for views
"""

import os
import sys

from rattail.db.util import get_fieldnames
from rattail.util import simple_error

import colander
from deform import widget as dfwidget

from tailbone.views import MasterView


class ModelViewView(MasterView):
    """
    Master view for views
    """
    normalized_model_name = 'model_view'
    model_key = 'route_prefix'
    model_title = "Model View"
    url_prefix = '/views/model'
    viewable = True
    creatable = True
    editable = False
    deletable = False
    filterable = False
    pageable = False

    grid_columns = [
        'label',
        'model_name',
        'route_prefix',
        'permission_prefix',
    ]

    def get_data(self, **kwargs):
        """
        Fetch existing model views from app registry
        """
        data = []

        all_views = self.request.registry.settings['tailbone_model_views']
        for model_name in sorted(all_views):
            model_views = all_views[model_name]
            for view in model_views:
                data.append({
                    'model_name': model_name,
                    'label': view['label'],
                    'route_prefix': view['route_prefix'],
                    'permission_prefix': view['permission_prefix'],
                })

        return data

    def configure_grid(self, g):
        super().configure_grid(g)

        # label
        g.sorters['label'] = g.make_simple_sorter('label')
        g.set_sort_defaults('label')
        g.set_link('label')
        g.set_searchable('label')

        # model_name
        g.sorters['model_name'] = g.make_simple_sorter('model_name', foldcase=True)
        g.set_searchable('model_name')

        # route
        g.sorters['route'] = g.make_simple_sorter('route')
        g.set_searchable('route')

        # permission
        g.sorters['permission'] = g.make_simple_sorter('permission')
        g.set_searchable('permission')

    def default_view_url(self):
        return lambda view, i: self.request.route_url(view['route_prefix'])

    def make_form_schema(self):
        return ModelViewSchema()

    def template_kwargs_create(self, **kwargs):
        kwargs = super().template_kwargs_create(**kwargs)
        app = self.get_rattail_app()
        db_handler = app.get_db_handler()

        model_classes = db_handler.get_model_classes()
        kwargs['model_names'] = [cls.__name__ for cls in model_classes]

        pkg = self.rattail_config.get('rattail', 'running_from_source.rootpkg')
        if pkg:
            kwargs['pkgroot'] = pkg
            pkg = sys.modules[pkg]
            pkgdir = os.path.dirname(pkg.__file__)
            kwargs['view_dir'] = os.path.join(pkgdir, 'web', 'views') + os.sep
        else:
            kwargs['pkgroot'] = 'poser'
            kwargs['view_dir'] = '??' + os.sep

        return kwargs

    def write_view_file(self):
        data = self.request.json_body
        path = data['view_file']

        if os.path.exists(path):
            if data['overwrite']:
                os.remove(path)
            else:
                return {'error': "File already exists"}

        app = self.get_rattail_app()
        tb = app.get_tailbone_handler()
        model_class = getattr(self.model, data['model_name'])

        data['model_module_name'] = self.model.__name__
        data['model_title_plural'] = getattr(model_class,
                                             'model_title_plural',
                                             # TODO
                                             model_class.__name__)

        data['model_versioned'] = hasattr(model_class, '__versioned__')

        fieldnames = get_fieldnames(self.rattail_config,
                                                  model_class)
        fieldnames.remove('uuid')
        data['model_fieldnames'] = fieldnames

        tb.write_model_view(data, path)

        return {'ok': True}

    def check_view(self):
        data = self.request.json_body

        try:
            url = self.request.route_url(data['route_prefix'])
        except Exception as error:
            return {'ok': True,
                    'problem': simple_error(error)}

        return {'ok': True, 'url': url}

    @classmethod
    def defaults(cls, config):
        rattail_config = config.registry.settings.get('rattail_config')

        # allow creating views only if *not* production
        if not rattail_config.production():
            cls.creatable = True

        cls._model_view_defaults(config)
        cls._defaults(config)

    @classmethod
    def _model_view_defaults(cls, config):
        route_prefix = cls.get_route_prefix()
        url_prefix = cls.get_url_prefix()
        permission_prefix = cls.get_permission_prefix()

        if cls.creatable:

            # write view class to file
            config.add_route('{}.write_view_file'.format(route_prefix),
                             '{}/write-view-file'.format(url_prefix),
                             request_method='POST')
            config.add_view(cls, attr='write_view_file',
                            route_name='{}.write_view_file'.format(route_prefix),
                            renderer='json',
                            permission='{}.create'.format(permission_prefix))

            # check view
            config.add_route('{}.check_view'.format(route_prefix),
                             '{}/check-view'.format(url_prefix),
                             request_method='POST')
            config.add_view(cls, attr='check_view',
                            route_name='{}.check_view'.format(route_prefix),
                            renderer='json',
                            permission='{}.create'.format(permission_prefix))


class ModelViewSchema(colander.Schema):

    model_name = colander.SchemaNode(colander.String())


def defaults(config, **kwargs):
    base = globals()

    ModelViewView = kwargs.get('ModelViewView', base['ModelViewView'])
    ModelViewView.defaults(config)


def includeme(config):
    defaults(config)
