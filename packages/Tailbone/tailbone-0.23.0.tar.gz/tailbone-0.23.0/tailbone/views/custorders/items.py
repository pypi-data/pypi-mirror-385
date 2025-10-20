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
Customer order item views
"""

import datetime

from sqlalchemy import orm

from rattail.db.model import CustomerOrderItem

from webhelpers2.html import HTML, tags

from tailbone.views import MasterView
from tailbone.util import raw_datetime, csrf_token


class CustomerOrderItemView(MasterView):
    """
    Master view for customer order items
    """
    model_class = CustomerOrderItem
    route_prefix = 'custorders.items'
    url_prefix = '/custorders/items'
    creatable = False
    editable = False
    deletable = False

    labels = {
        'order': "Customer Order",
        'order_id': "Order ID",
        'order_uom': "Order UOM",
        'status_code': "Status",
    }

    grid_columns = [
        'order_id',
        'person',
        '_product_key_',
        'product_brand',
        'product_description',
        'product_size',
        'department_name',
        'case_quantity',
        'order_quantity',
        'order_uom',
        'total_price',
        'order_created',
        'status_code',
        'flagged',
    ]

    form_fields = [
        'order',
        'customer',
        'person',
        'sequence',
        '_product_key_',
        'product',
        'pending_product',
        'product_brand',
        'product_description',
        'product_size',
        'case_quantity',
        'order_quantity',
        'order_uom',
        'unit_price',
        'total_price',
        'special_order',
        'price_needs_confirmation',
        'paid_amount',
        'payment_transaction_number',
        'status_code',
        'flagged',
        'contact_attempts',
        'last_contacted',
        'events',
    ]

    def __init__(self, request):
        super().__init__(request)
        app = self.get_rattail_app()
        self.custorder_handler = app.get_custorder_handler()
        self.batch_handler = app.get_batch_handler(
            'custorder',
            default='rattail.batch.custorder:CustomerOrderBatchHandler')

    def query(self, session):
        model = self.model
        return session.query(model.CustomerOrderItem)\
                      .join(model.CustomerOrder)\
                      .options(orm.joinedload(model.CustomerOrderItem.order)\
                               .joinedload(model.CustomerOrder.person))

    def configure_grid(self, g):
        super().configure_grid(g)
        model = self.model

        # order_id
        g.set_renderer('order_id', self.render_order_id)
        g.set_link('order_id')

        # person
        g.set_label('person', "Person Name")
        g.set_renderer('person', self.render_person_text)
        g.set_link('person')
        g.set_joiner('person', lambda q: q.outerjoin(model.Person))
        g.set_sorter('person', model.Person.display_name)
        g.set_filter('person', model.Person.display_name,
                     default_active=True, default_verb='contains')

        # product_key
        field = self.get_product_key_field()
        g.set_renderer(field, lambda item, field: getattr(item, f'product_{field}'))

        # product_*
        g.set_label('product_brand', "Brand")
        g.set_link('product_brand')
        g.set_label('product_description', "Description")
        g.set_link('product_description')
        g.set_label('product_size', "Size")

        # "numbers"
        g.set_type('case_quantity', 'quantity')
        g.set_type('order_quantity', 'quantity')
        g.set_type('total_price', 'currency')
        # TODO: deprecate / remove these
        g.set_type('cases_ordered', 'quantity')
        g.set_type('units_ordered', 'quantity')

        # order_uom
        # nb. this is not relevant if "case orders only"
        if not self.batch_handler.allow_unit_orders():
            g.remove('order_uom')
        else:
            g.set_enum('order_uom', self.enum.UNIT_OF_MEASURE)

        # order_created
        g.set_renderer('order_created', self.render_order_created)
        g.set_sorter('order_created', model.CustomerOrder.created)
        g.set_sort_defaults('order_created', 'desc')

        # status_code
        g.set_renderer('status_code', self.render_status_code_column)

        # abbreviate some labels, only in grid header
        g.set_label('case_quantity', "Case Qty")
        g.filters['case_quantity'].label = "Case Quantity"
        g.set_label('order_quantity', "Order Qty")
        g.filters['order_quantity'].label = "Order Quantity"
        g.set_label('department_name', "Department")
        g.filters['department_name'].label = "Department Name"
        g.set_label('total_price', "Total")
        g.filters['total_price'].label = "Total Price"
        g.set_label('order_created', "Ordered")
        if 'order_created' in g.filters:
            g.filters['order_created'].label = "Order Created"

    def render_order_id(self, item, field):
        return item.order.id

    def render_person_text(self, item, field):
        person = item.order.person
        if person:
            text = str(person)
            return text

    def render_order_created(self, item, column):
        app = self.get_rattail_app()
        value = app.localtime(item.order.created, from_utc=True)
        return raw_datetime(self.rattail_config, value)

    def render_status_code_column(self, item, field):
        text = self.enum.CUSTORDER_ITEM_STATUS.get(item.status_code,
                                                   str(item.status_code))
        if item.status_text:
            return HTML.tag('span', title=item.status_text, c=[text])
        return text

    def configure_form(self, f):
        super().configure_form(f)
        item = f.model_instance

        # order
        f.set_renderer('order', self.render_order)

        # contact
        if self.batch_handler.new_order_requires_customer():
            f.remove('person')
        else:
            f.remove('customer')

        # product key
        key = self.get_product_key_field()
        f.set_renderer(key, lambda item, field: getattr(item, f'product_{key}'))

        # (pending) product
        f.set_renderer('product', self.render_product)
        f.set_renderer('pending_product', self.render_pending_product)
        if self.viewing:
            if item.product and not item.pending_product:
                f.remove('pending_product')
            elif item.pending_product and not item.product:
                f.remove('product')

        # product*
        if not self.creating and item.product:
            f.remove('product_brand', 'product_description')
        f.set_enum('product_unit_of_measure', self.enum.UNIT_OF_MEASURE)

        # highlight pending fields
        f.set_renderer('product_brand', self.highlight_pending_field)
        f.set_renderer('product_description', self.highlight_pending_field)
        f.set_renderer('product_size', self.highlight_pending_field)
        f.set_renderer('case_quantity', self.highlight_pending_field_quantity)

        # quantity fields
        f.set_type('cases_ordered', 'quantity')
        f.set_type('units_ordered', 'quantity')
        f.set_type('order_quantity', 'quantity')
        f.set_enum('order_uom', self.enum.UNIT_OF_MEASURE)

        # price fields
        f.set_renderer('unit_price', self.render_price_with_confirmation)
        f.set_renderer('total_price', self.render_price_with_confirmation)
        f.set_renderer('price_needs_confirmation', self.render_price_needs_confirmation)
        f.set_type('paid_amount', 'currency')

        # person
        f.set_renderer('person', self.render_person)

        # status_code
        f.set_renderer('status_code', self.render_status_code)

        # flagged
        f.set_renderer('flagged', self.render_flagged)

        # events
        f.set_renderer('events', self.render_events)

    def render_flagged(self, item, field):
        text = "Yes" if item.flagged else "No"
        items = [HTML.tag('span', c=text)]

        if self.has_perm('change_status'):
            button_text = "Un-Flag This" if item.flagged else "Flag This"
            form = [
                tags.form(self.get_action_url('change_flagged', item),
                          **{'@submit': 'changeFlaggedSubmit'}),
                csrf_token(self.request),
                tags.hidden('new_flagged',
                            value='false' if item.flagged else 'true'),
                HTML.tag('b-button',
                         type='is-warning' if item.flagged else 'is-primary',
                         c=f"{{{{ changeFlaggedSubmitting ? 'Working, please wait...' : '{button_text}' }}}}",
                         native_type='submit',
                         style='margin-left: 1rem;',
                         icon_pack='fas', icon_left='flag',
                         **{':disabled': 'changeFlaggedSubmitting'}),
                tags.end_form(),
            ]
            items.append(HTML.literal('').join(form))

        left = HTML.tag('div', class_='level-left', c=items)
        outer = HTML.tag('div', class_='level', c=[left])
        return outer

    def change_flagged(self):
        """
        View for changing "flagged" status of one or more order products.
        """
        item = self.get_instance()
        redirect = self.redirect(self.get_action_url('view', item))

        new_flagged = self.request.POST['new_flagged'] == 'true'
        item.flagged = new_flagged

        flagged = "FLAGGED" if new_flagged else "UN-FLAGGED"
        self.request.session.flash(f"Order item has been {flagged}")
        return redirect

    def highlight_pending_field(self, item, field, value=None):
        if value is None:
            value = getattr(item, field)
        if not item.product_uuid and item.pending_product_uuid:
            return HTML.tag('span', c=[value],
                            class_='has-text-success')
        return value

    def highlight_pending_field_quantity(self, item, field):
        app = self.get_rattail_app()
        value = getattr(item, field)
        value = app.render_quantity(value)
        return self.highlight_pending_field(item, field, value)

    def render_price_with_confirmation(self, item, field):
        price = getattr(item, field)
        app = self.get_rattail_app()
        text = app.render_currency(price)
        if not item.product_uuid and item.pending_product_uuid:
            text = HTML.tag('span', c=[text],
                            class_='has-text-success')
        if item.price_needs_confirmation:
            return HTML.tag('span', class_='has-background-warning',
                            c=[text])
        return text

    def render_price_needs_confirmation(self, item, field):

        value = item.price_needs_confirmation
        text = "Yes" if value else "No"
        items = [text]

        if value and self.has_perm('confirm_price'):
            button = HTML.tag('b-button', type='is-primary', c="Confirm Price",
                              style='margin-left: 1rem;',
                              icon_pack='fas', icon_left='check',
                              **{'@click': "$emit('confirm-price')"})
            items.append(button)

        left = HTML.tag('div', class_='level-left', c=items)
        outer = HTML.tag('div', class_='level', c=[left])
        return outer

    def render_status_code(self, item, field):
        text = self.enum.CUSTORDER_ITEM_STATUS[item.status_code]
        if item.status_text:
            text = "{} ({})".format(text, item.status_text)
        items = [HTML.tag('span', c=[text])]

        if self.has_perm('change_status'):

            # Mark Received
            if self.can_be_received(item):
                button = HTML.tag('b-button', type='is-primary', c="Mark Received",
                                  style='margin-left: 1rem;',
                                  icon_pack='fas', icon_left='check',
                                  **{'@click': "$emit('mark-received')"})
                items.append(button)

            # Change Status
            button = HTML.tag('b-button', type='is-primary', c="Change Status",
                              style='margin-left: 1rem;',
                              icon_pack='fas', icon_left='edit',
                              **{'@click': "$emit('change-status')"})
            items.append(button)

        left = HTML.tag('div', class_='level-left', c=items)
        outer = HTML.tag('div', class_='level', c=[left])
        return outer

    def can_be_received(self, item):

        # TODO: is this generic enough?  probably belongs in handler anyway..
        if item.status_code in (self.enum.CUSTORDER_ITEM_STATUS_INITIATED,
                                self.enum.CUSTORDER_ITEM_STATUS_READY,
                                self.enum.CUSTORDER_ITEM_STATUS_PLACED):
            return True

        return False

    def render_events(self, item, field):
        route_prefix = self.get_route_prefix()

        factory = self.get_grid_factory()
        g = factory(
            self.request,
            key=f'{route_prefix}.events',
            data=[],
            columns=[
                'occurred',
                'type_code',
                'user',
                'note',
            ],
            labels={
                'occurred': "When",
                'type_code': "What",
                'user': "Who",
            },
        )

        table = HTML.literal(
            g.render_table_element(data_prop='eventsData'))
        elements = [table]

        if self.has_perm('add_note'):
            button = HTML.tag('b-button', type='is-primary', c="Add Note",
                              class_='is-pulled-right',
                              icon_pack='fas', icon_left='plus',
                              **{'@click': "$emit('add-note')"})
            button_wrapper = HTML.tag('div', c=[button],
                                      style='margin-top: 0.5rem;')
            elements.append(button_wrapper)

        return HTML.tag('div',
                        style='display: flex; flex-direction: column;',
                        c=elements)

    def template_kwargs_view(self, **kwargs):
        kwargs = super().template_kwargs_view(**kwargs)
        model = self.model
        app = self.get_rattail_app()
        item = kwargs['instance']

        # fetch events for current item
        kwargs['events_data'] = self.get_context_events(item)

        # fetch "other" order items, siblings of current one
        order = item.order
        other_items = self.Session.query(model.CustomerOrderItem)\
                                  .filter(model.CustomerOrderItem.order == order)\
                                  .filter(model.CustomerOrderItem.uuid != item.uuid)\
                                  .all()
        other_data = []
        product_key_field = self.get_product_key_field()
        for other in other_items:

            order_date = None
            if order.created:
                order_date = app.localtime(order.created, from_utc=True).date()

            other_data.append({
                'uuid': other.uuid,
                'product_key': getattr(other, f'product_{product_key_field}'),
                'brand_name': other.product_brand,
                'product_description': other.product_description,
                'product_size': other.product_size,
                'product_case_quantity': app.render_quantity(other.case_quantity),
                'order_quantity': app.render_quantity(other.order_quantity),
                'order_uom': self.enum.UNIT_OF_MEASURE[other.order_uom],
                'department_name': other.department_name,
                'product_barcode': other.product_upc.pretty() if other.product_upc else None,
                'unit_price': app.render_currency(other.unit_price),
                'total_price': app.render_currency(other.total_price),
                'order_date': app.render_date(order_date),
                'status_code': self.enum.CUSTORDER_ITEM_STATUS[other.status_code],
                'flagged': other.flagged,
            })
        kwargs['other_order_items_data'] = other_data

        return kwargs

    def get_context_events(self, item):
        app = self.get_rattail_app()
        events = []
        for event in item.events:
            occurred = app.localtime(event.occurred, from_utc=True)
            events.append({
                'occurred': raw_datetime(self.rattail_config, occurred),
                'type_code': self.enum.CUSTORDER_ITEM_EVENT.get(event.type_code, event.type_code),
                'user': str(event.user),
                'note': event.note,
            })
        return events

    def confirm_price(self):
        """
        View for confirming price of an order item.
        """
        item = self.get_instance()
        redirect = self.redirect(self.get_action_url('view', item))

        # locate user responsible for change
        user = self.request.user

        # grab user-provided note to attach to event
        note = self.request.POST.get('note')

        # declare item no longer in need of price confirmation
        item.price_needs_confirmation = False
        item.add_event(self.enum.CUSTORDER_ITEM_EVENT_PRICE_CONFIRMED,
                       user, note=note)

        # advance item to next status
        if item.status_code == self.enum.CUSTORDER_ITEM_STATUS_INITIATED:
            item.status_code = self.enum.CUSTORDER_ITEM_STATUS_READY
            item.status_text = "price has been confirmed"

        self.request.session.flash("Price has been confirmed.")
        return redirect

    def mark_received(self):
        """
        View to mark some order item(s) as having been received.
        """
        app = self.get_rattail_app()
        model = self.model
        uuids = self.request.POST['order_item_uuids'].split(',')

        order_items = self.Session.query(model.CustomerOrderItem)\
                                  .filter(model.CustomerOrderItem.uuid.in_(uuids))\
                                  .all()

        handler = app.get_custorder_handler()
        handler.mark_received(order_items, self.request.user)

        msg = self.mark_received_get_flash(order_items)
        self.request.session.flash(msg)
        return self.redirect(self.request.get_referrer(default=self.get_index_url()))

    def mark_received_get_flash(self, order_items):
        return "Order item statuses have been updated."

    def change_status(self):
        """
        View for changing status of one or more order items.
        """
        model = self.model
        order_item = self.get_instance()
        redirect = self.redirect(self.get_action_url('view', order_item))

        # validate new status
        new_status_code = int(self.request.POST['new_status_code'])
        if new_status_code not in self.enum.CUSTORDER_ITEM_STATUS:
            self.request.session.flash("Invalid status code", 'error')
            return redirect

        # locate order items to which new status will be applied
        order_items = [order_item]
        uuids = self.request.POST['uuids']
        if uuids:
            for uuid in uuids.split(','):
                item = self.Session.get(model.CustomerOrderItem, uuid)
                if item:
                    order_items.append(item)

        # locate user responsible for change
        user = self.request.user

        # maybe grab extra user-provided note to attach
        extra_note = self.request.POST.get('note')

        # apply new status to order item(s)
        for item in order_items:
            if item.status_code != new_status_code:

                # attach event
                note = "status changed from \"{}\" to \"{}\"".format(
                    self.enum.CUSTORDER_ITEM_STATUS[item.status_code],
                    self.enum.CUSTORDER_ITEM_STATUS[new_status_code])
                if extra_note:
                    note = "{} - NOTE: {}".format(note, extra_note)
                item.events.append(model.CustomerOrderItemEvent(
                    type_code=self.enum.CUSTORDER_ITEM_EVENT_STATUS_CHANGE,
                    user=user, note=note))

                # change status
                item.status_code = new_status_code
                # nb. must blank this out, b/c user cannot specify new
                # text and the old text no longer applies
                item.status_text = None

        self.request.session.flash("Status has been updated to: {}".format(
            self.enum.CUSTORDER_ITEM_STATUS[new_status_code]))
        return redirect

    def add_note(self):
        """
        View for adding a new note to current order item, optinally
        also adding it to all other items under the parent order.
        """
        item = self.get_instance()
        data = self.request.json_body

        self.custorder_handler.add_note(item, data['note'], self.request.user,
                                        apply_all=data['apply_all'] == True)

        self.Session.flush()
        self.Session.refresh(item)
        return {'events': self.get_context_events(item)}

    def render_order(self, item, field):
        order = item.order
        if not order:
            return ""
        text = str(order)
        url = self.request.route_url('custorders.view', uuid=order.uuid)
        return tags.link_to(text, url)

    def render_person(self, item, field):
        person = item.order.person
        if person:
            text = str(person)
            url = self.request.route_url('people.view', uuid=person.uuid)
            return tags.link_to(text, url)

    @classmethod
    def defaults(cls, config):
        cls._order_item_defaults(config)
        cls._defaults(config)

    @classmethod
    def _order_item_defaults(cls, config):
        route_prefix = cls.get_route_prefix()
        url_prefix = cls.get_url_prefix()
        instance_url_prefix = cls.get_instance_url_prefix()
        permission_prefix = cls.get_permission_prefix()
        model_title = cls.get_model_title()
        model_title_plural = cls.get_model_title_plural()

        # fix permission group name
        config.add_tailbone_permission_group(permission_prefix, model_title_plural)

        # confirm price
        config.add_tailbone_permission(permission_prefix,
                                       '{}.confirm_price'.format(permission_prefix),
                                       "Confirm price for a {}".format(model_title))
        config.add_route('{}.confirm_price'.format(route_prefix),
                         '{}/confirm-price'.format(instance_url_prefix),
                         request_method='POST')
        config.add_view(cls, attr='confirm_price',
                        route_name='{}.confirm_price'.format(route_prefix),
                        permission='{}.confirm_price'.format(permission_prefix))

        # mark received
        config.add_route(f'{route_prefix}.mark_received',
                         f'{url_prefix}/mark-received',
                         request_method='POST')
        config.add_view(cls, attr='mark_received',
                        route_name=f'{route_prefix}.mark_received',
                        permission=f'{permission_prefix}.change_status')

        # change status
        config.add_tailbone_permission(permission_prefix,
                                       '{}.change_status'.format(permission_prefix),
                                       "Change status for 1 or more {}".format(model_title_plural))
        config.add_route('{}.change_status'.format(route_prefix),
                         '{}/change-status'.format(instance_url_prefix),
                         request_method='POST')
        config.add_view(cls, attr='change_status',
                        route_name='{}.change_status'.format(route_prefix),
                        permission='{}.change_status'.format(permission_prefix))

        # change flagged
        config.add_route(f'{route_prefix}.change_flagged',
                         f'{instance_url_prefix}/change-flagged',
                         request_method='POST')
        config.add_view(cls, attr='change_flagged',
                        route_name=f'{route_prefix}.change_flagged',
                        permission=f'{permission_prefix}.change_status')

        # add note
        config.add_tailbone_permission(permission_prefix,
                                       '{}.add_note'.format(permission_prefix),
                                       "Add arbitrary notes for {}".format(model_title_plural))
        config.add_route('{}.add_note'.format(route_prefix),
                         '{}/add-note'.format(instance_url_prefix),
                         request_method='POST')
        config.add_view(cls, attr='add_note',
                        route_name='{}.add_note'.format(route_prefix),
                        renderer='json',
                        permission='{}.add_note'.format(permission_prefix))


# TODO: deprecate / remove this
CustomerOrderItemsView = CustomerOrderItemView


def defaults(config, **kwargs):
    base = globals()

    CustomerOrderItemView = kwargs.get('CustomerOrderItemView', base['CustomerOrderItemView'])
    CustomerOrderItemView.defaults(config)


def includeme(config):
    defaults(config)
