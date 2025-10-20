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
Member Views
"""

from collections import OrderedDict

import sqlalchemy as sa
import sqlalchemy_continuum as continuum

from rattail.db import model
from rattail.db.model import MembershipType, Member, MemberEquityPayment

from deform import widget as dfwidget
from webhelpers2.html import tags

from tailbone import grids, forms
from tailbone.views import MasterView


class MembershipTypeView(MasterView):
    """
    Master view for Membership Types
    """
    model_class = MembershipType
    route_prefix = 'membership_types'
    url_prefix = '/membership-types'
    has_versions = True

    labels = {
        'id': "ID",
    }

    grid_columns = [
        'number',
        'name',
    ]

    has_rows = True
    model_row_class = Member
    rows_title = "Members"

    row_grid_columns = [
        '_member_key_',
        'person',
        'active',
        'equity_current',
        'equity_total',
        'joined',
        'withdrew',
    ]

    def configure_grid(self, g):
        """ """
        super().configure_grid(g)

        g.set_sort_defaults('number')

        g.set_link('number')
        g.set_link('name')

    def get_row_data(self, memtype):
        """ """
        model = self.model
        return self.Session.query(model.Member)\
                           .filter(model.Member.membership_type == memtype)

    def get_parent(self, member):
        return member.membership_type

    def configure_row_grid(self, g):
        super().configure_row_grid(g)

        g.filters['active'].default_active = True
        g.filters['active'].default_verb = 'is_true'

        g.set_link('person')

    def row_view_action_url(self, member, i):
        return self.request.route_url('members.view', uuid=member.uuid)


class MemberView(MasterView):
    """
    Master view for the Member class.
    """
    model_class = Member
    is_contact = True
    touchable = True
    has_versions = True
    configurable = True
    supports_autocomplete = True

    labels = {
        'id': "ID",
        'person': "Account Holder",
    }

    grid_columns = [
        '_member_key_',
        'person',
        'membership_type',
        'active',
        'equity_current',
        'joined',
        'withdrew',
        'equity_total',
    ]

    form_fields = [
        '_member_key_',
        'person',
        'customer',
        'default_email',
        'default_phone',
        'membership_type',
        'active',
        'equity_total',
        'equity_current',
        'equity_payment_due',
        'joined',
        'withdrew',
    ]

    has_rows = True
    model_row_class = MemberEquityPayment
    rows_title = "Equity Payments"

    row_grid_columns = [
        'received',
        'amount',
        'description',
        'source',
        'transaction_identifier',
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
        """ """
        super().configure_grid(g)
        route_prefix = self.get_route_prefix()
        model = self.model

        # member key
        field = self.get_member_key_field()
        g.filters[field].default_active = True
        g.filters[field].default_verb = 'equal'
        g.set_sort_defaults(field)
        g.set_link(field)

        # person
        g.set_link('person')
        g.set_joiner('person', lambda q: q.outerjoin(model.Person))
        g.set_sorter('person', model.Person.display_name)
        g.set_filter('person', model.Person.display_name)

        # customer
        g.set_link('customer')
        g.set_joiner('customer', lambda q: q.outerjoin(model.Customer))
        g.set_sorter('customer', model.Customer.name)
        g.set_filter('customer', model.Customer.name)

        g.filters['active'].default_active = True
        g.filters['active'].default_verb = 'is_true'

        # phone
        g.set_label('phone', "Phone Number")
        g.set_joiner('phone', lambda q: q.outerjoin(model.MemberPhoneNumber, sa.and_(
            model.MemberPhoneNumber.parent_uuid == model.Member.uuid,
            model.MemberPhoneNumber.preference == 1)))
        g.set_sorter('phone', model.MemberPhoneNumber.number)
        g.set_filter('phone', model.MemberPhoneNumber.number,
                     factory=grids.filters.AlchemyPhoneNumberFilter)

        # email
        g.set_label('email', "Email Address")
        g.set_joiner('email', lambda q: q.outerjoin(model.MemberEmailAddress, sa.and_(
            model.MemberEmailAddress.parent_uuid == model.Member.uuid,
            model.MemberEmailAddress.preference == 1)))
        g.set_sorter('email', model.MemberEmailAddress.address)
        g.set_filter('email', model.MemberEmailAddress.address)

        # membership_type
        g.set_joiner('membership_type', lambda q: q.outerjoin(model.MembershipType))
        g.set_sorter('membership_type', model.MembershipType.name)
        g.set_filter('membership_type', model.MembershipType.name,
                     label="Membership Type Name")

        if (self.request.has_perm('people.view_profile')
            and self.should_link_straight_to_profile()):

            # add View Raw action
            url = lambda r, i: self.request.route_url(
                f'{route_prefix}.view', **self.get_action_route_kwargs(r))
            # nb. insert to slot 1, just after normal View action
            g.actions.insert(1, self.make_action('view_raw', url=url, icon='eye'))

        # equity_total
        # TODO: should make this configurable
        # g.set_type('equity_total', 'currency')
        g.set_renderer('equity_total', self.render_equity_total)
        g.remove_sorter('equity_total')
        g.remove_filter('equity_total')

    def render_equity_total(self, member, field):
        app = self.get_rattail_app()
        equity = app.get_membership_handler().get_equity_total(member, cached=False)
        return app.render_currency(equity)

    def default_view_url(self):
        if (self.request.has_perm('people.view_profile')
            and self.should_link_straight_to_profile()):
            app = self.get_rattail_app()

            def url(member, i):
                person = app.get_person(member)
                if person:
                    return self.request.route_url(
                        'people.view_profile', uuid=person.uuid,
                        _anchor='member')
                return self.get_action_url('view', member)

            return url

        return super().default_view_url()

    def should_link_straight_to_profile(self):
        return self.rattail_config.getbool('rattail',
                                           'members.straight_to_profile',
                                           default=False)

    def grid_extra_class(self, member, i):
        """ """
        if not member.active:
            return 'warning'
        if member.equity_current is False:
            return 'notice'

    def configure_form(self, f):
        """ """
        super().configure_form(f)
        model = self.model
        member = f.model_instance

        # date fields
        f.set_type('joined', 'date_jquery')
        f.set_type('withdrew', 'date_jquery')

        # equity fields
        f.set_renderer('equity_total', self.render_equity_total)
        f.set_type('equity_payment_due', 'date_jquery')
        f.set_type('equity_last_paid', 'date_jquery')

        # person
        if self.creating or self.editing:
            if 'person' in f.fields:
                f.replace('person', 'person_uuid')
                people = self.Session.query(model.Person)\
                                     .order_by(model.Person.display_name)
                values = [(p.uuid, str(p))
                          for p in people]
                require = False
                if not require:
                    values.insert(0, ('', "(none)"))
                f.set_widget('person_uuid', dfwidget.SelectWidget(values=values))
                f.set_label('person_uuid', "Person")
        else:
            f.set_readonly('person')
            f.set_renderer('person', self.render_person)

        # customer
        if self.creating or self.editing:
            if 'customer' in f.fields:
                f.replace('customer', 'customer_uuid')
                customers = self.Session.query(model.Customer)\
                                          .order_by(model.Customer.name)
                values = [(c.uuid, str(c))
                          for c in customers]
                require = False
                if not require:
                    values.insert(0, ('', "(none)"))
                f.set_widget('customer_uuid', dfwidget.SelectWidget(values=values))
                f.set_label('customer_uuid', "Customer")
        else:
            f.set_readonly('customer')
            f.set_renderer('customer', self.render_customer)

        # default_email
        f.set_renderer('default_email', self.render_default_email)
        if not self.creating and member.emails:
            f.set_default('default_email', member.emails[0].address)

        # default_phone
        f.set_renderer('default_phone', self.render_default_phone)
        if not self.creating and member.phones:
            f.set_default('default_phone', member.phones[0].number)

        # membership_type
        f.set_renderer('membership_type', self.render_membership_type)

        if self.creating:
            f.remove_fields(
                'equity_total',
                'equity_last_paid',
                'equity_payment_credit',
                'withdrew',
            )

    def render_equity_total(self, member, field):
        app = self.get_rattail_app()
        total = sum([payment.amount for payment in member.equity_payments])
        return app.render_currency(total)

    def template_kwargs_view(self, **kwargs):
        """ """
        kwargs = super().template_kwargs_view(**kwargs)
        app = self.get_rattail_app()
        member = kwargs['instance']

        people = OrderedDict()
        person = app.get_person(member)
        if person:
            people.setdefault(person.uuid, person)
        customer = app.get_customer(member)
        if customer:
            person = app.get_person(customer)
            if person:
                people.setdefault(person.uuid, person)
        kwargs['show_profiles_people'] = list(people.values())

        return kwargs

    def render_default_email(self, member, field):
        """ """
        if member.emails:
            return member.emails[0].address

    def render_default_phone(self, member, field):
        """ """
        if member.phones:
            return member.phones[0].number

    def render_membership_type(self, member, field):
        memtype = getattr(member, field)
        if not memtype:
            return
        text = str(memtype)
        url = self.request.route_url('membership_types.view', uuid=memtype.uuid)
        return tags.link_to(text, url)

    def get_row_data(self, member):
        """ """
        model = self.model
        return self.Session.query(model.MemberEquityPayment)\
                               .filter(model.MemberEquityPayment.member == member)

    def get_parent(self, payment):
        return payment.member

    def configure_row_grid(self, g):
        super().configure_row_grid(g)

        g.set_type('amount', 'currency')

        g.set_sort_defaults('received', 'desc')

    def row_view_action_url(self, payment, i):
        return self.request.route_url('member_equity_payments.view',
                                      uuid=payment.uuid)

    def configure_get_simple_settings(self):
        """ """
        return [

            # General
            {'section': 'rattail',
             'option': 'members.key_field'},
            {'section': 'rattail',
             'option': 'members.key_label'},
            {'section': 'rattail',
             'option': 'members.straight_to_profile',
             'type': bool},

            # Relationships
            {'section': 'rattail',
             'option': 'members.max_one_per_person',
             'type': bool},
        ]


class MemberEquityPaymentView(MasterView):
    """
    Master view for the MemberEquityPayment class.
    """
    model_class = MemberEquityPayment
    route_prefix = 'member_equity_payments'
    url_prefix = '/member-equity-payments'
    supports_grid_totals = True
    has_versions = True

    labels = {
        'status_code': "Status",
    }

    grid_columns = [
        'received',
        '_member_key_',
        'member',
        'amount',
        'description',
        'source',
        'transaction_identifier',
        'status_code',
    ]

    form_fields = [
        '_member_key_',
        'member',
        'amount',
        'received',
        'description',
        'source',
        'transaction_identifier',
        'status_code',
    ]

    def query(self, session):
        """ """
        query = super().query(session)
        model = self.model

        query = query.join(model.Member)

        return query

    def configure_grid(self, g):
        """ """
        super().configure_grid(g)
        model = self.model

        # member_key
        field = self.get_member_key_field()
        attr = getattr(model.Member, field)
        g.set_renderer(field, self.render_member_key)
        g.set_filter(field, attr,
                     label=self.get_member_key_label(),
                     default_active=True,
                     default_verb='equal')
        g.set_sorter(field, attr)

        # member (name)
        g.set_joiner('member', lambda q: q.outerjoin(model.Person))
        g.set_sorter('member', model.Person.display_name)
        g.set_link('member')
        g.set_filter('member', model.Person.display_name,
                     label="Member Name")

        g.set_type('amount', 'currency')

        g.set_sort_defaults('received', 'desc')
        g.set_link('received')

        # description
        g.set_link('description')

        g.set_link('transaction_identifier')

        # status_code
        g.set_enum('status_code', model.MemberEquityPayment.STATUS)

    def render_member_key(self, payment, field):
        key = getattr(payment.member, field)
        return key

    def fetch_grid_totals(self):
        app = self.get_rattail_app()
        results = self.get_effective_data()
        total = sum([payment.amount for payment in results])
        return {'totals_display': app.render_currency(total)}

    def configure_form(self, f):
        """ """
        super().configure_form(f)
        model = self.model
        payment = f.model_instance

        # member_key
        field = self.get_member_key_field()
        f.set_renderer(field, self.render_member_key)
        f.set_readonly(field)

        # member
        if self.creating:
            f.replace('member', 'member_uuid')
            member_display = ""
            if self.request.method == 'POST':
                if self.request.POST.get('member_uuid'):
                    member = self.Session.get(model.Member,
                                              self.request.POST['member_uuid'])
                    if member:
                        member_display = str(member)
            elif self.editing:
                member_display = str(payment.member or '')
            members_url = self.request.route_url('members.autocomplete')
            f.set_widget('member_uuid', forms.widgets.JQueryAutocompleteWidget(
                field_display=member_display, service_url=members_url))
            f.set_label('member_uuid', "Member")
        else:
            f.set_readonly('member')
            f.set_renderer('member', self.render_member)

        # amount
        f.set_type('amount', 'currency')

        # received
        if self.creating:
            f.set_type('received', 'date_jquery')
        else:
            f.set_readonly('received')

        # status_code
        f.set_enum('status_code', model.MemberEquityPayment.STATUS)

    def get_version_diff_enums(self, version):
        """ """
        model = self.model
        cls = continuum.parent_class(version.__class__)

        if cls is model.MemberEquityPayment:
            return {'status_code': model.MemberEquityPayment.STATUS}


def defaults(config, **kwargs):
    base = globals()

    MembershipTypeView = kwargs.get('MembershipTypeView', base['MembershipTypeView'])
    MembershipTypeView.defaults(config)

    MemberView = kwargs.get('MemberView', base['MemberView'])
    MemberView.defaults(config)

    MemberEquityPaymentView = kwargs.get('MemberEquityPaymentView', base['MemberEquityPaymentView'])
    MemberEquityPaymentView.defaults(config)


def includeme(config):
    defaults(config)
