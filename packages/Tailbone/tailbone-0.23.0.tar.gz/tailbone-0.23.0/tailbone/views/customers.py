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
Customer Views
"""

from collections import OrderedDict

import sqlalchemy as sa
from sqlalchemy import orm

import colander
from pyramid.httpexceptions import HTTPNotFound
from webhelpers2.html import HTML, tags

from tailbone import grids
from tailbone.db import Session
from tailbone.views import MasterView

from rattail.db.model import Customer, CustomerShopper, PendingCustomer


class CustomerView(MasterView):
    """
    Master view for the Customer class.
    """
    model_class = Customer
    is_contact = True
    has_versions = True
    results_downloadable = True
    people_detachable = True
    touchable = True
    supports_autocomplete = True
    configurable = True

    # whether to show "view full profile" helper for customer view
    show_profiles_helper = True

    labels = {
        'id': "ID",
        'name': "Account Name",
        'default_phone': "Phone Number",
        'default_email': "Email Address",
        'default_address': "Physical Address",
        'active_in_pos': "Active in POS",
        'active_in_pos_sticky': "Always Active in POS",
    }

    grid_columns = [
        '_customer_key_',
        'name',
        'phone',
        'email',
    ]

    form_fields = [
        '_customer_key_',
        'name',
        'account_holder',
        'default_phone',
        'default_address',
        'address_street',
        'address_street2',
        'address_city',
        'address_state',
        'address_zipcode',
        'default_email',
        'email_preference',
        'wholesale',
        'active_in_pos',
        'active_in_pos_sticky',
        'shoppers',
        'people',
        'groups',
        'members',
    ]

    mergeable = True

    merge_coalesce_fields = [
        'email_addresses',
        'phone_numbers',
    ]

    merge_fields = merge_coalesce_fields + [
        'uuid',
        'name',
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

    def get_expose_active_in_pos(self):
        if not hasattr(self, '_expose_active_in_pos'):
            self._expose_active_in_pos = self.rattail_config.getbool(
                'rattail', 'customers.active_in_pos',
                default=False)
        return self._expose_active_in_pos

    # TODO: this is duplicated in people view module
    def should_expose_shoppers(self):
        return self.rattail_config.getbool('rattail',
                                           'customers.expose_shoppers',
                                           default=True)

    # TODO: this is duplicated in people view module
    def should_expose_people(self):
        return self.rattail_config.getbool('rattail',
                                           'customers.expose_people',
                                           default=True)

    def query(self, session):
        query = super().query(session)
        app = self.get_rattail_app()
        model = self.model
        query = query.outerjoin(model.Person,
                                model.Person.uuid == model.Customer.account_holder_uuid)
        return query

    def configure_grid(self, g):
        super().configure_grid(g)
        app = self.get_rattail_app()
        model = self.model
        route_prefix = self.get_route_prefix()

        # customer key
        field = self.get_customer_key_field()
        g.filters[field].default_active = True
        g.filters[field].default_verb = 'equal'
        g.set_sort_defaults(field)
        g.set_link(field)

        # name
        g.filters['name'].default_active = True
        g.filters['name'].default_verb = 'contains'

        # phone
        g.set_label('phone', "Phone Number")
        g.set_joiner('phone', lambda q: q.outerjoin(model.CustomerPhoneNumber, sa.and_(
            model.CustomerPhoneNumber.parent_uuid == model.Customer.uuid,
            model.CustomerPhoneNumber.preference == 1)))
        g.set_sorter('phone', model.CustomerPhoneNumber.number)
        g.set_filter('phone', model.CustomerPhoneNumber.number,
                     # label="Phone Number",
                     factory=grids.filters.AlchemyPhoneNumberFilter)

        # email
        g.set_label('email', "Email Address")
        g.set_joiner('email', lambda q: q.outerjoin(model.CustomerEmailAddress, sa.and_(
            model.CustomerEmailAddress.parent_uuid == model.Customer.uuid,
            model.CustomerEmailAddress.preference == 1)))
        g.set_sorter('email', model.CustomerEmailAddress.address)
        g.set_filter('email', model.CustomerEmailAddress.address)#, label="Email Address")

        # email_preference
        g.set_enum('email_preference', self.enum.EMAIL_PREFERENCE)

        # account_holder_*_name
        g.set_filter('account_holder_first_name', model.Person.first_name)
        g.set_filter('account_holder_last_name', model.Person.last_name)

        # person
        g.set_renderer('person', self.grid_render_person)
        g.set_sorter('person', model.Person.display_name)

        # active_in_pos
        if self.get_expose_active_in_pos():
            g.filters['active_in_pos'].default_active = True
            g.filters['active_in_pos'].default_verb = 'is_true'

        if (self.request.has_perm('people.view_profile')
            and self.should_link_straight_to_profile()):

            # add View Raw action
            url = lambda r, i: self.request.route_url(
                f'{route_prefix}.view', **self.get_action_route_kwargs(r))
            # nb. insert to slot 1, just after normal View action
            g.actions.insert(1, self.make_action('view_raw', url=url, icon='eye'))

        g.set_link('name')
        g.set_link('person')
        g.set_link('email')

    def default_view_url(self):
        if (self.request.has_perm('people.view_profile')
            and self.should_link_straight_to_profile()):
            app = self.get_rattail_app()

            def url(customer, i):
                person = app.get_person(customer)
                if person:
                    return self.request.route_url(
                        'people.view_profile', uuid=person.uuid,
                        _anchor='customer')
                return self.get_action_url('view', customer)

            return url

        return super().default_view_url()

    def should_link_straight_to_profile(self):
        return self.rattail_config.getbool('rattail',
                                           'customers.straight_to_profile',
                                           default=False)

    def grid_extra_class(self, customer, i):
        if self.get_expose_active_in_pos():
            if not customer.active_in_pos:
                return 'warning'

    def get_instance(self):
        try:
            instance = super().get_instance()
        except HTTPNotFound:
            pass
        else:
            if instance:
                return instance

        model = self.model
        key = self.request.matchdict['uuid']

        # search by Customer.id
        instance = self.Session.query(model.Customer)\
                               .filter(model.Customer.id == key)\
                               .first()
        if instance:
            return instance

        # search by CustomerPerson.uuid
        instance = self.Session.get(model.CustomerPerson, key)
        if instance:
            return instance.customer

        # search by CustomerGroupAssignment.uuid
        instance = self.Session.get(model.CustomerGroupAssignment, key)
        if instance:
            return instance.customer

        raise self.notfound()

    def configure_form(self, f):
        super().configure_form(f)
        customer = f.model_instance
        permission_prefix = self.get_permission_prefix()

        # account_holder
        if self.creating:
            f.remove_field('account_holder')
        else:
            f.set_readonly('account_holder')
            f.set_renderer('account_holder', self.render_person)

        # default_email
        f.set_renderer('default_email', self.render_default_email)
        if not self.creating and customer.emails:
            f.set_default('default_email', customer.emails[0].address)

        # default_phone
        f.set_renderer('default_phone', self.render_default_phone)
        if not self.creating and customer.phones:
            f.set_default('default_phone', customer.phones[0].number)

        # default_address
        if self.creating or self.editing:
            f.remove_field('default_address')
        else:
            f.set_renderer('default_address', self.render_default_address)
            f.set_readonly('default_address')

        # address_*
        if not (self.creating or self.editing):
            f.remove_fields('address_street',
                            'address_street2',
                            'address_city',
                            'address_state',
                            'address_zipcode')
        elif self.editing and customer.addresses:
            addr = customer.addresses[0]
            f.set_default('address_street', addr.street)
            f.set_default('address_street2', addr.street2)
            f.set_default('address_city', addr.city)
            f.set_default('address_state', addr.state)
            f.set_default('address_zipcode', addr.zipcode)

        # email_preference
        f.set_enum('email_preference', self.enum.EMAIL_PREFERENCE)
        preferences = list(self.enum.EMAIL_PREFERENCE.items())
        preferences.insert(0, ('', "(no preference)"))
        f.widgets['email_preference'].values = preferences

        # person
        if self.creating:
            f.remove_field('person')
        else:
            f.set_readonly('person')
            f.set_renderer('person', self.form_render_person)

        # shoppers
        if self.should_expose_shoppers():
            if self.viewing:
                f.set_renderer('shoppers', self.render_shoppers)
            else:
                f.remove('shoppers')
        else:
            f.remove('shoppers')

        # people
        if self.should_expose_people():
            if self.viewing:
                f.set_renderer('people', self.render_people)
            else:
                f.remove('people')
        else:
            f.remove('people')

        # groups
        if self.creating:
            f.remove_field('groups')
        else:
            f.set_renderer('groups', self.render_groups)
            f.set_readonly('groups')

        # active_in_pos*
        if not self.get_expose_active_in_pos():
            f.remove('active_in_pos',
                     'active_in_pos_sticky')

        # members
        if self.creating:
            f.remove_field('members')
        else:
            f.set_renderer('members', self.render_members)
            f.set_readonly('members')

    def template_kwargs_view(self, **kwargs):
        kwargs = super().template_kwargs_view(**kwargs)
        customer = kwargs['instance']

        kwargs['expose_shoppers'] = self.should_expose_shoppers()
        if kwargs['expose_shoppers']:
            shoppers = []
            for shopper in customer.shoppers:
                person = shopper.person
                active = None
                if shopper.active is not None:
                    active = "Yes" if shopper.active else "No"
                data = {
                    'uuid': shopper.uuid,
                    'shopper_number': shopper.shopper_number,
                    'first_name': person.first_name,
                    'last_name': person.last_name,
                    'full_name': person.display_name,
                    'phone': person.first_phone_number(),
                    'email': person.first_email_address(),
                    'active': active,
                }
                shoppers.append(data)
            kwargs['shoppers_data'] = shoppers

        kwargs['expose_people'] = self.should_expose_people()
        if kwargs['expose_people']:
            people = []
            for person in customer.people:
                data = {
                    'uuid': person.uuid,
                    'full_name': person.display_name,
                    'first_name': person.first_name,
                    'last_name': person.last_name,
                    '_action_url_view': self.request.route_url('people.view',
                                                               uuid=person.uuid),
                }
                if self.editable and self.request.has_perm('people.edit'):
                    data['_action_url_edit'] = self.request.route_url(
                        'people.edit',
                        uuid=person.uuid)
                if self.people_detachable and self.has_perm('detach_person'):
                    data['_action_url_detach'] = self.request.route_url(
                        'customers.detach_person',
                        uuid=customer.uuid,
                        person_uuid=person.uuid)
                people.append(data)
            kwargs['people_data'] = people

        kwargs['show_profiles_helper'] = self.show_profiles_helper
        if kwargs['show_profiles_helper']:
            people = OrderedDict()

            if customer.account_holder:
                person = customer.account_holder
                people.setdefault(person.uuid, person)

            for shopper in customer.shoppers:
                if shopper.active:
                    person = shopper.person
                    people.setdefault(person.uuid, person)

            for person in customer.people:
                people.setdefault(person.uuid, person)

            kwargs['show_profiles_people'] = list(people.values())

        return kwargs

    def unique_id(self, node, value):
        model = self.model
        query = self.Session.query(model.Customer)\
                            .filter(model.Customer.id == value)
        if self.editing:
            customer = self.get_instance()
            query = query.filter(model.Customer.uuid != customer.uuid)
        if query.count():
            raise colander.Invalid(node, "Customer ID must be unique")

    def render_default_address(self, customer, field):
        if customer.addresses:
            return str(customer.addresses[0])

    def grid_render_person(self, customer, field):
        person = getattr(customer, field)
        if not person:
            return ""
        return str(person)

    def form_render_person(self, customer, field):
        person = getattr(customer, field)
        if not person:
            return ""

        text = str(person)
        url = self.request.route_url('people.view', uuid=person.uuid)
        return tags.link_to(text, url)

    def render_shoppers(self, customer, field):
        route_prefix = self.get_route_prefix()
        permission_prefix = self.get_permission_prefix()

        factory = self.get_grid_factory()
        g = factory(
            self.request,
            key=f'{route_prefix}.people',
            data=[],
            columns=[
                'shopper_number',
                'first_name',
                'last_name',
                'phone',
                'email',
                'active',
            ],
            sortable=True,
            sorters={'shopper_number': True,
                     'first_name': True,
                     'last_name': True,
                     'phone': True,
                     'email': True,
                     'active': True},
            labels={'shopper_number': "Shopper #"},
        )

        return HTML.literal(
            g.render_table_element(data_prop='shoppers'))

    def render_people(self, customer, field):
        route_prefix = self.get_route_prefix()
        permission_prefix = self.get_permission_prefix()

        factory = self.get_grid_factory()
        g = factory(
            self.request,
            key=f'{route_prefix}.people',
            data=[],
            columns=[
                'full_name',
                'first_name',
                'last_name',
            ],
            sortable=True,
            sorters={'full_name': True, 'first_name': True, 'last_name': True},
        )

        if self.request.has_perm('people.view'):
            g.actions.append(self.make_action('view', icon='eye'))
        if self.request.has_perm('people.edit'):
            g.actions.append(self.make_action('edit', icon='edit'))
        if self.people_detachable and self.has_perm('detach_person'):
            g.actions.append(self.make_action('detach', icon='minus-circle',
                                              link_class='has-text-warning',
                                              click_handler="$emit('detach-person', props.row._action_url_detach)"))

        return HTML.literal(
            g.render_table_element(data_prop='peopleData'))

    def render_groups(self, customer, field):
        groups = customer.groups
        if not groups:
            return ""
        items = []
        for group in groups:
            text = "({}) {}".format(group.id, group.name)
            url = self.request.route_url('customergroups.view', uuid=group.uuid)
            items.append(HTML.tag('li', tags.link_to(text, url)))
        return HTML.tag('ul', HTML.literal('').join(items))

    def render_members(self, customer, field):
        members = customer.members
        if not members:
            return ""
        items = []
        for member in members:
            text = str(member)
            url = self.request.route_url('members.view', uuid=member.uuid)
            items.append(HTML.tag('li', tags.link_to(text, url)))
        return HTML.tag('ul', HTML.literal('').join(items))

    def get_version_child_classes(self):
        classes = super().get_version_child_classes()
        model = self.model
        classes.extend([
            (model.CustomerGroupAssignment, 'customer_uuid'),
            (model.CustomerPhoneNumber, 'parent_uuid'),
            (model.CustomerEmailAddress, 'parent_uuid'),
            (model.CustomerMailingAddress, 'parent_uuid'),
            (model.CustomerPerson, 'customer_uuid'),
            (model.CustomerNote, 'parent_uuid'),
        ])
        return classes

    def detach_person(self):
        model = self.model
        customer = self.get_instance()
        person = self.Session.get(model.Person, self.request.matchdict['person_uuid'])
        if not person:
            return self.notfound()

        if person in customer.people:
            customer.people.remove(person)
        else:
            self.request.session.flash("No change; person \"{}\" not attached to customer \"{}\"".format(
                person, customer))

        return self.redirect(self.request.get_referrer())

    def get_merge_data(self, customer):
        return {
            'uuid': customer.uuid,
            'name': customer.name,
            'email_addresses': [e.address for e in customer.emails],
            'phone_numbers': [p.number for p in customer.phones],
        }

    def merge_objects(self, removing, keeping):
        coalesce = self.get_merge_coalesce_fields()
        if coalesce:

            if 'email_addresses' in coalesce:
                keeping_emails = [e.address for e in keeping.emails]
                for email in removing.emails:
                    if email.address not in keeping_emails:
                        keeping.add_email(address=email.address,
                                          type=email.type,
                                          invalid=email.invalid)
                        keeping_emails.append(email.address)

            if 'phone_numbers' in coalesce:
                keeping_phones = [e.number for e in keeping.phones]
                for phone in removing.phones:
                    if phone.number not in keeping_phones:
                        keeping.add_phone(number=phone.number,
                                          type=phone.type)
                        keeping_phones.append(phone.number)

        self.Session.delete(removing)

    def configure_get_simple_settings(self):
        return [

            # General
            {'section': 'rattail',
             'option': 'customers.key_field'},
            {'section': 'rattail',
             'option': 'customers.key_label'},
            {'section': 'rattail',
             'option': 'customers.choice_uses_dropdown',
             'type': bool},
            {'section': 'rattail',
             'option': 'customers.straight_to_profile',
             'type': bool},
            {'section': 'rattail',
             'option': 'customers.expose_shoppers',
             'type': bool,
             'default': True},
            {'section': 'rattail',
             'option': 'customers.expose_people',
             'type': bool,
             'default': True},
            {'section': 'rattail',
             'option': 'clientele.handler'},

            # POS
            {'section': 'rattail',
             'option': 'customers.active_in_pos',
             'type': bool},

        ]

    @classmethod
    def defaults(cls, config):
        cls._defaults(config)
        cls._customer_defaults(config)

    @classmethod
    def _customer_defaults(cls, config):
        route_prefix = cls.get_route_prefix()
        url_prefix = cls.get_url_prefix()
        instance_url_prefix = cls.get_instance_url_prefix()
        permission_prefix = cls.get_permission_prefix()
        model_key = cls.get_model_key()
        model_title = cls.get_model_title()

        # detach person
        if cls.people_detachable:
            config.add_tailbone_permission(permission_prefix,
                                           '{}.detach_person'.format(permission_prefix),
                                           "Detach a Person from a {}".format(model_title))
            # TODO: this should require POST!
            config.add_route('{}.detach_person'.format(route_prefix),
                             '{}/detach-person/{{person_uuid}}'.format(instance_url_prefix),
                             # request_method='POST',
            )
            config.add_view(cls, attr='detach_person',
                            route_name='{}.detach_person'.format(route_prefix),
                            permission='{}.detach_person'.format(permission_prefix))


class CustomerShopperView(MasterView):
    """
    Master view for the CustomerShopper class.
    """
    model_class = CustomerShopper
    route_prefix = 'customer_shoppers'
    url_prefix = '/customer-shoppers'

    grid_columns = [
        'customer_key',
        'customer',
        'shopper_number',
        'person',
        'active',
    ]

    form_fields = [
        'customer',
        'shopper_number',
        'person',
        'active',
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

    def query(self, session):
        query = super().query(session)
        model = self.model
        return query.join(model.Customer)\
                    .join(model.Person,
                          model.Person.uuid == model.CustomerShopper.person_uuid)

    def configure_grid(self, g):
        super().configure_grid(g)
        app = self.get_rattail_app()
        model = self.model

        # customer_key
        key = app.get_customer_key_field()
        label = app.get_customer_key_label()
        g.set_label('customer_key', label)
        g.set_renderer('customer_key',
                       lambda shopper, field: getattr(shopper.customer, key))
        g.set_sorter('customer_key', getattr(model.Customer, key))
        g.set_sort_defaults('customer_key')
        g.set_filter('customer_key', getattr(model.Customer, key),
                     label=f"Customer {label}",
                     default_active=True,
                     default_verb='equal')

        # customer (name)
        g.set_sorter('customer', model.Customer.name)
        g.set_filter('customer', model.Customer.name,
                     label="Customer Account Name")

        # person (name)
        g.set_sorter('person', model.Person.display_name)
        g.set_filter('person', model.Person.display_name,
                     label="Person Name")

    def configure_form(self, f):
        super().configure_form(f)

        f.set_renderer('customer', self.render_customer)
        f.set_renderer('person', self.render_person)


class PendingCustomerView(MasterView):
    """
    Master view for the Pending Customer class.
    """
    model_class = PendingCustomer
    route_prefix = 'pending_customers'
    url_prefix = '/customers/pending'

    labels = {
        'id': "ID",
        'status_code': "Status",
    }

    grid_columns = [
        'id',
        'display_name',
        'first_name',
        'last_name',
        'phone_number',
        'email_address',
        'status_code',
    ]

    form_fields = [
        'id',
        'display_name',
        'first_name',
        'middle_name',
        'last_name',
        'phone_number',
        'phone_type',
        'email_address',
        'email_type',
        'address_street',
        'address_street2',
        'address_city',
        'address_state',
        'address_zipcode',
        'address_type',
        'status_code',
        'created',
        'user',
    ]

    def configure_grid(self, g):
        super().configure_grid(g)

        g.set_enum('status_code', self.enum.PENDING_CUSTOMER_STATUS)
        g.filters['status_code'].default_active = True
        g.filters['status_code'].default_verb = 'not_equal'
        g.filters['status_code'].default_value = str(self.enum.PENDING_CUSTOMER_STATUS_RESOLVED)

        g.set_sort_defaults('display_name')
        g.set_link('id')
        g.set_link('display_name')

    def configure_form(self, f):
        super().configure_form(f)

        f.set_enum('status_code', self.enum.PENDING_CUSTOMER_STATUS)

        # created
        if self.creating:
            f.remove('created')
        else:
            f.set_readonly('created')

        # user
        if self.creating:
            f.remove('user')
        else:
            f.set_readonly('user')
            f.set_renderer('user', self.render_user)

    def editable_instance(self, pending):
        if pending.status_code == self.enum.PENDING_CUSTOMER_STATUS_RESOLVED:
            return False
        return True

    def resolve_person(self):
        model = self.model
        pending = self.get_instance()
        redirect = self.redirect(self.get_action_url('view', pending))

        uuid = self.request.POST['person_uuid']
        person = self.Session.get(model.Person, uuid)
        if not person:
            self.request.session.flash("Person not found!", 'error')
            return redirect

        app = self.get_rattail_app()
        people_handler = app.get_people_handler()
        people_handler.resolve_person(pending, person, self.request.user)
        self.Session.flush()
        return redirect

    @classmethod
    def defaults(cls, config):
        cls._defaults(config)
        cls._pending_customer_defaults(config)

    @classmethod
    def _pending_customer_defaults(cls, config):
        route_prefix = cls.get_route_prefix()
        instance_url_prefix = cls.get_instance_url_prefix()
        permission_prefix = cls.get_permission_prefix()
        model_title = cls.get_model_title()

        # resolve person
        config.add_tailbone_permission(permission_prefix,
                                       '{}.resolve_person'.format(permission_prefix),
                                       "Resolve a {} as a Person".format(model_title))
        config.add_route('{}.resolve_person'.format(route_prefix),
                         '{}/resolve-person'.format(instance_url_prefix),
                         request_method='POST')
        config.add_view(cls, attr='resolve_person',
                        route_name='{}.resolve_person'.format(route_prefix),
                        permission='{}.resolve_person'.format(permission_prefix))


# # TODO: this is referenced by some custom apps, but should be moved??
# def unique_id(value, field):
#     customer = field.parent.model
#     query = Session.query(model.Customer).filter(model.Customer.id == value)
#     if customer.uuid:
#         query = query.filter(model.Customer.uuid != customer.uuid)
#     if query.count():
#         raise fa.ValidationError("Customer ID must be unique")


# TODO: this only works when creating, need to add edit support?
# TODO: can this just go away? since we have unique_id() view method above
def unique_id(node, value):
    customers = Session.query(Customer).filter(Customer.id == value)
    if customers.count():
        raise colander.Invalid(node, "Customer ID must be unique")


def customer_info(request):
    """
    View which returns simple dictionary of info for a particular customer.
    """
    app = request.rattail_config.get_app()
    model = app.model
    uuid = request.params.get('uuid')
    customer = Session.get(model.Customer, uuid) if uuid else None
    if not customer:
        return {}
    return {
        'uuid':                 customer.uuid,
        'name':                 customer.name,
        'phone_number':         customer.phone.number if customer.phone else '',
        }


def defaults(config, **kwargs):
    base = globals()

    # TODO: deprecate / remove this
    config.add_route('customer.info', '/customers/info')
    customer_info = kwargs.get('customer_info', base['customer_info'])
    config.add_view(customer_info, route_name='customer.info',
                    renderer='json', permission='customers.view')

    CustomerView = kwargs.get('CustomerView',
                              base['CustomerView'])
    CustomerView.defaults(config)

    CustomerShopperView = kwargs.get('CustomerShopperView',
                                     base['CustomerShopperView'])
    CustomerShopperView.defaults(config)

    PendingCustomerView = kwargs.get('PendingCustomerView',
                                     base['PendingCustomerView'])
    PendingCustomerView.defaults(config)


def includeme(config):
    defaults(config)
