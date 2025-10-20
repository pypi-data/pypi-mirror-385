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
Base class for purchasing batch views
"""

import warnings

from rattail.db.model import PurchaseBatch, PurchaseBatchRow

import colander
from deform import widget as dfwidget
from webhelpers2.html import tags, HTML

from tailbone import forms
from tailbone.views.batch import BatchMasterView


class PurchasingBatchView(BatchMasterView):
    """
    Master view base class, for purchase batches.  The views for both
    "ordering" and "receiving" batches will inherit from this.
    """
    model_class = PurchaseBatch
    model_row_class = PurchaseBatchRow
    default_handler_spec = 'rattail.batch.purchase:PurchaseBatchHandler'
    supports_new_product = False
    cloneable = True

    labels = {
        'po_total': "PO Total",
    }

    grid_columns = [
        'id',
        'vendor',
        'department',
        'buyer',
        'date_ordered',
        'created',
        'created_by',
        'rowcount',
        'status_code',
        'executed',
    ]

    form_fields = [
        'id',
        'store',
        'buyer',
        'vendor',
        'description',
        'workflow',
        'department',
        'purchase',
        'vendor_email',
        'vendor_fax',
        'vendor_contact',
        'vendor_phone',
        'date_ordered',
        'date_received',
        'po_number',
        'po_total',
        'invoice_date',
        'invoice_number',
        'invoice_total',
        'notes',
        'created',
        'created_by',
        'status_code',
        'complete',
        'executed',
        'executed_by',
    ]

    row_labels = {
        'upc': "UPC",
        'item_id': "Item ID",
        'brand_name': "Brand",
        'case_quantity': "Case Size",
        'po_line_number': "PO Line Number",
        'po_unit_cost': "PO Unit Cost",
        'po_case_size': "PO Case Size",
        'po_total': "PO Total",
    }

    # row_grid_columns = [
    #     'sequence',
    #     'upc',
    #     # 'item_id',
    #     'brand_name',
    #     'description',
    #     'size',
    #     'cases_ordered',
    #     'units_ordered',
    #     'cases_received',
    #     'units_received',
    #     'po_total',
    #     'invoice_total',
    #     'credits',
    #     'status_code',
    # ]

    row_form_fields = [
        'upc',
        'item_id',
        'product',
        'brand_name',
        'description',
        'size',
        'case_quantity',
        'ordered',
        'cases_ordered',
        'units_ordered',
        'received',
        'cases_received',
        'units_received',
        'damaged',
        'cases_damaged',
        'units_damaged',
        'expired',
        'cases_expired',
        'units_expired',
        'mispick',
        'cases_mispick',
        'units_mispick',
        'missing',
        'cases_missing',
        'units_missing',
        'po_line_number',
        'po_unit_cost',
        'po_total',
        'invoice_line_number',
        'invoice_unit_cost',
        'invoice_total',
        'invoice_total_calculated',
        'status_code',
        'credits',
    ]

    @property
    def batch_mode(self):
        raise NotImplementedError("Please define `batch_mode` for your purchasing batch view")

    def get_supported_workflows(self):
        """
        Return the supported "create batch" workflows.
        """
        enum = self.app.enum
        if self.batch_mode == enum.PURCHASE_BATCH_MODE_ORDERING:
            return self.batch_handler.supported_ordering_workflows()
        elif self.batch_mode == enum.PURCHASE_BATCH_MODE_RECEIVING:
            return self.batch_handler.supported_receiving_workflows()
        elif self.batch_mode == enum.PURCHASE_BATCH_MODE_COSTING:
            return self.batch_handler.supported_costing_workflows()
        raise ValueError("unknown batch mode")

    def allow_any_vendor(self):
        """
        Return boolean indicating whether creating a batch for "any"
        vendor is allowed, vs. only supported vendors.
        """
        enum = self.app.enum

        if self.batch_mode == enum.PURCHASE_BATCH_MODE_ORDERING:
            return self.batch_handler.allow_ordering_any_vendor()

        elif self.batch_mode == enum.PURCHASE_BATCH_MODE_RECEIVING:
            value = self.config.get_bool('rattail.batch.purchase.allow_receiving_any_vendor')
            if value is not None:
                return value
            value = self.config.get_bool('rattail.batch.purchase.supported_vendors_only')
            if value is not None:
                warnings.warn("setting rattail.batch.purchase.supported_vendors_only is deprecated; "
                              "please use rattail.batch.purchase.allow_receiving_any_vendor instead",
                              DeprecationWarning)
                # nb. must negate this setting
                return not value
            return False

        raise ValueError("unknown batch mode")

    def get_supported_vendors(self):
        """
        Return the supported vendors for creating a batch.
        """
        return []

    def create(self, form=None, **kwargs):
        """
        Custom view for creating a new batch.  We split the process
        into two steps, 1) choose workflow and 2) create batch.  This
        is because the specific form details for creating a batch will
        depend on which "type" of batch creation is to be done, and
        it's much easier to keep conditional logic for that in the
        server instead of client-side etc.
        """
        model = self.app.model
        enum = self.app.enum
        route_prefix = self.get_route_prefix()

        workflows = self.get_supported_workflows()
        valid_workflows = [workflow['workflow_key']
                           for workflow in workflows]

        # if user has already identified their desired workflow, then
        # we can just farm out to the default logic.  we will of
        # course configure our form differently, based on workflow,
        # but this create() method at least will not need
        # customization for that.
        if self.request.matched_route.name.endswith('create_workflow'):

            redirect = self.redirect(self.request.route_url(f'{route_prefix}.create'))

            # however we do have one more thing to check - the workflow
            # requested must of course be valid!
            workflow_key = self.request.matchdict['workflow_key']
            if workflow_key not in valid_workflows:
                self.request.session.flash(f"Not a supported workflow: {workflow_key}", 'error')
                raise redirect

            # also, we require vendor to be correctly identified.  if
            # someone e.g. navigates to a URL by accident etc. we want
            # to gracefully handle and redirect
            uuid = self.request.matchdict['vendor_uuid']
            vendor = self.Session.get(model.Vendor, uuid)
            if not vendor:
                self.request.session.flash("Invalid vendor selection.  "
                                           "Please choose an existing vendor.",
                                           'warning')
                raise redirect

            # okay now do the normal thing, per workflow
            return super().create(**kwargs)

        # on the other hand, if caller provided a form, that means we are in
        # the middle of some other custom workflow, e.g. "add child to truck
        # dump parent" or some such.  in which case we also defer to the normal
        # logic, so as to not interfere with that.
        if form:
            return super().create(form=form, **kwargs)

        # okay, at this point we need the user to select a vendor and workflow
        self.creating = True
        context = {}

        # form to accept user choice of vendor/workflow
        schema = colander.Schema()
        schema.add(colander.SchemaNode(colander.String(), name='vendor'))
        schema.add(colander.SchemaNode(colander.String(), name='workflow',
                                       validator=colander.OneOf(valid_workflows)))
        factory = self.get_form_factory()
        form = factory(schema=schema, request=self.request)

        # configure vendor field
        vendor_handler = self.app.get_vendor_handler()
        if self.allow_any_vendor():
            # user may choose *any* available vendor
            use_dropdown = vendor_handler.choice_uses_dropdown()
            if use_dropdown:
                vendors = self.Session.query(model.Vendor)\
                                      .order_by(model.Vendor.id)\
                                      .all()
                vendor_values = [(vendor.uuid, f"({vendor.id}) {vendor.name}")
                                 for vendor in vendors]
                form.set_widget('vendor', dfwidget.SelectWidget(values=vendor_values))
                if len(vendors) == 1:
                    form.set_default('vendor', vendors[0].uuid)
            else:
                vendor_display = ""
                if self.request.method == 'POST':
                    if self.request.POST.get('vendor'):
                        vendor = self.Session.get(model.Vendor, self.request.POST['vendor'])
                        if vendor:
                            vendor_display = str(vendor)
                vendors_url = self.request.route_url('vendors.autocomplete')
                form.set_widget('vendor', forms.widgets.JQueryAutocompleteWidget(
                    field_display=vendor_display, service_url=vendors_url))
        else: # only "supported" vendors allowed
            vendors = self.get_supported_vendors()
            vendor_values = [(vendor.uuid, vendor_handler.render_vendor(vendor))
                             for vendor in vendors]
            form.set_widget('vendor', dfwidget.SelectWidget(values=vendor_values))
        form.set_validator('vendor', self.valid_vendor_uuid)

        # configure workflow field
        values = [(workflow['workflow_key'], workflow['display'])
                  for workflow in workflows]
        form.set_widget('workflow',
                        dfwidget.SelectWidget(values=values))
        if len(workflows) == 1:
            form.set_default('workflow', workflows[0]['workflow_key'])

        form.submit_label = "Continue"
        form.cancel_url = self.get_index_url()

        # if form validates, that means user has chosen a creation
        # type, so we just redirect to the appropriate "new batch of
        # type X" page
        if form.validate():
            workflow_key = form.validated['workflow']
            vendor_uuid = form.validated['vendor']
            url = self.request.route_url(f'{route_prefix}.create_workflow',
                                         workflow_key=workflow_key,
                                         vendor_uuid=vendor_uuid)
            raise self.redirect(url)

        context['form'] = form
        if hasattr(form, 'make_deform_form'):
            context['dform'] = form.make_deform_form()
        return self.render_to_response('create', context)

    def query(self, session):
        model = self.model
        return session.query(model.PurchaseBatch)\
                      .filter(model.PurchaseBatch.mode == self.batch_mode)

    def configure_grid(self, g):
        super().configure_grid(g)
        model = self.model

        # vendor
        g.set_link('vendor')
        g.set_joiner('vendor', lambda q: q.join(model.Vendor))
        g.set_sorter('vendor', model.Vendor.name)
        g.set_filter('vendor', model.Vendor.name,
                     default_active=True, default_verb='contains')

        # department
        g.set_joiner('department', lambda q: q.join(model.Department))
        g.set_filter('department', model.Department.name)
        g.set_sorter('department', model.Department.name)

        g.set_joiner('buyer', lambda q: q.join(model.Employee).join(model.Person))
        g.set_filter('buyer', model.Person.display_name)
        g.set_sorter('buyer', model.Person.display_name)

        # TODO: we used to include the 'complete' filter by default, but it
        # seems to likely be confusing for newcomers, so it is no longer
        # default.  not sure if there are any other implications...?
        # if self.request.has_perm('{}.execute'.format(self.get_permission_prefix())):
        #     g.filters['complete'].default_active = True
        #     g.filters['complete'].default_verb = 'is_true'

        # invoice_total
        g.set_type('invoice_total', 'currency')
        g.set_label('invoice_total', "Total")

        # invoice_total_calculated
        g.set_type('invoice_total_calculated', 'currency')
        g.set_label('invoice_total_calculated', "Total")

        g.set_label('date_ordered', "Ordered")
        g.set_label('date_received', "Received")

    def grid_extra_class(self, batch, i):
        if batch.status_code == batch.STATUS_UNKNOWN_PRODUCT:
            return 'notice'

#     def make_form(self, batch, **kwargs):
#         if self.creating:
#             kwargs.setdefault('id', 'new-purchase-form')
#         form = super(PurchasingBatchView, self).make_form(batch, **kwargs)
#         return form

    def configure_common_form(self, f):
        super().configure_common_form(f)

        # po_total
        if self.creating:
            f.remove_fields('po_total',
                            'po_total_calculated')
        else:
            f.set_readonly('po_total')
            f.set_type('po_total', 'currency')
            f.set_readonly('po_total_calculated')
            f.set_type('po_total_calculated', 'currency')

    def configure_form(self, f):
        super().configure_form(f)
        model = self.app.model
        enum = self.app.enum
        route_prefix = self.get_route_prefix()

        today = self.app.today()
        batch = f.model_instance
        workflow = self.request.matchdict.get('workflow_key')
        vendor_handler = self.app.get_vendor_handler()

        # mode
        f.set_enum('mode', enum.PURCHASE_BATCH_MODE)

        # workflow
        if self.creating:
            if workflow:
                f.set_widget('workflow', dfwidget.HiddenWidget())
                f.set_default('workflow', workflow)
                f.set_hidden('workflow')
                # nb. show readonly '_workflow'
                f.insert_after('workflow', '_workflow')
                f.set_readonly('_workflow')
                f.set_renderer('_workflow', self.render_workflow)
            else:
                f.set_readonly('workflow')
                f.set_renderer('workflow', self.render_workflow)
        else:
            f.remove('workflow')

        # store
        single_store = self.config.single_store()
        if self.creating:
            f.replace('store', 'store_uuid')
            if single_store:
                store = self.config.get_store(self.Session())
                f.set_widget('store_uuid', dfwidget.HiddenWidget())
                f.set_default('store_uuid', store.uuid)
                f.set_hidden('store_uuid')
            else:
                f.set_widget('store_uuid', dfwidget.SelectWidget(values=self.get_store_values()))
                f.set_label('store_uuid', "Store")
        else:
            f.set_readonly('store')
            f.set_renderer('store', self.render_store)

        # purchase
        f.set_renderer('purchase', self.render_purchase)
        if self.editing:
            f.set_readonly('purchase')

        # vendor
        # fs.vendor.set(renderer=forms.renderers.VendorFieldRenderer,
        #               attrs={'selected': 'vendor_selected',
        #                      'cleared': 'vendor_cleared'})
        f.set_renderer('vendor', self.render_vendor)
        if self.creating:
            f.replace('vendor', 'vendor_uuid')
            f.set_label('vendor_uuid', "Vendor")
            use_dropdown = vendor_handler.choice_uses_dropdown()
            if use_dropdown:
                vendors = self.Session.query(model.Vendor)\
                                      .order_by(model.Vendor.id)
                vendor_values = [(vendor.uuid, "({}) {}".format(vendor.id, vendor.name))
                                 for vendor in vendors]
                f.set_widget('vendor_uuid', dfwidget.SelectWidget(values=vendor_values))
            else:
                vendor_display = ""
                if self.request.method == 'POST':
                    if self.request.POST.get('vendor_uuid'):
                        vendor = self.Session.get(model.Vendor, self.request.POST['vendor_uuid'])
                        if vendor:
                            vendor_display = str(vendor)
                vendors_url = self.request.route_url('vendors.autocomplete')
                f.set_widget('vendor_uuid', forms.widgets.JQueryAutocompleteWidget(
                    field_display=vendor_display, service_url=vendors_url))
            f.set_validator('vendor_uuid', self.valid_vendor_uuid)
        elif self.editing:
            f.set_readonly('vendor')

        # department
        f.set_renderer('department', self.render_department)
        if self.creating:
            if 'department' in f.fields:
                f.replace('department', 'department_uuid')
                f.set_node('department_uuid', colander.String())
                dept_options = self.get_department_options()
                dept_values = [(v, k) for k, v in dept_options]
                dept_values.insert(0, ('', "(unspecified)"))
                f.set_widget('department_uuid', dfwidget.SelectWidget(values=dept_values))
                f.set_required('department_uuid', False)
                f.set_label('department_uuid', "Department")
        else:
            f.set_readonly('department')

        # buyer
        if 'buyer' in f:
            f.set_renderer('buyer', self.render_buyer)
            if self.creating or self.editing:
                f.replace('buyer', 'buyer_uuid')
                f.set_node('buyer_uuid', colander.String(), missing=colander.null)
                buyer_display = ""
                if self.request.method == 'POST':
                    if self.request.POST.get('buyer_uuid'):
                        buyer = self.Session.get(model.Employee, self.request.POST['buyer_uuid'])
                        if buyer:
                            buyer_display = str(buyer)
                elif self.creating:
                    buyer = self.app.get_employee(self.request.user)
                    if buyer:
                        buyer_display = str(buyer)
                        f.set_default('buyer_uuid', buyer.uuid)
                elif self.editing:
                    buyer_display = str(batch.buyer or '')
                buyers_url = self.request.route_url('employees.autocomplete')
                f.set_widget('buyer_uuid', forms.widgets.JQueryAutocompleteWidget(
                    field_display=buyer_display, service_url=buyers_url))
                f.set_label('buyer_uuid', "Buyer")

        # order_file
        if self.creating:
            f.set_type('order_file', 'file', required=False)
        else:
            f.set_readonly('order_file')
            f.set_renderer('order_file', self.render_downloadable_file)

        # order_parser_key
        if self.creating:
            kwargs = {}
            if 'vendor_uuid' in self.request.matchdict:
                vendor = self.Session.get(model.Vendor,
                                          self.request.matchdict['vendor_uuid'])
                if vendor:
                    kwargs['vendor'] = vendor
            parsers = vendor_handler.get_supported_order_parsers(**kwargs)
            parser_values = [(p.key, p.title) for p in parsers]
            if len(parsers) == 1:
                f.set_default('order_parser_key', parsers[0].key)
            f.set_widget('order_parser_key', dfwidget.SelectWidget(values=parser_values))
            f.set_label('order_parser_key', "Order Parser")
        else:
            f.remove_field('order_parser_key')

        # invoice_file
        if self.creating:
            f.set_type('invoice_file', 'file', required=False)
        else:
            f.set_readonly('invoice_file')
            f.set_renderer('invoice_file', self.render_downloadable_file)

        # invoice_parser_key
        if self.creating:
            kwargs = {}

            if 'vendor_uuid' in self.request.matchdict:
                vendor = self.Session.get(model.Vendor,
                                          self.request.matchdict['vendor_uuid'])
                if vendor:
                    kwargs['vendor'] = vendor

            parsers = self.batch_handler.get_supported_invoice_parsers(**kwargs)
            parser_values = [(p.key, p.display) for p in parsers]
            if len(parsers) == 1:
                f.set_default('invoice_parser_key', parsers[0].key)

            f.set_widget('invoice_parser_key', dfwidget.SelectWidget(values=parser_values))
        else:
            f.remove_field('invoice_parser_key')

        # date_ordered
        f.set_type('date_ordered', 'date_jquery')
        if self.creating:
            f.set_default('date_ordered', today)

        # date_received
        f.set_type('date_received', 'date_jquery')
        if self.creating:
            f.set_default('date_received', today)

        # invoice_date
        f.set_type('invoice_date', 'date_jquery')

        # po_number
        f.set_label('po_number', "PO Number")

        # invoice_total
        f.set_readonly('invoice_total')
        f.set_type('invoice_total', 'currency')

        # invoice_total_calculated
        f.set_readonly('invoice_total_calculated')
        f.set_type('invoice_total_calculated', 'currency')

        # vendor_email
        f.set_readonly('vendor_email')
        f.set_renderer('vendor_email', self.render_vendor_email)

        # vendor_fax
        f.set_readonly('vendor_fax')
        f.set_renderer('vendor_fax', self.render_vendor_fax)

        # vendor_contact
        f.set_readonly('vendor_contact')
        f.set_renderer('vendor_contact', self.render_vendor_contact)

        # vendor_phone
        f.set_readonly('vendor_phone')
        f.set_renderer('vendor_phone', self.render_vendor_phone)

        if self.creating:
            f.remove_fields('po_total',
                            'invoice_total',
                            'complete',
                            'vendor_email',
                            'vendor_fax',
                            'vendor_phone',
                            'vendor_contact',
                            'status_code')

        # tweak some things if we are in "step 2" of creating new batch
        if self.creating and workflow:

            # display vendor but do not allow changing
            vendor = self.Session.get(model.Vendor, self.request.matchdict['vendor_uuid'])
            if not vendor:
                raise ValueError(f"vendor not found: {self.request.matchdict['vendor_uuid']}")
            f.set_readonly('vendor_uuid')
            f.set_default('vendor_uuid', str(vendor))

            # cancel should take us back to choosing a workflow
            f.cancel_url = self.request.route_url(f'{route_prefix}.create')

    def render_workflow(self, batch, field):
        key = self.request.matchdict['workflow_key']
        info = self.get_workflow_info(key)
        if info:
            return info['display']

    def get_workflow_info(self, key):
        enum = self.app.enum
        if self.batch_mode == enum.PURCHASE_BATCH_MODE_ORDERING:
            return self.batch_handler.ordering_workflow_info(key)
        elif self.batch_mode == enum.PURCHASE_BATCH_MODE_RECEIVING:
            return self.batch_handler.receiving_workflow_info(key)
        elif self.batch_mode == enum.PURCHASE_BATCH_MODE_COSTING:
            return self.batch_handler.costing_workflow_info(key)
        raise ValueError("unknown batch mode")

    def render_store(self, batch, field):
        store = batch.store
        if not store:
            return ""
        text = "({}) {}".format(store.id, store.name)
        url = self.request.route_url('stores.view', uuid=store.uuid)
        return tags.link_to(text, url)

    def render_purchase(self, batch, field):
        model = self.model

        # default logic can only render the "normal" (built-in)
        # purchase field; anything else must be handled by view
        # supplement if possible
        if field != 'purchase':
            for supp in self.iter_view_supplements():
                renderer = getattr(supp, f'render_purchase_{field}', None)
                if renderer:
                    return renderer(batch)

        # nothing to render if no purchase found
        purchase = getattr(batch, field)
        if not purchase:
            return

        # render link to native purchase, if possible
        text = str(purchase)
        if isinstance(purchase, model.Purchase):
            url = self.request.route_url('purchases.view', uuid=purchase.uuid)
            return tags.link_to(text, url)

        # otherwise just render purchase as-is
        return text

    def render_vendor_email(self, batch, field):
        if batch.vendor.email:
            return batch.vendor.email.address

    def render_vendor_fax(self, batch, field):
        return self.get_vendor_fax_number(batch)

    def render_vendor_contact(self, batch, field):
        if batch.vendor.contact:
            return str(batch.vendor.contact)

    def render_vendor_phone(self, batch, field):
        return self.get_vendor_phone_number(batch)

    def render_department(self, batch, field):
        department = batch.department
        if not department:
            return ""
        if department.number:
            text = "({}) {}".format(department.number, department.name)
        else:
            text = department.name
        url = self.request.route_url('departments.view', uuid=department.uuid)
        return tags.link_to(text, url)

    def render_buyer(self, batch, field):
        employee = batch.buyer
        if not employee:
            return ""
        text = str(employee)
        if self.request.has_perm('employees.view'):
            url = self.request.route_url('employees.view', uuid=employee.uuid)
            return tags.link_to(text, url)
        return text

    def get_store_values(self):
        model = self.model
        stores = self.Session.query(model.Store)\
                             .order_by(model.Store.id)
        return [(s.uuid, "({}) {}".format(s.id, s.name))
                for s in stores]

    def get_vendors(self):
        model = self.model
        return self.Session.query(model.Vendor)\
                           .order_by(model.Vendor.name)

    def get_vendor_values(self):
        vendors = self.get_vendors()
        return [(v.uuid, "({}) {}".format(v.id, v.name))
                for v in vendors]

    def get_buyers(self):
        model = self.model
        return self.Session.query(model.Employee)\
                           .join(model.Person)\
                           .filter(model.Employee.status == self.enum.EMPLOYEE_STATUS_CURRENT)\
                           .order_by(model.Person.display_name)

    def get_buyer_values(self):
        buyers = self.get_buyers()
        return [(b.uuid, str(b))
                for b in buyers]

    def get_department_options(self):
        model = self.model
        departments = self.Session.query(model.Department).order_by(model.Department.number)
        return [('{} {}'.format(d.number, d.name), d.uuid) for d in departments]

    def get_vendor_phone_number(self, batch):
        for phone in batch.vendor.phones:
            if phone.type == 'Voice':
                return phone.number

    def get_vendor_fax_number(self, batch):
        for phone in batch.vendor.phones:
            if phone.type == 'Fax':
                return phone.number

    def get_batch_kwargs(self, batch, **kwargs):
        kwargs = super().get_batch_kwargs(batch, **kwargs)
        model = self.app.model

        kwargs['mode'] = self.batch_mode
        kwargs['workflow'] = self.request.POST['workflow']
        kwargs['truck_dump'] = batch.truck_dump
        kwargs['order_parser_key'] = batch.order_parser_key
        kwargs['invoice_parser_key'] = batch.invoice_parser_key

        if batch.store:
            kwargs['store'] = batch.store
        elif batch.store_uuid:
            kwargs['store_uuid'] = batch.store_uuid

        if batch.truck_dump_batch:
            kwargs['truck_dump_batch'] = batch.truck_dump_batch
        elif batch.truck_dump_batch_uuid:
            kwargs['truck_dump_batch_uuid'] = batch.truck_dump_batch_uuid

        if batch.vendor:
            kwargs['vendor'] = batch.vendor
        elif batch.vendor_uuid:
            kwargs['vendor_uuid'] = batch.vendor_uuid

        # must pull vendor from URL if it was not in form data
        if 'vendor_uuid' not in kwargs and 'vendor' not in kwargs:
            if 'vendor_uuid' in self.request.matchdict:
                kwargs['vendor_uuid'] = self.request.matchdict['vendor_uuid']

        if batch.department:
            kwargs['department'] = batch.department
        elif batch.department_uuid:
            kwargs['department_uuid'] = batch.department_uuid

        if batch.buyer:
            kwargs['buyer'] = batch.buyer
        elif batch.buyer_uuid:
            kwargs['buyer_uuid'] = batch.buyer_uuid

        kwargs['po_number'] = batch.po_number
        kwargs['po_total'] = batch.po_total

        # TODO: should these always get set?
        if self.batch_mode == self.enum.PURCHASE_BATCH_MODE_ORDERING:
            kwargs['date_ordered'] = batch.date_ordered
        elif self.batch_mode == self.enum.PURCHASE_BATCH_MODE_RECEIVING:
            kwargs['date_ordered'] = batch.date_ordered
            kwargs['date_received'] = batch.date_received
            kwargs['invoice_number'] = batch.invoice_number
        elif self.batch_mode == self.enum.PURCHASE_BATCH_MODE_COSTING:
            kwargs['invoice_date'] = batch.invoice_date
            kwargs['invoice_number'] = batch.invoice_number

        if self.batch_mode in (self.enum.PURCHASE_BATCH_MODE_RECEIVING,
                               self.enum.PURCHASE_BATCH_MODE_COSTING):
            field = self.batch_handler.get_purchase_order_fieldname()
            if field == 'purchase':
                purchase = batch.purchase
                if not purchase and batch.purchase_uuid:
                    purchase = self.Session.get(model.Purchase, batch.purchase_uuid)
                    assert purchase
                if purchase:
                    kwargs['purchase'] = purchase
                    kwargs['buyer'] = purchase.buyer
                    kwargs['buyer_uuid'] = purchase.buyer_uuid
                    kwargs['date_ordered'] = purchase.date_ordered
                    kwargs['po_total'] = purchase.po_total
            elif hasattr(batch, field):
                kwargs[field] = getattr(batch, field)

        return kwargs

#     def template_kwargs_view(self, **kwargs):
#         kwargs = super(PurchasingBatchView, self).template_kwargs_view(**kwargs)
#         vendor = kwargs['batch'].vendor
#         kwargs['vendor_cost_count'] = Session.query(model.ProductCost)\
#                                              .filter(model.ProductCost.vendor == vendor)\
#                                              .count()
#         kwargs['vendor_cost_threshold'] = self.rattail_config.getint(
#             'tailbone', 'purchases.order_form.vendor_cost_warning_threshold', default=699)
#         return kwargs

    def template_kwargs_create(self, **kwargs):
        kwargs['purchases_field'] = 'purchase_uuid'
        return kwargs

#     def get_row_data(self, batch):
#         query = super(PurchasingBatchView, self).get_row_data(batch)
#         return query.options(orm.joinedload(model.PurchaseBatchRow.credits))

    def configure_row_grid(self, g):
        super().configure_row_grid(g)

        g.set_type('upc', 'gpc')
        g.set_type('cases_ordered', 'quantity')
        g.set_type('units_ordered', 'quantity')
        g.set_type('cases_shipped', 'quantity')
        g.set_type('units_shipped', 'quantity')
        g.set_type('cases_received', 'quantity')
        g.set_type('units_received', 'quantity')
        g.set_type('po_total', 'currency')
        g.set_type('po_total_calculated', 'currency')
        g.set_type('credits', 'boolean')

        # we only want the grid columns to have abbreviated labels,
        # but *not* the filters
        # TODO: would be nice to somehow make this simpler
        g.set_label('department_name', "Department")
        g.filters['department_name'].label = "Department Name"
        g.set_label('cases_ordered', "Cases Ord.")
        g.filters['cases_ordered'].label = "Cases Ordered"
        g.set_label('units_ordered', "Units Ord.")
        g.filters['units_ordered'].label = "Units Ordered"
        g.set_label('cases_shipped', "Cases Shp.")
        g.filters['cases_shipped'].label = "Cases Shipped"
        g.set_label('units_shipped', "Units Shp.")
        g.filters['units_shipped'].label = "Units Shipped"
        g.set_label('cases_received', "Cases Rec.")
        g.filters['cases_received'].label = "Cases Received"
        g.set_label('units_received', "Units Rec.")
        g.filters['units_received'].label = "Units Received"

        # catalog_unit_cost
        g.set_renderer('catalog_unit_cost', self.render_row_grid_cost)
        g.set_label('catalog_unit_cost', "Catalog Cost")
        g.filters['catalog_unit_cost'].label = "Catalog Unit Cost"

        # po_unit_cost
        g.set_renderer('po_unit_cost', self.render_row_grid_cost)
        g.set_label('po_unit_cost', "PO Cost")
        g.filters['po_unit_cost'].label = "PO Unit Cost"

        # invoice_unit_cost
        g.set_renderer('invoice_unit_cost', self.render_row_grid_cost)
        g.set_label('invoice_unit_cost', "Invoice Cost")
        g.filters['invoice_unit_cost'].label = "Invoice Unit Cost"

        # invoice_total
        g.set_type('invoice_total', 'currency')
        g.set_label('invoice_total', "Total")

        # invoice_total_calculated
        g.set_type('invoice_total_calculated', 'currency')
        g.set_label('invoice_total_calculated', "Total")

        g.set_label('po_total', "Total")
        g.set_label('credits', "Credits?")

        g.set_link('upc')
        g.set_link('vendor_code')
        g.set_link('description')

    def render_row_grid_cost(self, row, field):
        cost = getattr(row, field)
        if cost is None:
            return ""
        return "{:0,.3f}".format(cost)

    def make_row_grid_tools(self, batch):
        return self.make_default_row_grid_tools(batch)

    def row_grid_extra_class(self, row, i):
        if row.status_code in (row.STATUS_PRODUCT_NOT_FOUND,
                               row.STATUS_COST_NOT_FOUND):
            return 'warning'
        if row.status_code in (row.STATUS_INCOMPLETE,
                               row.STATUS_CASE_QUANTITY_DIFFERS,
                               row.STATUS_ORDERED_RECEIVED_DIFFER,
                               row.STATUS_TRUCKDUMP_UNCLAIMED,
                               row.STATUS_TRUCKDUMP_PARTCLAIMED,
                               row.STATUS_OUT_OF_STOCK,
                               row.STATUS_ON_PO_NOT_INVOICE,
                               row.STATUS_ON_INVOICE_NOT_PO,
                               row.STATUS_COST_INCREASE,
                               row.STATUS_DID_NOT_RECEIVE):
            return 'notice'

    def configure_row_form(self, f):
        super().configure_row_form(f)
        row = f.model_instance
        if self.creating:
            batch = self.get_instance()
        else:
            batch = self.get_parent(row)

        # readonly fields
        f.set_readonly('case_quantity')

        # quantity fields
        f.set_renderer('ordered', self.render_row_quantity)
        f.set_renderer('shipped', self.render_row_quantity)
        f.set_renderer('received', self.render_row_quantity)
        f.set_renderer('damaged', self.render_row_quantity)
        f.set_renderer('expired', self.render_row_quantity)
        f.set_renderer('mispick', self.render_row_quantity)
        f.set_renderer('missing', self.render_row_quantity)

        f.set_type('case_quantity', 'quantity')
        f.set_type('po_case_size', 'quantity')
        f.set_type('invoice_case_size', 'quantity')
        f.set_type('cases_ordered', 'quantity')
        f.set_type('units_ordered', 'quantity')
        f.set_type('cases_shipped', 'quantity')
        f.set_type('units_shipped', 'quantity')
        f.set_type('cases_received', 'quantity')
        f.set_type('units_received', 'quantity')
        f.set_type('cases_damaged', 'quantity')
        f.set_type('units_damaged', 'quantity')
        f.set_type('cases_expired', 'quantity')
        f.set_type('units_expired', 'quantity')
        f.set_type('cases_mispick', 'quantity')
        f.set_type('units_mispick', 'quantity')
        f.set_type('cases_missing', 'quantity')
        f.set_type('units_missing', 'quantity')

        # currency fields
        # nb. we only show "total" fields as currency, but not case or
        # unit cost fields, b/c currency is rounded to 2 places
        f.set_type('po_total', 'currency')
        f.set_type('po_total_calculated', 'currency')

        # upc
        f.set_type('upc', 'gpc')

        # invoice total
        f.set_readonly('invoice_total')
        f.set_type('invoice_total', 'currency')
        f.set_label('invoice_total', "Invoice Total (Orig.)")

        # invoice total_calculated
        f.set_readonly('invoice_total_calculated')
        f.set_type('invoice_total_calculated', 'currency')
        f.set_label('invoice_total_calculated', "Invoice Total (Calc.)")

        # credits
        f.set_readonly('credits')
        if self.viewing:
            f.set_renderer('credits', self.render_row_credits)

        if self.creating:
            f.remove_fields(
                'upc',
                'product',
                'po_total',
                'invoice_total',
            )
            if self.batch_mode == self.enum.PURCHASE_BATCH_MODE_ORDERING:
                f.remove_fields('cases_received',
                                'units_received')
            elif self.batch_mode == self.enum.PURCHASE_BATCH_MODE_RECEIVING:
                f.remove_fields('cases_ordered',
                                'units_ordered')

        elif self.editing:
            f.set_readonly('upc')
            f.set_readonly('item_id')
            f.set_readonly('product')
            f.set_renderer('product', self.render_product)

            # TODO: what's up with this again?
            # f.remove_fields('po_total',
            #                 'invoice_total',
            #                 'status_code')

        elif self.viewing:
            if row.product:
                f.remove_fields('brand_name',
                                'description',
                                'size')
                f.set_renderer('product', self.render_product)
            else:
                f.remove_field('product')

    def render_row_quantity(self, row, field):
        app = self.get_rattail_app()
        cases = getattr(row, 'cases_{}'.format(field))
        units = getattr(row, 'units_{}'.format(field))
        # nb. do not render anything if empty quantities
        if cases or units:
            return app.render_cases_units(cases, units)

    def make_row_credits_grid(self, row):
        route_prefix = self.get_route_prefix()
        factory = self.get_grid_factory()

        g = factory(
            self.request,
            key=f'{route_prefix}.row_credits',
            data=[],
            columns=[
                'credit_type',
                'shorted',
                'credit_total',
                'expiration_date',
                # 'mispick_upc',
                # 'mispick_brand_name',
                # 'mispick_description',
                # 'mispick_size',
            ],
            labels={
                'credit_type': "Type",
                'shorted': "Quantity",
                'credit_total': "Total",
                # 'mispick_upc': "Mispick UPC",
                # 'mispick_brand_name': "MP Brand",
                # 'mispick_description': "MP Description",
                # 'mispick_size': "MP Size",
            })

        g.set_type('credit_total', 'currency')

        if not self.batch_handler.allow_expired_credits():
            g.remove('expiration_date')

        return g

    def render_row_credits(self, row, field):
        g = self.make_row_credits_grid(row)
        return HTML.literal(
            g.render_table_element(data_prop='rowData.credits'))

#     def before_create_row(self, form):
#         row = form.fieldset.model
#         batch = self.get_instance()
#         batch.add_row(row)
#         # TODO: this seems heavy-handed but works..
#         row.product_uuid = self.item_lookup(form.fieldset.item_lookup.value)

#     def after_create_row(self, row):
#         self.handler.refresh_row(row)

    def save_edit_row_form(self, form):
        """
        Supplements or overrides the default logic, as follows:

        *Ordering Mode*

        So far, we only allow updating the ``cases_ordered`` and/or
        ``units_ordered`` quantities; therefore the form data should have one
        or both of those fields.

        This data is then passed to the
        :meth:`~rattail:rattail.batch.purchase.PurchaseBatchHandler.update_row_quantity()`
        method of the batch handler.

        Note that the "normal" logic for this method is not invoked at all, for
        ordering batches.

        .. note::
           There is some logic in place for receiving mode, which sort of tries
           to update the overall invoice total for the batch, since the form
           data might cause those to need adjustment.  However the logic is
           incomplete as of this writing.

        .. todo::
           Need to fully implement ``save_edit_row_form()`` for receiving batch.
        """
        row = form.model_instance
        batch = row.batch

        if batch.mode == self.enum.PURCHASE_BATCH_MODE_ORDERING:

            # figure out which values need updating
            form_data = self.form_deserialized
            data = {}
            for key in ('cases_ordered', 'units_ordered'):
                if key in form_data:
                    # this is really to convert/avoid colander.null, but the
                    # handler method also assumes that if we pass a value, it
                    # will not be None
                    data[key] = form_data[key] or 0
            if data:

                # let handler do the actual updating
                self.handler.update_row_quantity(row, **data)

        else: # *not* ordering mode

            if batch.mode == self.enum.PURCHASE_BATCH_MODE_RECEIVING:

                # TODO: should stop doing it this way! (use the ordering mode way instead)
                # first undo any totals previously in effect for the row
                if row.invoice_total:
                    # TODO: pretty sure this should update the `_calculated` value instead?
                    # TODO: also, should update the value again after the super() call
                    batch.invoice_total -= row.invoice_total

            # do the "normal" save logic...
            row = super().save_edit_row_form(form)

            # TODO: is this needed?
            # self.handler.refresh_row(row)

        return row

#     def redirect_after_create_row(self, row):
#         self.request.session.flash("Added item: {} {}".format(row.upc.pretty(), row.product))
#         return self.redirect(self.request.current_route_url())

    # TODO: seems like this should be master behavior, controlled by setting?
    def redirect_after_edit_row(self, row, **kwargs):
        parent = self.get_parent(row)
        return self.redirect(self.get_action_url('view', parent))

#     def get_execute_success_url(self, batch, result, **kwargs):
#         # if batch execution yielded a Purchase, redirect to it
#         if isinstance(result, model.Purchase):
#             return self.request.route_url('purchases.view', uuid=result.uuid)

#         # otherwise just view batch again
#         return self.get_action_url('view', batch)

    @classmethod
    def defaults(cls, config):
        cls._purchase_batch_defaults(config)
        cls._batch_defaults(config)
        cls._defaults(config)

    @classmethod
    def _purchase_batch_defaults(cls, config):
        route_prefix = cls.get_route_prefix()
        url_prefix = cls.get_url_prefix()
        permission_prefix = cls.get_permission_prefix()

        # new batch using workflow X
        config.add_route(f'{route_prefix}.create_workflow',
                         f'{url_prefix}/new/{{workflow_key}}/{{vendor_uuid}}')
        config.add_view(cls, attr='create',
                        route_name=f'{route_prefix}.create_workflow',
                        permission=f'{permission_prefix}.create')


class NewProduct(colander.Schema):

    item_id = colander.SchemaNode(colander.String())

    description = colander.SchemaNode(colander.String())
