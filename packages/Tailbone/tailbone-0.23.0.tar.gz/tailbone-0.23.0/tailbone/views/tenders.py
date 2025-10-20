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
Views for tenders
"""

from rattail.db.model import Tender

from tailbone.views import MasterView


class TenderView(MasterView):
    """
    Master view for the Tender class.
    """
    model_class = Tender
    has_versions = True

    grid_columns = [
        'code',
        'name',
        'is_cash',
        'is_foodstamp',
        'allow_cash_back',
        'kick_drawer',
    ]

    form_fields = [
        'code',
        'name',
        'is_cash',
        'is_foodstamp',
        'allow_cash_back',
        'kick_drawer',
        'notes',
        'disabled',
    ]

    def configure_grid(self, g):
        super().configure_grid(g)

        g.set_link('code')

        g.set_link('name')
        g.set_sort_defaults('name')

    def grid_extra_class(self, tender, i):
        if tender.disabled:
            return 'warning'

    def configure_form(self, f):
        super().configure_form(f)

        f.set_type('notes', 'text')


def defaults(config, **kwargs):
    base = globals()

    TenderView = kwargs.get('TenderView', base['TenderView'])
    TenderView.defaults(config)


def includeme(config):
    defaults(config)
