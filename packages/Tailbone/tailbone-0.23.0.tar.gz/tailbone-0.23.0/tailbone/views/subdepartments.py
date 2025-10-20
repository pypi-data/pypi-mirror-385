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
Subdepartment Views
"""

import sqlalchemy as sa

from rattail.db import model

from deform import widget as dfwidget

from tailbone.db import Session
from tailbone.views import MasterView


class SubdepartmentView(MasterView):
    """
    Master view for the Subdepartment class.
    """
    model_class = model.Subdepartment
    supports_autocomplete = True
    touchable = True
    results_downloadable = True
    has_versions = True

    grid_columns = [
        'number',
        'name',
        'department',
    ]

    form_fields = [
        'number',
        'name',
        'department',
    ]

    mergeable = True
    merge_additive_fields = [
        'product_count',
    ]
    merge_fields = merge_additive_fields + [
        'uuid',
        'number',
        'name',
        'department_number',
    ]

    has_rows = True
    model_row_class = model.Product

    row_labels = {
        'upc': "UPC",
    }

    row_grid_columns = [
        'upc',
        'brand',
        'description',
        'size',
        'vendor',
        'regular_price',
        'current_price',
    ]

    def configure_grid(self, g):
        super(SubdepartmentView, self).configure_grid(g)

        # number
        g.set_link('number')

        # name
        g.filters['name'].default_active = True
        g.filters['name'].default_verb = 'contains'
        g.set_sort_defaults('name')

        # department (name)
        g.set_joiner('department', lambda q: q.outerjoin(model.Department))
        g.set_sorter('department', model.Department.name)
        g.set_filter('department', model.Department.name)

        g.set_link('name')

    def configure_form(self, f):
        super(SubdepartmentView, self).configure_form(f)
        f.remove_field('products')

        # department
        if self.creating or self.editing:
            if 'department' in f.fields:
                f.replace('department', 'department_uuid')
                departments = self.get_departments()
                dept_values = [(d.uuid, "{} {}".format(d.number, d.name))
                               for d in departments]
                require_department = False
                if not require_department:
                    dept_values.insert(0, ('', "(none)"))
                f.set_widget('department_uuid',
                             dfwidget.SelectWidget(values=dept_values))
                f.set_label('department_uuid', "Department")
        else:
            f.set_readonly('department')
            f.set_renderer('department', self.render_department)

    def get_departments(self):
        """
        Returns the list of departments to be exposed in a drop-down.
        """
        model = self.model
        return self.Session.query(model.Department)\
                           .filter(sa.or_(
                               model.Department.product == True,
                               model.Department.product == None))\
                           .order_by(model.Department.name)\
                           .all()

    def get_merge_data(self, subdept):
        return {
            'uuid': subdept.uuid,
            'number': subdept.number,
            'name': subdept.name,
            'department_number': subdept.department.number if subdept.department else None,
            'product_count': len(subdept.products),
        }

    def merge_objects(self, removing, keeping):

        # merge products
        for product in removing.products:
            product.subdepartment = keeping

        Session.delete(removing)

    def get_row_data(self, subdepartment):
        return self.Session.query(model.Product)\
                           .filter(model.Product.subdepartment == subdepartment)

    def get_parent(self, product):
        return product.subdepartment

    def configure_row_grid(self, g):
        super(SubdepartmentView, self).configure_row_grid(g)

        app = self.get_rattail_app()
        self.handler = app.get_products_handler()
        g.set_renderer('regular_price', self.render_price)
        g.set_renderer('current_price', self.render_price)

        g.set_sort_defaults('upc')

    def render_price(self, product, field):
        if not product.not_for_sale:
            price = product[field]
            if price:
                return self.handler.render_price(price)

    def row_view_action_url(self, product, i):
        return self.request.route_url('products.view', uuid=product.uuid)


# TODO: deprecate / remove this
SubdepartmentsView = SubdepartmentView


def defaults(config, **kwargs):
    base = globals()

    SubdepartmentView = kwargs.get('SubdepartmentView', base['SubdepartmentView'])
    SubdepartmentView.defaults(config)


def includeme(config):
    defaults(config)
