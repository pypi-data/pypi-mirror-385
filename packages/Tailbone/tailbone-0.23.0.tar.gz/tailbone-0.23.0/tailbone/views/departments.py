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
Department Views
"""

from rattail.db.model import Department, Product

from webhelpers2.html import HTML

from tailbone.views import MasterView


class DepartmentView(MasterView):
    """
    Master view for the Department class.
    """
    model_class = Department
    touchable = True
    has_versions = True
    results_downloadable = True
    supports_autocomplete = True

    grid_columns = [
        'number',
        'name',
        'product',
        'personnel',
        'tax',
        'food_stampable',
        'exempt_from_gross_sales',
    ]

    form_fields = [
        'number',
        'name',
        'product',
        'personnel',
        'tax',
        'food_stampable',
        'exempt_from_gross_sales',
        'default_custorder_discount',
        'allow_product_deletions',
        'employees',
    ]

    has_rows = True
    model_row_class = Product
    rows_title = "Products"

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
        super().configure_grid(g)

        # number
        g.set_sort_defaults('number')
        g.set_link('number')

        # name
        g.filters['name'].default_active = True
        g.filters['name'].default_verb = 'contains'
        g.set_link('name')

        g.set_type('product', 'boolean')
        g.set_type('personnel', 'boolean')

    def configure_form(self, f):
        super().configure_form(f)

        f.remove_field('subdepartments')

        if self.creating or self.editing:
            f.remove('employees')
        else:
            f.set_renderer('employees', self.render_employees)

        f.set_type('product', 'boolean')
        f.set_type('personnel', 'boolean')

        # tax
        if self.creating:
            # TODO: make this editable instead
            f.remove('tax')
        else:
            f.set_renderer('tax', self.render_tax)
            # TODO: make this editable
            f.set_readonly('tax')

        # default_custorder_discount
        f.set_type('default_custorder_discount', 'percent')

    def render_employees(self, department, field):
        route_prefix = self.get_route_prefix()
        permission_prefix = self.get_permission_prefix()

        factory = self.get_grid_factory()
        g = factory(
            self.request,
            key=f'{route_prefix}.employees',
            data=[],
            columns=[
                'first_name',
                'last_name',
            ],
            sortable=True,
            sorters={'first_name': True, 'last_name': True},
        )

        if self.request.has_perm('employees.view'):
            g.actions.append(self.make_action('view', icon='eye'))
        if self.request.has_perm('employees.edit'):
            g.actions.append(self.make_action('edit', icon='edit'))

        return HTML.literal(
            g.render_table_element(data_prop='employeesData'))

    def template_kwargs_view(self, **kwargs):
        kwargs = super().template_kwargs_view(**kwargs)
        department = kwargs['instance']
        department_employees = sorted(department.employees, key=str)

        employees = []
        for employee in department_employees:
            person = employee.person
            employees.append({
                'uuid': employee.uuid,
                'first_name': person.first_name,
                'last_name': person.last_name,
                '_action_url_view': self.request.route_url('employees.view', uuid=employee.uuid),
                '_action_url_edit': self.request.route_url('employees.edit', uuid=employee.uuid),
            })
        kwargs['employees_data'] = employees

        return kwargs

    def before_delete(self, department):
        """
        Check to see if there are any products which belong to the department;
        if there are then we do not allow delete and redirect the user.
        """
        model = self.model
        count = self.Session.query(model.Product)\
                            .filter(model.Product.department == department)\
                            .count()
        if count:
            self.request.session.flash("Will not delete department which still has {} products: {}".format(
                count, department), 'error')
            raise self.redirect(self.get_action_url('view', department))

    def get_row_data(self, department):
        model = self.model
        return self.Session.query(model.Product)\
                           .filter(model.Product.department == department)

    def get_parent(self, product):
        return product.department

    def configure_row_grid(self, g):
        super().configure_row_grid(g)

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

    def list_by_vendor(self):
        """
        View list of departments by vendor
        """
        model = self.model
        data = self.Session.query(model.Department)\
                           .outerjoin(model.Product)\
                           .join(model.ProductCost)\
                           .join(model.Vendor)\
                           .filter(model.Vendor.uuid == self.request.params['uuid'])\
                           .distinct()\
                           .order_by(model.Department.name)

        def normalize(dept):
            return {
                'uuid': dept.uuid,
                'number': dept.number,
                'name': dept.name,
            }

        return self.json_response([normalize(d) for d in data])

    @classmethod
    def defaults(cls, config):
        route_prefix = cls.get_route_prefix()
        url_prefix = cls.get_url_prefix()
        permission_prefix = cls.get_permission_prefix()

        # list by vendor
        config.add_route('{}.by_vendor'.format(route_prefix), '{}/by-vendor'.format(url_prefix))
        config.add_view(cls, attr='list_by_vendor', route_name='{}.by_vendor'.format(route_prefix),
                        permission='{}.list'.format(permission_prefix))

        cls._defaults(config)


def defaults(config, **kwargs):
    base = globals()

    DepartmentView = kwargs.get('DepartmentView', base['DepartmentView'])
    DepartmentView.defaults(config)


def includeme(config):
    defaults(config)
