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
Views for POS batches
"""

from rattail.db.model import POSBatch, POSBatchRow

from webhelpers2.html import HTML

from tailbone.views.batch import BatchMasterView


class POSBatchView(BatchMasterView):
    """
    Master view for POS batches
    """
    model_class = POSBatch
    model_row_class = POSBatchRow
    default_handler_spec = 'rattail.batch.pos:POSBatchHandler'
    route_prefix = 'batch.pos'
    url_prefix = '/batch/pos'
    creatable = False
    editable = False
    cloneable = True
    refreshable = False
    rows_deletable = False
    rows_bulk_deletable = False

    labels = {
        'terminal_id': "Terminal ID",
        'fs_tender_total': "FS Tender Total",
    }

    grid_columns = [
        'id',
        'created',
        'terminal_id',
        'cashier',
        'customer',
        'rowcount',
        'sales_total',
        'void',
        'status_code',
        'executed',
    ]

    form_fields = [
        'id',
        'terminal_id',
        'cashier',
        'customer',
        'customer_is_member',
        'customer_is_employee',
        'params',
        'rowcount',
        'sales_total',
        'taxes',
        'tender_total',
        'fs_tender_total',
        'balance',
        'void',
        'training_mode',
        'status_code',
        'created',
        'created_by',
        'executed',
        'executed_by',
    ]

    row_grid_columns = [
        'sequence',
        'row_type',
        'item_entry',
        'description',
        'reg_price',
        'txn_price',
        'quantity',
        'sales_total',
        'tender_total',
        'tax_code',
        'user',
    ]

    row_form_fields = [
        'sequence',
        'row_type',
        'item_entry',
        'product',
        'description',
        'department_number',
        'department_name',
        'reg_price',
        'cur_price',
        'cur_price_type',
        'cur_price_start',
        'cur_price_end',
        'txn_price',
        'txn_price_adjusted',
        'quantity',
        'sales_total',
        'tax_code',
        'tender_total',
        'tender',
        'void',
        'status_code',
        'timestamp',
        'user',
    ]

    def configure_grid(self, g):
        super().configure_grid(g)
        model = self.model

        # terminal_id
        g.set_label('terminal_id', "Terminal")
        if 'terminal_id' in g.filters:
            g.filters['terminal_id'].label = self.labels.get('terminal_id', "Terminal ID")

        # cashier
        def join_cashier(q):
            return q.outerjoin(model.Employee,
                               model.Employee.uuid == model.POSBatch.cashier_uuid)\
                    .outerjoin(model.Person,
                               model.Person.uuid == model.Employee.person_uuid)
        g.set_joiner('cashier', join_cashier)
        g.set_sorter('cashier', model.Person.display_name)

        # customer
        g.set_link('customer')
        g.set_joiner('customer', lambda q: q.outerjoin(model.Customer))
        g.set_sorter('customer', model.Customer.name)

        g.set_link('created')
        g.set_link('created_by')

        g.set_type('sales_total', 'currency')
        g.set_type('tender_total', 'currency')
        g.set_type('fs_tender_total', 'currency')

        # executed
        # nb. default view should show "all recent" batches regardless
        # of execution (i think..)
        if 'executed' in g.filters:
            g.filters['executed'].default_active = False

    def grid_extra_class(self, batch, i):
        if batch.void:
            return 'warning'
        if (batch.training_mode
            or batch.status_code == batch.STATUS_SUSPENDED):
            return 'notice'

    def configure_form(self, f):
        super().configure_form(f)
        app = self.get_rattail_app()

        # cashier
        f.set_renderer('cashier', self.render_employee)

        # customer
        f.set_renderer('customer', self.render_customer)

        f.set_type('sales_total', 'currency')
        f.set_type('tender_total', 'currency')
        f.set_type('fs_tender_total', 'currency')

        if self.viewing:
            f.set_renderer('taxes', self.render_taxes)

        f.set_renderer('balance', lambda batch, field: app.render_currency(batch.get_balance()))

    def render_taxes(self, batch, field):
        route_prefix = self.get_route_prefix()

        factory = self.get_grid_factory()
        g = factory(
            self.request,
            key=f'{route_prefix}.taxes',
            data=[],
            columns=[
                'code',
                'description',
                'rate',
                'total',
            ],
        )

        return HTML.literal(
            g.render_table_element(data_prop='taxesData'))

    def template_kwargs_view(self, **kwargs):
        kwargs = super().template_kwargs_view(**kwargs)
        app = self.get_rattail_app()
        batch = kwargs['instance']

        taxes = []
        for btax in batch.taxes.values():
            data = {
                'uuid': btax.uuid,
                'code': btax.tax_code,
                'description': btax.tax.description,
                'rate': app.render_percent(btax.tax_rate),
                'total': app.render_currency(btax.tax_total),
            }
            taxes.append(data)
        taxes.sort(key=lambda t: t['code'])
        kwargs['taxes_data'] = taxes

        kwargs['execute_enabled'] = False
        kwargs['why_not_execute'] = "POS batch must be executed at POS"

        return kwargs

    def configure_row_grid(self, g):
        super().configure_row_grid(g)

        g.set_enum('row_type', self.enum.POS_ROW_TYPE)

        g.set_type('quantity', 'quantity')
        g.set_type('reg_price', 'currency')
        g.set_type('txn_price', 'currency')
        g.set_type('sales_total', 'currency')
        g.set_type('tender_total', 'currency')

        g.set_link('product')
        g.set_link('description')

    def row_grid_extra_class(self, row, i):
        if row.void:
            return 'warning'

    def configure_row_form(self, f):
        super().configure_row_form(f)

        f.set_enum('row_type', self.enum.POS_ROW_TYPE)

        f.set_renderer('product', self.render_product)
        f.set_renderer('tender', self.render_tender)

        f.set_type('quantity', 'quantity')
        f.set_type('reg_price', 'currency')
        f.set_type('txn_price', 'currency')
        f.set_type('sales_total', 'currency')
        f.set_type('tender_total', 'currency')

        f.set_renderer('user', self.render_user)

    @classmethod
    def defaults(cls, config):
        cls._batch_defaults(config)
        cls._defaults(config)
        cls._pos_batch_defaults(config)

    @classmethod
    def _pos_batch_defaults(cls, config):
        rattail_config = config.registry.settings.get('rattail_config')

        if rattail_config.getbool('tailbone', 'expose_pos_permissions',
                                  default=False):

            config.add_tailbone_permission_group('pos', "POS", overwrite=False)

            config.add_tailbone_permission('pos', 'pos.test_error',
                                           "Force error to test error handling")
            config.add_tailbone_permission('pos', 'pos.ring_sales',
                                           "Make transactions (ring up sales)")
            config.add_tailbone_permission('pos', 'pos.override_price',
                                           "Override price for any item")
            config.add_tailbone_permission('pos', 'pos.del_customer',
                                           "Remove customer from current transaction")
            # config.add_tailbone_permission('pos', 'pos.resume',
            #                                "Resume previously-suspended transaction")
            config.add_tailbone_permission('pos', 'pos.toggle_training',
                                           "Start/end training mode")
            config.add_tailbone_permission('pos', 'pos.suspend',
                                           "Suspend current transaction")
            config.add_tailbone_permission('pos', 'pos.swap_customer',
                                           "Swap customer for current transaction")
            config.add_tailbone_permission('pos', 'pos.void_txn',
                                           "Void current transaction")


def defaults(config, **kwargs):
    base = globals()

    POSBatchView = kwargs.get('POSBatchView', base['POSBatchView'])
    POSBatchView.defaults(config)


def includeme(config):
    defaults(config)
