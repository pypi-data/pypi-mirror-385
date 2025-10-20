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
Vendor Views
"""

from rattail.db import model

from webhelpers2.html import tags

from tailbone.views import MasterView
from tailbone.db import Session


class VendorView(MasterView):
    """
    Master view for the Vendor class.
    """
    model_class = model.Vendor
    has_versions = True
    touchable = True
    results_downloadable = True
    supports_autocomplete = True
    configurable = True

    labels = {
        'id': "ID",
        'default_phone': "Phone Number",
        'default_email': "Default Email",
    }

    grid_columns = [
        'id',
        'name',
        'abbreviation',
        'phone',
        'email',
        'contact',
        'terms',
    ]

    form_fields = [
        'id',
        'name',
        'abbreviation',
        'special_discount',
        'lead_time_days',
        'order_interval_days',
        'default_phone',
        'default_email',
        'orders_email',
        'contact',
        'terms',
    ]

    def configure_grid(self, g):
        super().configure_grid(g)

        g.filters['name'].default_active = True
        g.filters['name'].default_verb = 'contains'
        g.set_sort_defaults('name')

        g.set_label('phone', "Phone Number")
        g.set_label('email', "Email Address")

        g.set_link('id')
        g.set_link('name')
        g.set_link('abbreviation')

    def configure_form(self, f):
        super().configure_form(f)
        app = self.get_rattail_app()
        vendor = f.model_instance

        f.set_type('lead_time_days', 'quantity')
        f.set_type('order_interval_days', 'quantity')

        # default_phone
        f.set_renderer('default_phone', self.render_default_phone)
        if not self.creating and vendor.phones:
            f.set_default('default_phone', vendor.phones[0].number)

        # default_email
        f.set_renderer('default_email', self.render_default_email)
        if not self.creating and vendor.emails:
            f.set_default('default_email', vendor.emails[0].address)

        # orders_email
        f.set_renderer('orders_email', self.render_orders_email)
        if not self.creating and vendor.emails:
            f.set_default('orders_email', app.get_contact_email_address(vendor, type_='Orders') or '')

        # contact
        if self.creating:
            f.remove_field('contact')
        else:
            f.set_readonly('contact')
            f.set_renderer('contact', self.render_contact)

    def objectify(self, form, data=None):
        if data is None:
            data = form.validated
        vendor = super().objectify(form, data)
        vendor = self.objectify_contact(vendor, data)
        app = self.get_rattail_app()

        if 'orders_email' in data:
            address = data['orders_email']
            email = app.get_contact_email(vendor, type_='Orders')
            if address:
                if email:
                    if email.address != address:
                        email.address = address
                else:
                    vendor.add_email_address(address, type='Orders')
            elif email:
                vendor.emails.remove(email)

        return vendor

    def render_default_email(self, vendor, field):
        if vendor.emails:
            return vendor.emails[0].address

    def render_orders_email(self, vendor, field):
        app = self.get_rattail_app()
        return app.get_contact_email_address(vendor, type_='Orders')

    def render_default_phone(self, vendor, field):
        if vendor.phones:
            return vendor.phones[0].number

    def render_contact(self, vendor, field):
        person = vendor.contact
        if not person:
            return ""
        text = str(person)
        url = self.request.route_url('people.view', uuid=person.uuid)
        return tags.link_to(text, url)

    def before_delete(self, vendor):
        # Remove all product costs.
        q = self.Session.query(model.ProductCost).filter(
            model.ProductCost.vendor == vendor)
        for cost in q:
            self.Session.delete(cost)

    def get_version_child_classes(self):
        return super().get_version_child_classes() + [
            (model.VendorPhoneNumber, 'parent_uuid'),
            (model.VendorEmailAddress, 'parent_uuid'),
            (model.VendorContact, 'vendor_uuid'),
        ]

    def configure_get_simple_settings(self):
        config = self.rattail_config
        return [

            # display
            {'section': 'rattail',
             'option': 'vendors.choice_uses_dropdown',
             'type': bool},
        ]

    def configure_get_context(self, **kwargs):
        context = super().configure_get_context(**kwargs)

        context['supported_vendor_settings'] = self.configure_get_supported_vendor_settings()

        return context

    def configure_gather_settings(self, data, **kwargs):
        settings = super().configure_gather_settings(
            data, **kwargs)

        supported_vendor_settings = self.configure_get_supported_vendor_settings()
        for setting in supported_vendor_settings.values():
            name = 'rattail.vendor.{}'.format(setting['key'])
            settings.append({'name': name,
                             'value': data[name]})

        return settings

    def configure_remove_settings(self, **kwargs):
        super().configure_remove_settings(**kwargs)
        app = self.get_rattail_app()
        names = []

        supported_vendor_settings = self.configure_get_supported_vendor_settings()
        for setting in supported_vendor_settings.values():
            names.append('rattail.vendor.{}'.format(setting['key']))

        if names:
            # nb. using thread-local session here; we do not use
            # self.Session b/c it may not point to Rattail
            session = Session()
            for name in names:
                app.delete_setting(session, name)

    def configure_get_supported_vendor_settings(self):
        app = self.get_rattail_app()
        vendor_handler = app.get_vendor_handler()
        batch_handler = app.get_batch_handler('purchase')
        settings = {}

        for parser in batch_handler.get_supported_invoice_parsers():
            key = parser.vendor_key
            if not key:
                continue

            vendor = vendor_handler.get_vendor(self.Session(), key)
            settings[key] = {
                'key': key,
                'value': vendor.uuid if vendor else None,
                'label': str(vendor) if vendor else None,
            }

        return settings


def defaults(config, **kwargs):
    base = globals()

    VendorView = kwargs.get('VendorView', base['VendorView'])
    VendorView.defaults(config)


def includeme(config):
    defaults(config)
