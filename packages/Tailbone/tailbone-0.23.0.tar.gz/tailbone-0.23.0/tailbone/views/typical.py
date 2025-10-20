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
Typical views for convenient includes
"""


def defaults(config, **kwargs):
    mod = lambda spec: kwargs.get(spec, spec)

    # main tables
    config.include(mod('tailbone.views.brands'))
    config.include(mod('tailbone.views.categories'))
    config.include(mod('tailbone.views.customergroups'))
    config.include(mod('tailbone.views.customers'))
    config.include(mod('tailbone.views.custorders'))
    config.include(mod('tailbone.views.departments'))
    config.include(mod('tailbone.views.employees'))
    config.include(mod('tailbone.views.families'))
    config.include(mod('tailbone.views.members'))
    config.include(mod('tailbone.views.products'))
    config.include(mod('tailbone.views.purchases'))
    config.include(mod('tailbone.views.reportcodes'))
    config.include(mod('tailbone.views.stores'))
    config.include(mod('tailbone.views.subdepartments'))
    config.include(mod('tailbone.views.taxes'))
    config.include(mod('tailbone.views.tenders'))
    config.include(mod('tailbone.views.uoms'))
    config.include(mod('tailbone.views.vendors'))

    # batches
    config.include(mod('tailbone.views.batch.handheld'))
    config.include(mod('tailbone.views.batch.importer'))
    config.include(mod('tailbone.views.batch.inventory'))
    config.include(mod('tailbone.views.batch.pos'))
    config.include(mod('tailbone.views.batch.vendorcatalog'))
    config.include(mod('tailbone.views.purchasing'))


def includeme(config):
    defaults(config)
