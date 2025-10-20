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
Views with info about the underlying Rattail tables
"""

import os
import sys
import warnings

import sqlalchemy as sa
from sqlalchemy_utils import get_mapper

from rattail.util import simple_error

import colander
from deform import widget as dfwidget
from webhelpers2.html import HTML

from tailbone.views import MasterView


class TableView(MasterView):
    """
    Master view for tables
    """
    normalized_model_name = 'table'
    model_key = 'table_name'
    model_title = "Table"
    creatable = False
    editable = False
    deletable = False
    filterable = False
    pageable = False

    labels = {
        'branch_name': "Schema Branch",
        'model_name': "Model Class",
        'module_name': "Module",
        'module_file': "File",
    }

    grid_columns = [
        'table_name',
        'row_count',
    ]

    has_rows = True
    rows_title = "Columns"
    rows_pageable = False
    rows_filterable = False
    rows_viewable = False

    row_grid_columns = [
        'sequence',
        'column_name',
        'data_type',
        'nullable',
        'description',
    ]

    def __init__(self, request):
        super().__init__(request)
        app = self.get_rattail_app()
        self.db_handler = app.get_db_handler()

    def get_data(self, **kwargs):
        """
        Fetch existing table names and estimate row counts via PG SQL
        """
        # note that we only show 'public' schema tables, i.e. avoid the 'batch'
        # schema, at least for now?  maybe should include all, plus show the
        # schema name within the results grid?
        sql = """
        select relname, n_live_tup
        from pg_stat_user_tables
        where schemaname = 'public'
        order by n_live_tup desc;
        """
        result = self.Session.execute(sa.text(sql))
        return [dict(table_name=row.relname, row_count=row.n_live_tup)
                for row in result]

    def configure_grid(self, g):
        super().configure_grid(g)

        # table_name
        g.sorters['table_name'] = g.make_simple_sorter('table_name', foldcase=True)
        g.set_sort_defaults('table_name')
        g.set_searchable('table_name')
        g.set_link('table_name')

        # row_count
        g.sorters['row_count'] = g.make_simple_sorter('row_count')

    def configure_form(self, f):
        super().configure_form(f)

        # TODO: should render this instead, by inspecting table
        if not self.creating:
            f.remove('versioned')

    def get_instance(self):
        model = self.model
        table_name = self.request.matchdict['table_name']

        sql = """
        select n_live_tup
        from pg_stat_user_tables
        where schemaname = 'public' and relname = :table_name
        order by n_live_tup desc;
        """
        result = self.Session.execute(sql, {'table_name': table_name})
        row = result.fetchone()
        if not row:
            raise self.notfound()

        data = {
            'table_name': table_name,
            'row_count': row['n_live_tup'],
        }

        table = model.Base.metadata.tables.get(table_name)
        data['table'] = table
        if table is not None:
            try:
                mapper = get_mapper(table)
            except ValueError:
                pass
            else:
                data['model_name'] = mapper.class_.__name__
                data['model_title'] = mapper.class_.get_model_title()
                data['model_title_plural'] = mapper.class_.get_model_title_plural()
                data['description'] = mapper.class_.__doc__

                # TODO: how to reliably get branch?  must walk all revisions?
                module_parts = mapper.class_.__module__.split('.')
                data['branch_name'] = module_parts[0]

                data['module_name'] = mapper.class_.__module__
                data['module_file'] = sys.modules[mapper.class_.__module__].__file__

        return data

    def get_instance_title(self, table):
        return table['table_name']

    def make_form_schema(self):
        return TableSchema()

    def get_xref_buttons(self, table):
        buttons = super().get_xref_buttons(table)

        if table.get('model_name'):
            all_views = self.request.registry.settings['tailbone_model_views']
            model_views = all_views.get(table['model_name'], [])
            for view in model_views:
                url = self.request.route_url(view['route_prefix'])
                buttons.append(self.make_xref_button(url=url, text=view['label'],
                                                     internal=True))

            if self.request.has_perm('model_views.create'):
                url = self.request.route_url('model_views.create',
                                             _query={'model_name': table['model_name']})
                buttons.append(self.make_button("New View",
                                                is_primary=True,
                                                url=url,
                                                icon_left='plus'))

        return buttons

    def template_kwargs_create(self, **kwargs):
        kwargs = super().template_kwargs_create(**kwargs)
        app = self.get_rattail_app()
        model = self.model

        kwargs['alembic_current_head'] = self.db_handler.check_alembic_current_head()

        kwargs['branch_name_options'] = self.db_handler.get_alembic_branch_names()

        branch_name = app.get_table_prefix()
        if branch_name not in kwargs['branch_name_options']:
            branch_name = None
        kwargs['branch_name'] = branch_name

        kwargs['existing_tables'] = [{'name': table}
                                     for table in sorted(model.Base.metadata.tables)]

        kwargs['model_dir'] = (os.path.dirname(model.__file__)
                               + os.sep)

        return kwargs

    def write_model_file(self):
        data = self.request.json_body
        path = data['module_file']
        model = self.model

        if os.path.exists(path):
            if data['overwrite']:
                os.remove(path)
            else:
                return {'error': "File already exists"}

        for column in data['columns']:
            if column['data_type']['type'] == '_fk_uuid_' and column['relationship']:
                name = column['relationship']

                table = model.Base.metadata.tables[column['data_type']['reference']]
                try:
                    mapper = get_mapper(table)
                except ValueError:
                    reference_model = table.name.capitalize()
                else:
                    reference_model = mapper.class_.__name__

                column['relationship'] = {
                    'name': name,
                    'reference_model': reference_model,
                }

        self.db_handler.write_table_model(data, path)
        return {'ok': True}

    def check_model(self):
        model = self.model
        data = self.request.json_body
        model_name = data['model_name']

        if not hasattr(model, model_name):
            return {'ok': True,
                    'problem': "class not found in primary model contents",
                    'model': self.model.__name__}

        # TODO: probably should inspect closer before assuming ok..?

        return {'ok': True}

    def write_revision_script(self):
        data = self.request.json_body
        script = self.db_handler.generate_revision_script(data['branch'],
                                                          message=data['message'])
        return {'ok': True,
                'script': script.path}

    def upgrade_db(self):
        self.db_handler.upgrade_db()
        return {'ok': True}

    def check_table(self):
        model = self.model
        data = self.request.json_body
        table_name = data['table_name']

        table = model.Base.metadata.tables.get(table_name)
        if table is None:
            return {'ok': True,
                    'problem': "Table does not exist in model metadata!"}

        try:
            count = self.Session.query(table).count()
        except Exception as error:
            return {'ok': True,
                    'problem': simple_error(error)}

        url = self.request.route_url('{}.view'.format(self.get_route_prefix()),
                                     table_name=table_name)
        return {'ok': True, 'url': url}

    def get_row_data(self, table):
        data = []
        for i, column in enumerate(table['table'].columns, 1):
            data.append({
                'column': column,
                'sequence': i,
                'column_name': column.name,
                'data_type': str(repr(column.type)),
                'nullable': column.nullable,
                'description': column.doc,
            })
        return data

    def configure_row_grid(self, g):
        super().configure_row_grid(g)

        g.sorters['sequence'] = g.make_simple_sorter('sequence')
        g.set_sort_defaults('sequence')
        g.set_label('sequence', "Seq.")

        g.sorters['column_name'] = g.make_simple_sorter('column_name',
                                                        foldcase=True)
        g.set_searchable('column_name')

        g.sorters['data_type'] = g.make_simple_sorter('data_type',
                                                      foldcase=True)
        g.set_searchable('data_type')

        g.set_type('nullable', 'boolean')
        g.sorters['nullable'] = g.make_simple_sorter('nullable')

        g.set_renderer('description', self.render_column_description)
        g.set_searchable('description')

    def render_column_description(self, column, field):
        text = column[field]
        if not text:
            return

        max_length = 80

        if len(text) < max_length:
            return text

        return HTML.tag('span', title=text, c="{} ...".format(text[:max_length]))

    def migrations(self):
        # TODO: allow alembic upgrade on POST
        # TODO: pass current revisions to page context
        return self.render_to_response('migrations', {})

    @classmethod
    def defaults(cls, config):
        rattail_config = config.registry.settings.get('rattail_config')

        # allow creating tables only if *not* production
        if not rattail_config.production():
            cls.creatable = True

        cls._table_defaults(config)
        cls._defaults(config)

    @classmethod
    def _table_defaults(cls, config):
        route_prefix = cls.get_route_prefix()
        url_prefix = cls.get_url_prefix()
        permission_prefix = cls.get_permission_prefix()

        # migrations
        config.add_tailbone_permission(permission_prefix,
                                       '{}.migrations'.format(permission_prefix),
                                       "View / apply Alembic migrations")
        config.add_route('{}.migrations'.format(route_prefix),
                         '{}/migrations'.format(url_prefix))
        config.add_view(cls, attr='migrations',
                        route_name='{}.migrations'.format(route_prefix),
                        renderer='json',
                        permission='{}.migrations'.format(permission_prefix))

        if cls.creatable:

            # write model class to file
            config.add_route('{}.write_model_file'.format(route_prefix),
                             '{}/write-model-file'.format(url_prefix),
                             request_method='POST')
            config.add_view(cls, attr='write_model_file',
                            route_name='{}.write_model_file'.format(route_prefix),
                            renderer='json',
                            permission='{}.create'.format(permission_prefix))

            # check model
            config.add_route('{}.check_model'.format(route_prefix),
                             '{}/check-model'.format(url_prefix),
                             request_method='POST')
            config.add_view(cls, attr='check_model',
                            route_name='{}.check_model'.format(route_prefix),
                            renderer='json',
                            permission='{}.create'.format(permission_prefix))

            # generate revision script
            config.add_route('{}.write_revision_script'.format(route_prefix),
                             '{}/write-revision-script'.format(url_prefix),
                             request_method='POST')
            config.add_view(cls, attr='write_revision_script',
                            route_name='{}.write_revision_script'.format(route_prefix),
                            renderer='json',
                            permission='{}.create'.format(permission_prefix))

            # upgrade db
            config.add_route('{}.upgrade_db'.format(route_prefix),
                             '{}/upgrade-db'.format(url_prefix),
                             request_method='POST')
            config.add_view(cls, attr='upgrade_db',
                            route_name='{}.upgrade_db'.format(route_prefix),
                            renderer='json',
                            permission='{}.create'.format(permission_prefix))

            # check table
            config.add_route('{}.check_table'.format(route_prefix),
                             '{}/check-table'.format(url_prefix),
                             request_method='POST')
            config.add_view(cls, attr='check_table',
                            route_name='{}.check_table'.format(route_prefix),
                            renderer='json',
                            permission='{}.create'.format(permission_prefix))


class TablesView(TableView):

    def __init__(self, request):
        warnings.warn("TablesView is deprecated; please use TableView instead",
                      DeprecationWarning, stacklevel=2)
        super().__init__(request)


class TableSchema(colander.Schema):

    table_name = colander.SchemaNode(colander.String())

    row_count = colander.SchemaNode(colander.Integer(),
                                    missing=colander.null)

    model_name = colander.SchemaNode(colander.String())

    model_title = colander.SchemaNode(colander.String())

    model_title_plural = colander.SchemaNode(colander.String())

    description = colander.SchemaNode(colander.String())

    branch_name = colander.SchemaNode(colander.String())

    module_name = colander.SchemaNode(colander.String(),
                                      missing=colander.null)

    module_file = colander.SchemaNode(colander.String(),
                                      missing=colander.null)

    versioned = colander.SchemaNode(colander.Bool())


def defaults(config, **kwargs):
    base = globals()

    TableView = kwargs.get('TableView', base['TableView'])
    TableView.defaults(config)


def includeme(config):
    defaults(config)
