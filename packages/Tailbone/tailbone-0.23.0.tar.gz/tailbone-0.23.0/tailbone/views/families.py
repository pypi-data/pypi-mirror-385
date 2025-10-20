# -*- coding: utf-8; -*-
################################################################################
#
#  Rattail -- Retail Software Framework
#  Copyright © 2010-2022 Lance Edgar
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
Family Views
"""

from __future__ import unicode_literals, absolute_import

from rattail.db import model

from tailbone.views import MasterView


class FamilyView(MasterView):
    """
    Master view for the Family class.
    """
    model_class = model.Family
    model_title_plural = "Families"
    route_prefix = 'families'
    has_versions = True
    results_downloadable = True
    grid_key = 'families'

    grid_columns = [
        'code',
        'name',
    ]

    form_fields = [
        'code',
        'name',
    ]

    has_rows = True
    model_row_class = model.Product

    row_grid_columns = [
        '_product_key_',
        'brand',
        'description',
        'size',
        'department',
        'vendor',
        'regular_price',
        'current_price',
    ]

    def configure_grid(self, g):
        super(FamilyView, self).configure_grid(g)
        g.filters['name'].default_active = True
        g.filters['name'].default_verb = 'contains'

        g.set_sort_defaults('code')

        g.set_link('code')
        g.set_link('name')

    def get_row_data(self, family):
        return self.Session.query(model.Product)\
                           .filter(model.Product.family == family)

    def get_parent(self, product):
        return product.family

    def configure_row_grid(self, g):
        super(FamilyView, self).configure_row_grid(g)

        app = self.get_rattail_app()
        self.handler = app.get_products_handler()
        g.set_renderer('regular_price', self.render_price)
        g.set_renderer('current_price', self.render_price)

        key = self.rattail_config.product_key()
        field = self.product_key_fields.get(key, key)
        g.set_sort_defaults(field)

    def render_price(self, product, field):
        if not product.not_for_sale:
            price = product[field]
            if price:
                return self.handler.render_price(price)

    def row_view_action_url(self, product, i):
        return self.request.route_url('products.view', uuid=product.uuid)

# TODO: deprecate / remove this
FamiliesView = FamilyView


def defaults(config, **kwargs):
    base = globals()

    FamilyView = kwargs.get('FamilyView', base['FamilyView'])
    FamilyView.defaults(config)


def includeme(config):
    defaults(config)
