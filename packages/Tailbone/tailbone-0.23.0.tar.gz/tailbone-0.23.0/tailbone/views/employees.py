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
Employee Views
"""

import sqlalchemy as sa

from rattail.db import model

import colander
from deform import widget as dfwidget
from webhelpers2.html import tags, HTML

from tailbone import grids
from tailbone.views import MasterView


class EmployeeView(MasterView):
    """
    Master view for the Employee class.
    """
    model_class = model.Employee
    has_versions = True
    touchable = True
    supports_autocomplete = True
    results_downloadable = True
    configurable = True

    labels = {
        'id': "ID",
        'display_name': "Short Name",
        'phone': "Phone Number",
    }

    grid_columns = [
        'id',
        'first_name',
        'last_name',
        'phone',
        'email',
        'status',
        'username',
    ]

    form_fields = [
        'person',
        'first_name',
        'last_name',
        'display_name',
        'phone',
        'email',
        'status',
        'full_time',
        'full_time_start',
        'id',
        'users',
        'stores',
        'departments',
    ]

    def should_expose_quickie_search(self):
        if self.expose_quickie_search:
            return True
        app = self.get_rattail_app()
        return app.get_people_handler().should_expose_quickie_search()

    def get_quickie_perm(self):
        return 'people.quickie'

    def get_quickie_url(self):
        return self.request.route_url('people.quickie')

    def get_quickie_placeholder(self):
        app = self.get_rattail_app()
        return app.get_people_handler().get_quickie_search_placeholder()

    def configure_grid(self, g):
        super().configure_grid(g)
        route_prefix = self.get_route_prefix()

        # phone
        g.set_joiner('phone', lambda q: q.outerjoin(model.EmployeePhoneNumber, sa.and_(
            model.EmployeePhoneNumber.parent_uuid == model.Employee.uuid,
            model.EmployeePhoneNumber.preference == 1)))
        g.set_filter('phone', model.EmployeePhoneNumber.number,
                     label="Phone Number",
                     factory=grids.filters.AlchemyPhoneNumberFilter)
        g.set_sorter('phone', model.EmployeePhoneNumber.number)

        # email
        g.joiners['email'] = lambda q: q.outerjoin(model.EmployeeEmailAddress, sa.and_(
            model.EmployeeEmailAddress.parent_uuid == model.Employee.uuid,
            model.EmployeeEmailAddress.preference == 1))
        g.filters['email'] = g.make_filter('email', model.EmployeeEmailAddress.address,
                                           label="Email Address")

        # first_name
        g.set_link('first_name')
        g.set_sorter('first_name', model.Person.first_name)
        g.set_sort_defaults('first_name')
        g.set_filter('first_name', model.Person.first_name,
                     default_active=True,
                     default_verb='contains')

        # last_name
        g.set_link('last_name')
        g.set_sorter('last_name', model.Person.last_name)
        g.set_filter('last_name', model.Person.last_name,
                     default_active=True,
                     default_verb='contains')

        # username
        if self.request.has_perm('users.view'):
            g.set_joiner('username', lambda q: q.outerjoin(model.User))
            g.set_filter('username', model.User.username)
            g.set_sorter('username', model.User.username)
            g.set_renderer('username', self.grid_render_username)
        else:
            g.remove('username')

        # id
        if self.has_perm('edit'):
            g.set_link('id')
        else:
            g.remove('id')
            del g.filters['id']

        # status
        if self.has_perm('view_all'):
            g.set_enum('status', self.enum.EMPLOYEE_STATUS)
            g.filters['status'].default_active = True
            g.filters['status'].default_verb = 'equal'
            g.filters['status'].default_value = str(self.enum.EMPLOYEE_STATUS_CURRENT)
        else:
            g.remove('status')
            del g.filters['status']

        g.set_sorter('email', model.EmployeeEmailAddress.address)

        g.set_label('email', "Email Address")

        if (self.request.has_perm('people.view_profile')
            and self.should_link_straight_to_profile()):

            # add View Raw action
            url = lambda r, i: self.request.route_url(
                f'{route_prefix}.view', **self.get_action_route_kwargs(r))
            # nb. insert to slot 1, just after normal View action
            g.actions.insert(1, self.make_action('view_raw', url=url, icon='eye'))

    def default_view_url(self):
        if (self.request.has_perm('people.view_profile')
            and self.should_link_straight_to_profile()):
            app = self.get_rattail_app()

            def url(employee, i):
                person = app.get_person(employee)
                if person:
                    return self.request.route_url(
                        'people.view_profile', uuid=person.uuid,
                        _anchor='employee')
                return self.get_action_url('view', employee)

            return url

        return super().default_view_url()

    def should_link_straight_to_profile(self):
        return self.rattail_config.getbool('rattail',
                                           'employees.straight_to_profile',
                                           default=False)

    def query(self, session):
        query = super().query(session)
        query = query.join(model.Person)
        if not self.has_perm('view_all'):
            query = query.filter(model.Employee.status == self.enum.EMPLOYEE_STATUS_CURRENT)
        return query

    def grid_render_username(self, employee, field):
        person = employee.person if employee else None
        if not person:
            return ""
        return ", ".join([u.username for u in person.users])

    def grid_extra_class(self, employee, i):
        if employee.status == self.enum.EMPLOYEE_STATUS_FORMER:
            return 'warning'

    def is_employee_protected(self, employee):
        for user in employee.person.users:
            if self.user_is_protected(user):
                return True
        return False

    def editable_instance(self, employee):
        if self.request.is_root:
            return True
        return not self.is_employee_protected(employee)

    def deletable_instance(self, employee):
        if self.request.is_root:
            return True
        return not self.is_employee_protected(employee)

    def configure_form(self, f):
        super().configure_form(f)
        employee = f.model_instance

        f.set_renderer('person', self.render_person)

        if self.creating or self.editing:
            f.remove('users')
        else:
            f.set_readonly('users')
            f.set_renderer('users', self.render_users)

        f.set_renderer('stores', self.render_stores)
        f.set_label('stores', "Stores") # TODO: should not be necessary
        if self.creating or self.editing:
            stores = self.get_possible_stores().all()
            store_values = [(s.uuid, str(s)) for s in stores]
            f.set_node('stores', colander.SchemaNode(colander.Set()))
            f.set_widget('stores', dfwidget.SelectWidget(multiple=True,
                                                         size=len(stores),
                                                         values=store_values))
            if self.editing:
                f.set_default('stores', [s.uuid for s in employee.stores])

        f.set_renderer('departments', self.render_departments)
        f.set_label('departments', "Departments") # TODO: should not be necessary
        if self.creating or self.editing:
            departments = self.get_possible_departments().all()
            dept_values = [(d.uuid, str(d)) for d in departments]
            f.set_node('departments', colander.SchemaNode(colander.Set()))
            f.set_widget('departments', dfwidget.SelectWidget(multiple=True,
                                                              size=len(departments),
                                                              values=dept_values))
            if self.editing:
                f.set_default('departments', [d.uuid for d in employee.departments])

        f.set_enum('status', self.enum.EMPLOYEE_STATUS)

        f.set_type('full_time_start', 'date_jquery')
        if self.editing:
            # TODO: this should not be needed (association proxy)
            f.set_default('full_time_start', employee.full_time_start)

        f.set_readonly('person')
        f.set_readonly('phone')
        f.set_readonly('email')

        f.set_label('email', "Email Address")

        if not self.viewing:
            f.remove_fields('first_name', 'last_name')

    def objectify(self, form, data=None):
        if data is None:
            data = form.validated
        employee = super().objectify(form, data)
        self.update_stores(employee, data)
        self.update_departments(employee, data)
        return employee

    def update_stores(self, employee, data):
        if 'stores' not in data:
            return
        old_stores = set([s.uuid for s in employee.stores])
        new_stores = data['stores']
        for uuid in new_stores:
            if uuid not in old_stores:
                employee._stores.append(model.EmployeeStore(store_uuid=uuid))
        for uuid in old_stores:
            if uuid not in new_stores:
                store = self.Session.get(model.Store, uuid)
                employee.stores.remove(store)

    def update_departments(self, employee, data):
        if 'departments' not in data:
            return
        old_depts = set([d.uuid for d in employee.departments])
        new_depts = data['departments']
        for uuid in new_depts:
            if uuid not in old_depts:
                employee._departments.append(model.EmployeeDepartment(department_uuid=uuid))
        for uuid in old_depts:
            if uuid not in new_depts:
                dept = self.Session.get(model.Department, uuid)
                employee.departments.remove(dept)

    def get_possible_stores(self):
        return self.Session.query(model.Store)\
                           .order_by(model.Store.name)

    def get_possible_departments(self):
        return self.Session.query(model.Department)\
                           .order_by(model.Department.name)

    def render_person(self, employee, field):
        person = employee.person if employee else None
        if not person:
            return ""
        text = str(person)
        url = self.request.route_url('people.view', uuid=person.uuid)
        return tags.link_to(text, url)

    def render_stores(self, employee, field):
        stores = employee.stores if employee else None
        if not stores:
            return ""
        items = []
        for store in sorted(stores, key=str):
            items.append(HTML.tag('li', c=str(store)))
        return HTML.tag('ul', c=items)

    def render_departments(self, employee, field):
        departments = employee.departments if employee else None
        if not departments:
            return ""
        items = []
        for department in sorted(departments, key=str):
            items.append(HTML.tag('li', c=str(department)))
        return HTML.tag('ul', c=items)

    def touch_instance(self, employee):
        app = self.get_rattail_app()
        employment = app.get_employment_handler()
        employment.touch_employee(self.Session(), employee)

    def get_version_child_classes(self):
        return [
            (model.Person, 'uuid', 'person_uuid'),
            (model.EmployeePhoneNumber, 'parent_uuid'),
            (model.EmployeeEmailAddress, 'parent_uuid'),
            (model.EmployeeStore, 'employee_uuid'),
            (model.EmployeeDepartment, 'employee_uuid'),
        ]

    def configure_get_simple_settings(self):
        return [

            # General
            {'section': 'rattail',
             'option': 'employees.straight_to_profile',
             'type': bool},
        ]

    @classmethod
    def defaults(cls, config):
        cls._defaults(config)
        cls._employee_defaults(config)

    @classmethod
    def _employee_defaults(cls, config):
        permission_prefix = cls.get_permission_prefix()
        model_title = cls.get_model_title()
        model_title_plural = cls.get_model_title_plural()

        # view *all* employees
        config.add_tailbone_permission(permission_prefix,
                                       '{}.view_all'.format(permission_prefix),
                                       "View *all* (not just current) {}".format(model_title_plural))

        # view employee "secrets"
        config.add_tailbone_permission(permission_prefix,
                                       '{}.view_secrets'.format(permission_prefix),
                                       "View \"secrets\" for {} (e.g. login ID, passcode)".format(model_title))


def defaults(config, **kwargs):
    base = globals()

    EmployeeView = kwargs.get('EmployeeView', base['EmployeeView'])
    EmployeeView.defaults(config)


def includeme(config):
    defaults(config)
