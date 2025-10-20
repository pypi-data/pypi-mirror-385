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
Customer Order Views
"""

import decimal
import logging

from sqlalchemy import orm

from rattail.db.model import CustomerOrder, CustomerOrderItem
from rattail.util import simple_error
from rattail.batch import get_batch_handler

from webhelpers2.html import tags, HTML

from tailbone.views import MasterView


log = logging.getLogger(__name__)


class CustomerOrderView(MasterView):
    """
    Master view for customer orders
    """
    model_class = CustomerOrder
    route_prefix = 'custorders'
    editable = False
    configurable = True

    labels = {
        'id': "Order ID",
        'status_code': "Status",
    }

    grid_columns = [
        'id',
        'customer',
        'person',
        'status_code',
        'created',
        'created_by',
    ]

    form_fields = [
        'id',
        'store',
        'customer',
        'person',
        'pending_customer',
        'phone_number',
        'email_address',
        'total_price',
        'status_code',
        'created',
        'created_by',
    ]

    has_rows = True
    model_row_class = CustomerOrderItem
    rows_viewable = False

    row_labels = {
        'order_uom': "Order UOM",
    }

    row_grid_columns = [
        'sequence',
        '_product_key_',
        'product_brand',
        'product_description',
        'product_size',
        'order_quantity',
        'order_uom',
        'case_quantity',
        'department_name',
        'total_price',
        'status_code',
        'flagged',
    ]

    PENDING_PRODUCT_ENTRY_FIELDS = [
        'key',
        'department_uuid',
        'brand_name',
        'description',
        'size',
        'vendor_name',
        'vendor_item_code',
        'unit_cost',
        'case_size',
        'regular_price_amount',
    ]

    def __init__(self, request):
        super().__init__(request)
        self.batch_handler = self.get_batch_handler()

    def query(self, session):
        model = self.app.model
        return session.query(model.CustomerOrder)\
                      .options(orm.joinedload(model.CustomerOrder.customer))

    def configure_grid(self, g):
        super().configure_grid(g)
        model = self.app.model

        # id
        g.set_link('id')
        g.filters['id'].default_active = True
        g.filters['id'].default_verb = 'equal'

        # import ipdb; ipdb.set_trace()

        # customer or person
        if self.batch_handler.new_order_requires_customer():
            g.remove('person')
            g.set_link('customer')
            g.set_joiner('customer', lambda q: q.outerjoin(model.Customer))
            g.set_sorter('customer', model.Customer.name)
            g.filters['customer'] = g.make_filter('customer', model.Customer.name,
                                                  label="Customer Name",
                                                  default_active=True,
                                                  default_verb='contains')
        else:
            g.remove('customer')
            g.set_link('person')
            g.set_joiner('person', lambda q: q.outerjoin(model.Person))
            g.set_sorter('person', model.Person.display_name)
            g.filters['person'] = g.make_filter('person', model.Person.display_name,
                                                label="Person Name",
                                                default_active=True,
                                                default_verb='contains')

        # status_code
        g.set_enum('status_code', self.enum.CUSTORDER_STATUS)

        # created
        g.set_sort_defaults('created', 'desc')

    def get_instance_title(self, order):
        return f"#{order.id} for {order.customer or order.person}"

    def configure_form(self, f):
        super().configure_form(f)
        order = f.model_instance

        f.set_readonly('id')

        f.set_renderer('store', self.render_store)

        # (pending) customer
        f.set_renderer('customer', self.render_customer)
        f.set_renderer('person', self.render_person)
        f.set_renderer('pending_customer', self.render_pending_customer)
        if self.viewing:
            if self.batch_handler.new_order_requires_customer():
                f.remove('person')
                if order.customer and not order.pending_customer:
                    f.remove('pending_customer')
                elif order.pending_customer and not order.customer:
                    f.remove('customer')
            else:
                f.remove('customer')
                if order.person and not order.pending_customer:
                    f.remove('pending_customer')
                elif order.pending_customer and not order.person:
                    f.remove('person')

        # contact info
        f.set_renderer('phone_number', self.highlight_pending_field)
        f.set_renderer('email_address', self.highlight_pending_field)

        f.set_type('total_price', 'currency')

        f.set_enum('status_code', self.enum.CUSTORDER_STATUS)

        f.set_readonly('created')

        f.set_readonly('created_by')
        f.set_renderer('created_by', self.render_user)

    def highlight_pending_field(self, order, field):
        value = getattr(order, field)
        pending = False
        if self.batch_handler.new_order_requires_customer():
            if not order.customer_uuid and order.pending_customer_uuid:
                pending = True
        else:
            if not order.person_uuid and order.pending_customer_uuid:
                pending = True
        if pending:
            return HTML.tag('span', c=[value],
                            class_='has-text-success')
        return value

    def render_person(self, order, field):
        person = order.person
        if not person:
            return ""
        text = str(person)
        url = self.request.route_url('people.view', uuid=person.uuid)
        return tags.link_to(text, url)

    def render_pending_customer(self, batch, field):
        pending = batch.pending_customer
        if not pending:
            return
        text = str(pending)
        url = self.request.route_url('pending_customers.view', uuid=pending.uuid)
        return tags.link_to(text, url,
                            class_='has-background-warning')

    def get_row_data(self, order):
        model = self.app.model
        return self.Session.query(model.CustomerOrderItem)\
                           .filter(model.CustomerOrderItem.order == order)

    def get_parent(self, item):
        return item.order

    def make_row_grid_kwargs(self, **kwargs):
        kwargs = super().make_row_grid_kwargs(**kwargs)

        actions = kwargs.get('actions', [])
        if not actions:
            actions.append(self.make_action('view', icon='eye',
                                            url=self.row_view_action_url))
            kwargs['actions'] = actions

        return kwargs

    def row_view_action_url(self, item, i):
        if self.request.has_perm('custorders.items.view'):
            return self.request.route_url('custorders.items.view', uuid=item.uuid)

    def configure_row_grid(self, g):
        super().configure_row_grid(g)
        app = self.get_rattail_app()
        handler = app.get_batch_handler(
            'custorder',
            default='rattail.batch.custorder:CustomerOrderBatchHandler')

        # product key
        key = self.get_product_key_field()
        g.set_renderer(key, lambda item, field: getattr(item, f'product_{key}'))

        g.set_type('case_quantity', 'quantity')
        g.set_type('order_quantity', 'quantity')
        g.set_type('cases_ordered', 'quantity')
        g.set_type('units_ordered', 'quantity')

        if handler.product_price_may_be_questionable():
            g.set_renderer('total_price', self.render_price_with_confirmation)
        else:
            g.set_type('total_price', 'currency')

        g.set_enum('order_uom', self.enum.UNIT_OF_MEASURE)
        g.set_renderer('status_code', self.render_row_status_code)

        g.set_label('sequence', "Seq.")
        g.filters['sequence'].label = "Sequence"
        g.set_label('product_brand', "Brand")
        g.set_label('product_description', "Description")
        g.set_label('product_size', "Size")
        g.set_label('status_code', "Status")

        g.set_sort_defaults('sequence')

        g.set_link('product_brand')
        g.set_link('product_description')

    def row_grid_extra_class(self, item, i):
        if not item.product_uuid and item.pending_product_uuid:
            return 'has-text-success'

    def render_price_with_confirmation(self, item, field):
        price = getattr(item, field)
        app = self.get_rattail_app()
        text = app.render_currency(price)
        if item.price_needs_confirmation:
            return HTML.tag('span', class_='has-background-warning',
                            c=[text])
        return text

    def render_row_status_code(self, item, field):
        text = self.enum.CUSTORDER_ITEM_STATUS.get(item.status_code,
                                                   str(item.status_code))
        if item.status_text:
            return HTML.tag('span', title=item.status_text, c=[text])
        return text

    def get_batch_handler(self):
        app = self.get_rattail_app()
        return app.get_batch_handler(
            'custorder',
            default='rattail.batch.custorder:CustomerOrderBatchHandler')

    def create(self, form=None, template='create'):
        """
        View for creating a new customer order.  Note that it does so by way of
        maintaining a "new customer order" batch, until the user finally
        submits the order, at which point the batch is converted to a proper
        order.
        """
        app = self.get_rattail_app()
        # TODO: deprecate / remove this
        self.handler = self.batch_handler
        batch = self.get_current_batch()

        if self.request.method == 'POST':

            # first we check for traditional form post
            action = self.request.POST.get('action')
            post_actions = [
                'start_over_entirely',
                'delete_batch',
            ]
            if action in post_actions:
                return getattr(self, action)(batch)

            # okay then, we'll assume newer JSON-style post params
            data = dict(self.request.json_body)
            action = data.get('action')
            json_actions = [
                'assign_contact',
                'unassign_contact',
                'update_phone_number',
                'update_email_address',
                'update_pending_customer',
                'get_customer_info',
                # 'set_customer_data',
                'get_product_info',
                'get_past_items',
                'add_item',
                'update_item',
                'delete_item',
                'submit_new_order',
            ]
            if action in json_actions:
                result = getattr(self, action)(batch, data)
                return self.json_response(result)

        items = [self.normalize_row(row)
                 for row in batch.active_rows()]

        context = self.get_context_contact(batch)

        context.update({
            'batch': batch,
            'normalized_batch': self.normalize_batch(batch),
            'new_order_requires_customer': self.batch_handler.new_order_requires_customer(),
            'product_price_may_be_questionable': self.batch_handler.product_price_may_be_questionable(),
            'allow_contact_info_choice': self.batch_handler.allow_contact_info_choice(),
            'allow_contact_info_create': self.batch_handler.allow_contact_info_creation(),
            'order_items': items,
            'product_key_label': app.get_product_key_label(),
            'allow_unknown_product': (self.batch_handler.allow_unknown_product()
                                      and self.has_perm('create_unknown_product')),
            'pending_product_required_fields': self.get_pending_product_required_fields(),
            'unknown_product_confirm_price': self.rattail_config.getbool(
                'rattail.custorders', 'unknown_product.always_confirm_price'),
            'department_options': self.get_department_options(),
            'default_uom_choices': self.batch_handler.uom_choices_for_product(None),
            'default_uom': None,
            'allow_item_discounts': self.batch_handler.allow_item_discounts(),
            'allow_item_discounts_if_on_sale': self.batch_handler.allow_item_discounts_if_on_sale(),
            # nb. render quantity so that '10.0' => '10'
            'default_item_discount': app.render_quantity(
                self.batch_handler.get_default_item_discount()),
            'allow_past_item_reorder': self.batch_handler.allow_past_item_reorder(),
        })

        if self.batch_handler.allow_case_orders():
            context['default_uom'] = self.enum.UNIT_OF_MEASURE_CASE
        elif self.batch_handler.allow_unit_orders():
            context['default_uom'] = self.enum.UNIT_OF_MEASURE_EACH

        return self.render_to_response(template, context)

    def get_department_options(self):
        model = self.model
        departments = self.Session.query(model.Department)\
                                  .order_by(model.Department.name)\
                                  .all()
        options = []
        for department in departments:
            options.append({'label': department.name,
                            'value': department.uuid})
        return options

    def get_pending_product_required_fields(self):
        required = []
        for field in self.PENDING_PRODUCT_ENTRY_FIELDS:
            require = self.rattail_config.getbool('rattail.custorders',
                                                  f'unknown_product.fields.{field}.required')
            if require is None and field == 'description':
                require = True
            if require:
                required.append(field)
        return required

    def get_current_batch(self):
        user = self.request.user
        if not user:
            raise RuntimeError("this feature requires a user to be logged in")

        model = self.app.model
        try:
            # there should be at most *one* new batch per user
            batch = self.Session.query(model.CustomerOrderBatch)\
                                .filter(model.CustomerOrderBatch.mode == self.enum.CUSTORDER_BATCH_MODE_CREATING)\
                                .filter(model.CustomerOrderBatch.created_by == user)\
                                .filter(model.CustomerOrderBatch.executed == None)\
                                .one()

        except orm.exc.NoResultFound:
            # no batch yet for this user, so make one

            batch = self.batch_handler.make_batch(
                self.Session(), created_by=user,
                mode=self.enum.CUSTORDER_BATCH_MODE_CREATING)
            self.Session.add(batch)
            self.Session.flush()

        return batch

    def start_over_entirely(self, batch):
        self.batch_handler.do_delete(batch)
        self.Session.flush()

        # send user back to normal "create" page; a new batch will be generated
        # for them automatically
        route_prefix = self.get_route_prefix()
        url = self.request.route_url('{}.create'.format(route_prefix))
        return self.redirect(url)

    def delete_batch(self, batch):
        self.batch_handler.do_delete(batch)
        self.Session.flush()

        # set flash msg just to be more obvious
        self.request.session.flash("New customer order has been deleted.")

        # send user back to customer orders page, w/ no new batch generated
        url = self.get_index_url()
        return self.redirect(url)

    def customer_autocomplete(self):
        """
        Customer autocomplete logic, which invokes the handler.
        """
        # TODO: deprecate / remove this
        self.handler = self.batch_handler
        term = self.request.GET['term']
        return self.batch_handler.customer_autocomplete(self.Session(), term,
                                                        user=self.request.user)

    def person_autocomplete(self):
        """
        Person autocomplete logic, which invokes the handler.
        """
        # TODO: deprecate / remove this
        self.handler = self.batch_handler
        term = self.request.GET['term']
        return self.batch_handler.person_autocomplete(self.Session(), term,
                                                      user=self.request.user)

    def get_customer_info(self, batch, data):
        uuid = data.get('uuid')
        if not uuid:
            return {'error': "Must specify a customer UUID"}

        model = self.app.model
        customer = self.Session.get(model.Customer, uuid)
        if not customer:
            return {'error': "Customer not found"}

        return self.info_for_customer(batch, data, customer)

    def info_for_customer(self, batch, data, customer):

        # most info comes from handler
        info = self.batch_handler.get_customer_info(batch)

        # maybe add profile URL
        if info['person_uuid']:
            if self.request.has_perm('people.view_profile'):
                info['contact_profile_url'] = self.request.route_url(
                    'people.view_profile', uuid=info['person_uuid']),

        return info

    def assign_contact(self, batch, data):
        model = self.app.model
        kwargs = {}

        # this will either be a Person or Customer UUID
        uuid = data['uuid']

        if self.batch_handler.new_order_requires_customer():

            customer = self.Session.get(model.Customer, uuid)
            if not customer:
                return {'error': "Customer not found"}
            kwargs['customer'] = customer

        else:

            person = self.Session.get(model.Person, uuid)
            if not person:
                return {'error': "Person not found"}
            kwargs['person'] = person

        # invoke handler to assign contact
        try:
            self.batch_handler.assign_contact(batch, **kwargs)
        except ValueError as error:
            return {'error': str(error)}

        self.Session.flush()
        context = self.get_context_contact(batch)
        context['success'] = True
        return context

    def get_context_contact(self, batch):
        context = {
            'customer_uuid': batch.customer_uuid,
            'person_uuid': batch.person_uuid,
            'phone_number': batch.phone_number,
            'contact_display': batch.contact_name,
            'email_address': batch.email_address,
            'contact_phones': self.batch_handler.get_contact_phones(batch),
            'contact_emails': self.batch_handler.get_contact_emails(batch),
            'contact_notes': self.batch_handler.get_contact_notes(batch),
            'add_phone_number': bool(batch.get_param('add_phone_number')),
            'add_email_address': bool(batch.get_param('add_email_address')),
            'contact_profile_url': None,
            'new_customer_name': None,
            'new_customer_first_name': None,
            'new_customer_last_name': None,
            'new_customer_phone': None,
            'new_customer_email': None,
        }

        pending = batch.pending_customer
        if pending:
            context.update({
                'new_customer_first_name': pending.first_name,
                'new_customer_last_name': pending.last_name,
                'new_customer_name': pending.display_name,
                'new_customer_phone': pending.phone_number,
                'new_customer_email': pending.email_address,
            })

        # figure out if "contact is known" from user's perspective.
        # if we have a uuid then it's definitely known, otherwise if
        # we have a pending customer then it's definitely *not* known,
        # but if no pending customer yet then we can still "assume" it
        # is known, by default, until user specifies otherwise.
        contact = self.batch_handler.get_contact(batch)
        if contact:
            context['contact_is_known'] = True
        else:
            context['contact_is_known'] = not bool(pending)

        # maybe add profile URL
        if batch.person_uuid:
            if self.request.has_perm('people.view_profile'):
                context['contact_profile_url'] = self.request.route_url(
                    'people.view_profile', uuid=batch.person_uuid)

        return context

    def unassign_contact(self, batch, data):
        self.batch_handler.unassign_contact(batch)
        self.Session.flush()
        context = self.get_context_contact(batch)
        context['success'] = True
        return context

    def update_phone_number(self, batch, data):
        app = self.get_rattail_app()

        batch.phone_number = app.format_phone_number(data['phone_number'])

        if data.get('add_phone_number'):
            batch.set_param('add_phone_number', True)
        else:
            batch.clear_param('add_phone_number')

        self.Session.flush()
        return {
            'success': True,
            'phone_number': batch.phone_number,
            'add_phone_number': bool(batch.get_param('add_phone_number')),
        }

    def update_email_address(self, batch, data):

        batch.email_address = data['email_address']

        if data.get('add_email_address'):
            batch.set_param('add_email_address', True)
        else:
            batch.clear_param('add_email_address')

        self.Session.flush()
        return {
            'success': True,
            'email_address': batch.email_address,
            'add_email_address': bool(batch.get_param('add_email_address')),
        }

    def update_pending_customer(self, batch, data):

        try:
            self.batch_handler.update_pending_customer(batch, self.request.user,
                                                       data)
        except Exception as error:
            return {'error': str(error)}

        self.Session.flush()
        context = self.get_context_contact(batch)
        context['success'] = True
        return context

    def product_autocomplete(self):
        """
        Custom product autocomplete logic, which invokes the handler.
        """
        term = self.request.GET['term']

        # if handler defines custom autocomplete, use that
        handler = self.get_batch_handler()
        if handler.has_custom_product_autocomplete:
            return handler.custom_product_autocomplete(self.Session(), term,
                                                       user=self.request.user)

        # otherwise we use 'products.neworder' autocomplete
        app = self.get_rattail_app()
        autocomplete = app.get_autocompleter('products.neworder')
        return autocomplete.autocomplete(self.Session(), term)

    def get_product_info(self, batch, data):
        uuid = data.get('uuid')
        if not uuid:
            return {'error': "Must specify a product UUID"}

        model = self.app.model
        product = self.Session.get(model.Product, uuid)
        if not product:
            return {'error': "Product not found"}

        return self.info_for_product(batch, data, product)

    def uom_choices_for_product(self, product):
        return self.batch_handler.uom_choices_for_product(product)

    def uom_choices_for_row(self, row):
        return self.batch_handler.uom_choices_for_row(row)

    def info_for_product(self, batch, data, product):
        try:
            info = self.batch_handler.get_product_info(batch, product)
        except Exception as error:
            return {'error': str(error)}
        else:
            info['url'] = self.request.route_url('products.view', uuid=info['uuid'])
            app = self.get_rattail_app()
            return app.json_friendly(info)

    def get_past_items(self, batch, data):
        app = self.get_rattail_app()
        past_products = self.batch_handler.get_past_products(batch)
        past_items = []

        for product in past_products:
            try:
                item = self.batch_handler.get_product_info(batch, product)
            except:
                # nb. handler may raise error if product is "unsupported"
                pass
            else:
                item = app.json_friendly(item)
                past_items.append(item)

        return {'past_items': past_items}

    def normalize_batch(self, batch):
        return {
            'uuid': batch.uuid,
            'total_price': str(batch.total_price or 0),
            'total_price_display': "${:0.2f}".format(batch.total_price or 0),
            'status_code': batch.status_code,
            'status_text': batch.status_text,
        }

    def get_unit_price_display(self, obj):
        """
        Returns a display string for the given object's unit price.
        The object can be either a ``Product`` instance, or a batch
        row.
        """
        app = self.get_rattail_app()
        model = self.model
        if isinstance(obj, model.Product):
            products = app.get_products_handler()
            return products.render_price(obj.regular_price)
        else: # row
            return app.render_currency(obj.unit_price)

    def normalize_row(self, row):
        products_handler = self.app.get_products_handler()

        data = {
            'uuid': row.uuid,
            'sequence': row.sequence,
            'item_entry': row.item_entry,
            'product_uuid': row.product_uuid,
            'product_upc': str(row.product_upc or ''),
            'product_item_id': row.product_item_id,
            'product_scancode': row.product_scancode,
            'product_upc_pretty': row.product_upc.pretty() if row.product_upc else None,
            'product_brand': row.product_brand,
            'product_description': row.product_description,
            'product_size': row.product_size,
            'product_weighed': row.product_weighed,

            'case_quantity': self.app.render_quantity(row.case_quantity),
            'cases_ordered': self.app.render_quantity(row.cases_ordered),
            'units_ordered': self.app.render_quantity(row.units_ordered),
            'order_quantity': self.app.render_quantity(row.order_quantity),
            'order_uom': row.order_uom,
            'order_uom_choices': self.uom_choices_for_row(row),
            'discount_percent': self.app.render_quantity(row.discount_percent),

            'department_display': row.department_name,

            'unit_price': float(row.unit_price) if row.unit_price is not None else None,
            'unit_price_display': self.get_unit_price_display(row),
            'total_price': float(row.total_price) if row.total_price is not None else None,
            'total_price_display': self.app.render_currency(row.total_price),

            'status_code': row.status_code,
            'status_text': row.status_text,
        }

        if row.unit_regular_price:
            data['unit_regular_price'] = float(row.unit_regular_price)
            data['unit_regular_price_display'] = self.app.render_currency(row.unit_regular_price)

        if row.unit_sale_price:
            data['unit_sale_price'] = float(row.unit_sale_price)
            data['unit_sale_price_display'] = self.app.render_currency(row.unit_sale_price)
        if row.sale_ends:
            sale_ends = self.app.localtime(row.sale_ends, from_utc=True).date()
            data['sale_ends'] = str(sale_ends)
            data['sale_ends_display'] = self.app.render_date(sale_ends)

        if row.unit_sale_price and row.unit_price == row.unit_sale_price:
            data['pricing_reflects_sale'] = True

        if row.product or row.pending_product:
            data['product_full_description'] = products_handler.make_full_description(
                row.product or row.pending_product)

        if row.product:
            cost = row.product.cost
            if cost:
                data['vendor_display'] = cost.vendor.name
        elif row.pending_product:
            data['vendor_display'] = row.pending_product.vendor_name

        if row.pending_product:
            pending = row.pending_product
            data['pending_product'] = {
                'uuid': pending.uuid,
                'upc': str(pending.upc) if pending.upc is not None else None,
                'item_id': pending.item_id,
                'scancode': pending.scancode,
                'brand_name': pending.brand_name,
                'description': pending.description,
                'size': pending.size,
                'department_uuid': pending.department_uuid,
                'regular_price_amount': float(pending.regular_price_amount) if pending.regular_price_amount is not None else None,
                'vendor_name': pending.vendor_name,
                'vendor_item_code': pending.vendor_item_code,
                'unit_cost': float(pending.unit_cost) if pending.unit_cost is not None else None,
                'case_size': float(pending.case_size) if pending.case_size is not None else None,
                'notes': pending.notes,
            }

        case_price = self.batch_handler.get_case_price_for_row(row)
        data['case_price'] = float(case_price) if case_price is not None else None
        data['case_price_display'] = self.app.render_currency(case_price)

        if self.batch_handler.product_price_may_be_questionable():
            data['price_needs_confirmation'] = row.price_needs_confirmation

        key = self.app.get_product_key_field()
        if key == 'upc':
            data['product_key'] = data['product_upc_pretty']
        elif key == 'item_id':
            data['product_key'] = row.product_item_id
        elif key == 'scancode':
            data['product_key'] = row.product_scancode
        else: # TODO: this seems not useful
            data['product_key'] = getattr(row.product, key, data['product_upc_pretty'])

        if row.product:
            data.update({
                'product_url': self.request.route_url('products.view', uuid=row.product.uuid),
                'product_image_url': products_handler.get_image_url(row.product),
            })
        elif row.product_upc:
            data['product_image_url'] = products_handler.get_image_url(upc=row.product_upc)

        unit_uom = self.enum.UNIT_OF_MEASURE_POUND if data['product_weighed'] else self.enum.UNIT_OF_MEASURE_EACH
        if row.order_uom == self.enum.UNIT_OF_MEASURE_CASE:
            if row.case_quantity is None:
                case_qty = unit_qty = '??'
            else:
                case_qty = data['case_quantity']
                unit_qty = self.app.render_quantity(row.order_quantity * row.case_quantity)
            data.update({
                'order_quantity_display': "{} {} (&times; {} {} = {} {})".format(
                    data['order_quantity'],
                    self.enum.UNIT_OF_MEASURE[self.enum.UNIT_OF_MEASURE_CASE],
                    case_qty,
                    self.enum.UNIT_OF_MEASURE[unit_uom],
                    unit_qty,
                    self.enum.UNIT_OF_MEASURE[unit_uom]),
            })
        else:
            data.update({
                'order_quantity_display': "{} {}".format(
                    self.app.render_quantity(row.order_quantity),
                    self.enum.UNIT_OF_MEASURE[unit_uom]),
            })

        return data

    def add_item(self, batch, data):
        model = self.app.model

        order_quantity = decimal.Decimal(data.get('order_quantity') or '0')
        order_uom = data.get('order_uom')
        discount_percent = decimal.Decimal(data.get('discount_percent') or '0')

        if data.get('product_is_known'):

            uuid = data.get('product_uuid')
            if not uuid:
                return {'error': "Must specify a product UUID"}

            product = self.Session.get(model.Product, uuid)
            if not product:
                return {'error': "Product not found"}

            kwargs = {}
            if self.batch_handler.product_price_may_be_questionable():
                kwargs['price_needs_confirmation'] = data.get('price_needs_confirmation')

            if self.batch_handler.allow_item_discounts():
                kwargs['discount_percent'] = discount_percent

            row = self.batch_handler.add_product(batch, product,
                                                 order_quantity, order_uom,
                                                 **kwargs)

        else: # unknown product; add pending
            pending_info = dict(data['pending_product'])

            if 'upc' in pending_info:
                pending_info['upc'] = self.app.make_gpc(pending_info['upc'])

            for field in ('unit_cost', 'regular_price_amount', 'case_size'):
                if field in pending_info:
                    try:
                        pending_info[field] = decimal.Decimal(pending_info[field])
                    except decimal.InvalidOperation:
                        return {'error': f"Invalid entry for field: {field}"}

            pending_info['user'] = self.request.user

            kwargs = {}
            if self.batch_handler.allow_item_discounts():
                kwargs['discount_percent'] = discount_percent

            row = self.batch_handler.add_pending_product(batch,
                                                         pending_info,
                                                         order_quantity, order_uom,
                                                         **kwargs)

        self.Session.flush()
        return {'batch': self.normalize_batch(batch),
                'row': self.normalize_row(row)}

    def update_item(self, batch, data):
        uuid = data.get('uuid')
        if not uuid:
            return {'error': "Must specify a row UUID"}

        model = self.app.model
        row = self.Session.get(model.CustomerOrderBatchRow, uuid)
        if not row:
            return {'error': "Row not found"}

        if row not in batch.active_rows():
            return {'error': "Row is not active for the batch"}

        order_quantity = decimal.Decimal(data.get('order_quantity') or '0')
        order_uom = data.get('order_uom')
        discount_percent = decimal.Decimal(data.get('discount_percent') or '0')

        if data.get('product_is_known'):

            uuid = data.get('product_uuid')
            if not uuid:
                return {'error': "Must specify a product UUID"}

            product = self.Session.get(model.Product, uuid)
            if not product:
                return {'error': "Product not found"}

            row.item_entry = product.uuid
            row.product = product
            row.order_quantity = order_quantity
            row.order_uom = order_uom

            if self.batch_handler.product_price_may_be_questionable():
                row.price_needs_confirmation = data.get('price_needs_confirmation')

            if self.batch_handler.allow_item_discounts():
                row.discount_percent = discount_percent

            self.batch_handler.refresh_row(row)

        else: # product is not known

            # set these first, since row will be refreshed below
            row.order_quantity = order_quantity
            row.order_uom = order_uom

            if self.batch_handler.allow_item_discounts():
                row.discount_percent = discount_percent

            # nb. this will refresh the row
            pending_info = dict(data['pending_product'])
            self.batch_handler.update_pending_product(row, pending_info)

        self.Session.flush()
        self.Session.refresh(row)
        return {'batch': self.normalize_batch(batch),
                'row': self.normalize_row(row)}

    def delete_item(self, batch, data):

        uuid = data.get('uuid')
        if not uuid:
            return {'error': "Must specify a row UUID"}

        model = self.app.model
        row = self.Session.get(model.CustomerOrderBatchRow, uuid)
        if not row:
            return {'error': "Row not found"}

        if row not in batch.active_rows():
            return {'error': "Row is not active for this batch"}

        self.batch_handler.do_remove_row(row)
        return {'ok': True,
                'batch': self.normalize_batch(batch)}

    def submit_new_order(self, batch, data):

        reason = self.batch_handler.why_not_execute(batch, user=self.request.user)
        if reason:
            return {'error': reason}

        try:
            result = self.execute_new_order_batch(batch, data)
        except Exception as error:
            log.warning("failed to execute new order batch: %s", batch,
                        exc_info=True)
            return {'error': simple_error(error)}
        else:
            if not result:
                return {'error': "Batch failed to execute"}

        return {
            'ok': True,
            'next_url': self.get_next_url_after_submit_new_order(batch, result),
        }

    def get_next_url_after_submit_new_order(self, batch, result, **kwargs):
        model = self.model

        if isinstance(result, model.CustomerOrder):
            return self.get_action_url('view', result)

    def execute_new_order_batch(self, batch, data):
        return self.batch_handler.do_execute(batch, self.request.user)

    def fetch_order_data(self):
        app = self.get_rattail_app()
        model = self.model

        order = None
        uuid = self.request.GET.get('uuid')
        if uuid:
            order = self.Session.get(model.CustomerOrder, uuid)
        if not order:
            # raise self.notfound()
            return {'error': "Customer order not found"}

        address = None
        if self.batch_handler.new_order_requires_customer():
            contact = order.customer
        else:
            contact = order.person
        if contact and contact.address:
            a = contact.address
            address = {
                'street_1': a.street,
                'street_2': a.street2,
                'city': a.city,
                'state': a.state,
                'zip': a.zipcode,
            }

        # gather all the order items
        items = []
        grand_total = 0
        for item in order.items:
            item_data = {
                'uuid': item.uuid,
                'special_order': False, # TODO
                'product_description': item.product_description,
                'order_quantity': app.render_quantity(item.order_quantity),
                'department': item.department_name,
                'price': app.render_currency(item.unit_price),
                'total': app.render_currency(item.total_price),
            }
            items.append(item_data)
            grand_total += item.total_price

        return {
            'uuid': order.uuid,
            'id': order.id,
            'created_display': app.render_datetime(app.localtime(order.created, from_utc=True)),
            'contact_display': str(contact or ''),
            'address': address,
            'phone_display': str(contact.phone) if contact and contact.phone else "",
            'email_display': str(contact.email) if contact and contact.email else "",
            'items': items,
            'grand_total_display': app.render_currency(grand_total),
        }

    def configure_get_simple_settings(self):
        settings = [

            # customer handling
            {'section': 'rattail.custorders',
             'option': 'new_order_requires_customer',
             'type': bool},
            {'section': 'rattail.custorders',
             'option': 'new_orders.allow_contact_info_choice',
             'type': bool},
            {'section': 'rattail.custorders',
             'option': 'new_orders.allow_contact_info_create',
             'type': bool},

            # product handling
            {'section': 'rattail.custorders',
             'option': 'allow_case_orders',
             'type': bool},
            {'section': 'rattail.custorders',
             'option': 'allow_unit_orders',
             'type': bool},
            {'section': 'rattail.custorders',
             'option': 'product_price_may_be_questionable',
             'type': bool},
            {'section': 'rattail.custorders',
             'option': 'allow_item_discounts',
             'type': bool},
            {'section': 'rattail.custorders',
             'option': 'allow_item_discounts_if_on_sale',
             'type': bool},
            {'section': 'rattail.custorders',
             'option': 'default_item_discount',
             'type': float},
            {'section': 'rattail.custorders',
             'option': 'allow_past_item_reorder',
             'type': bool},

            # unknown products
            {'section': 'rattail.custorders',
             'option': 'allow_unknown_product',
             'type': bool},
            {'section': 'rattail.custorders',
             'option': 'unknown_product.always_confirm_price',
             'type': bool},
        ]

        for field in self.PENDING_PRODUCT_ENTRY_FIELDS:
            setting = {'section': 'rattail.custorders',
                       'option': f'unknown_product.fields.{field}.required',
                       'type': bool}
            if field == 'description':
                setting['default'] = True
            settings.append(setting)

        return settings

    def configure_get_context(self, **kwargs):
        context = super().configure_get_context(**kwargs)

        context['pending_product_fields'] = self.PENDING_PRODUCT_ENTRY_FIELDS

        return context

    @classmethod
    def defaults(cls, config):
        cls._order_defaults(config)
        cls._defaults(config)

    @classmethod
    def _order_defaults(cls, config):
        route_prefix = cls.get_route_prefix()
        url_prefix = cls.get_url_prefix()
        model_title = cls.get_model_title()
        model_title_plural = cls.get_model_title_plural()
        permission_prefix = cls.get_permission_prefix()

        config.add_tailbone_permission_group(permission_prefix, model_title_plural, overwrite=False)

        config.add_tailbone_permission(permission_prefix,
                                       f'{permission_prefix}.create_unknown_product',
                                       f"Create new {model_title} for unknown product")

        # add pseudo-index page for creating new custorder
        # (makes it available when building menus etc.)
        config.add_tailbone_index_page('{}.create'.format(route_prefix),
                                       "New {}".format(model_title),
                                       '{}.create'.format(permission_prefix))

        # person autocomplete
        config.add_route('{}.person_autocomplete'.format(route_prefix),
                         '{}/person-autocomplete'.format(url_prefix),
                         request_method='GET')
        config.add_view(cls, attr='person_autocomplete',
                        route_name='{}.person_autocomplete'.format(route_prefix),
                        renderer='json',
                        permission='people.list')

        # customer autocomplete
        config.add_route('{}.customer_autocomplete'.format(route_prefix),
                         '{}/customer-autocomplete'.format(url_prefix),
                         request_method='GET')
        config.add_view(cls, attr='customer_autocomplete',
                        route_name='{}.customer_autocomplete'.format(route_prefix),
                        renderer='json',
                        permission='customers.list')

        # custom product autocomplete
        config.add_route('{}.product_autocomplete'.format(route_prefix),
                         '{}/product-autocomplete'.format(url_prefix),
                         request_method='GET')
        config.add_view(cls, attr='product_autocomplete',
                        route_name='{}.product_autocomplete'.format(route_prefix),
                        renderer='json',
                        permission='products.list')

        # fetch order data
        config.add_route(f'{route_prefix}.fetch_order_data',
                         f'{url_prefix}/fetch-order-data')
        config.add_view(cls, attr='fetch_order_data',
                        route_name=f'{route_prefix}.fetch_order_data',
                        renderer='json',
                        permission=f'{permission_prefix}.view')


# TODO: deprecate / remove this
CustomerOrdersView = CustomerOrderView


def defaults(config, **kwargs):
    base = globals()

    CustomerOrderView = kwargs.get('CustomerOrderView', base['CustomerOrderView'])
    CustomerOrderView.defaults(config)


def includeme(config):
    defaults(config)
