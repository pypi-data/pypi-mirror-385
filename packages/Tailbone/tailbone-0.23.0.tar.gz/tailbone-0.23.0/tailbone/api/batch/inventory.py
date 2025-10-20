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
Tailbone Web API - Inventory Batches
"""

import decimal

import sqlalchemy as sa

from rattail import pod
from rattail.db.model import InventoryBatch, InventoryBatchRow

from cornice import Service

from tailbone.api.batch import APIBatchView, APIBatchRowView


class InventoryBatchViews(APIBatchView):

    model_class = InventoryBatch
    default_handler_spec = 'rattail.batch.inventory:InventoryBatchHandler'
    route_prefix = 'inventory'
    permission_prefix = 'batch.inventory'
    collection_url_prefix = '/inventory-batches'
    object_url_prefix = '/inventory-batch'
    supports_toggle_complete = True

    def normalize(self, batch):
        data = super().normalize(batch)

        data['mode'] = batch.mode
        data['mode_display'] = self.enum.INVENTORY_MODE.get(batch.mode)
        if data['mode_display'] is None and batch.mode is not None:
            data['mode_display'] = str(batch.mode)

        data['reason_code'] = batch.reason_code

        return data

    def count_modes(self):
        """
        Retrieve info about the available batch count modes.
        """
        permission_prefix = self.get_permission_prefix()
        if self.request.is_root:
            modes = self.batch_handler.get_count_modes()
        else:
            modes = self.batch_handler.get_allowed_count_modes(
                self.Session(), self.request.user,
                permission_prefix=permission_prefix)
        return modes

    def adjustment_reasons(self):
        """
        Retrieve info about the available "reasons" for inventory adjustment
        batches.
        """
        raw_reasons = self.batch_handler.get_adjustment_reasons(self.Session())
        reasons = []
        for reason in raw_reasons:
            reasons.append({
                'uuid': reason.uuid,
                'code': reason.code,
                'description': reason.description,
                'hidden': reason.hidden,
            })
        return reasons

    @classmethod
    def defaults(cls, config):
        cls._defaults(config)
        cls._batch_defaults(config)
        cls._inventory_defaults(config)

    @classmethod
    def _inventory_defaults(cls, config):
        route_prefix = cls.get_route_prefix()
        permission_prefix = cls.get_permission_prefix()
        collection_url_prefix = cls.get_collection_url_prefix()

        # get count modes
        count_modes = Service(name='{}.count_modes'.format(route_prefix),
                              path='{}/count-modes'.format(collection_url_prefix))
        count_modes.add_view('GET', 'count_modes', klass=cls,
                             permission='{}.list'.format(permission_prefix))
        config.add_cornice_service(count_modes)

        # get adjustment reasons
        adjustment_reasons = Service(name='{}.adjustment_reasons'.format(route_prefix),
                                     path='{}/adjustment-reasons'.format(collection_url_prefix))
        adjustment_reasons.add_view('GET', 'adjustment_reasons', klass=cls,
                                    permission='{}.list'.format(permission_prefix))
        config.add_cornice_service(adjustment_reasons)


class InventoryBatchRowViews(APIBatchRowView):

    model_class = InventoryBatchRow
    default_handler_spec = 'rattail.batch.inventory:InventoryBatchHandler'
    route_prefix = 'inventory.rows'
    permission_prefix = 'batch.inventory'
    collection_url_prefix = '/inventory-batch-rows'
    object_url_prefix = '/inventory-batch-row'
    editable = True
    supports_quick_entry = True

    def normalize(self, row):
        batch = row.batch
        data = super().normalize(row)
        app = self.get_rattail_app()

        data['item_id'] = row.item_id
        data['upc'] = str(row.upc)
        data['upc_pretty'] = row.upc.pretty() if row.upc else None
        data['brand_name'] = row.brand_name
        data['description'] = row.description
        data['size'] = row.size
        data['full_description'] = row.product.full_description if row.product else row.description
        data['image_url'] = pod.get_image_url(self.rattail_config, row.upc) if row.upc else None
        data['case_quantity'] = app.render_quantity(row.case_quantity or 1)

        data['cases'] = row.cases
        data['units'] = row.units
        data['unit_uom'] = 'LB' if row.product and row.product.weighed else 'EA'
        data['quantity_display'] = "{} {}".format(
            app.render_quantity(row.cases or row.units),
            'CS' if row.cases else data['unit_uom'])

        data['allow_cases'] = self.batch_handler.allow_cases(batch)

        return data

    def update_object(self, row, data):
        """
        Supplements the default logic as follows:

        Converts certain fields within the data, to proper "native" types.
        """
        data = dict(data)

        # convert some data types as needed
        if 'cases' in data:
            if data['cases'] == '':
                data['cases'] = None
            elif data['cases']:
                data['cases'] = decimal.Decimal(data['cases'])
        if 'units' in data:
            if data['units'] == '':
                data['units'] = None
            elif data['units']:
                data['units'] = decimal.Decimal(data['units'])

        # update row per usual
        try:
            row = super().update_object(row, data)
        except sa.exc.DataError as error:
            # detect when user scans barcode for cases/units field
            if hasattr(error, 'orig'):
                orig = type(error.orig)
                if hasattr(orig, '__name__'):
                    # nb. this particular error is from psycopg2
                    if orig.__name__ == 'NumericValueOutOfRange':
                        return {'error': "Numeric value out of range"}
            raise
        return row


def defaults(config, **kwargs):
    base = globals()

    InventoryBatchViews = kwargs.get('InventoryBatchViews', base['InventoryBatchViews'])
    InventoryBatchViews.defaults(config)

    InventoryBatchRowViews = kwargs.get('InventoryBatchRowViews', base['InventoryBatchRowViews'])
    InventoryBatchRowViews.defaults(config)


def includeme(config):
    defaults(config)
