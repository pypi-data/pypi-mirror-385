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
Tailbone Web API - Label Views
"""

from __future__ import unicode_literals, absolute_import

from rattail.db.model import LabelProfile

from tailbone.api import APIMasterView


class LabelProfileView(APIMasterView):
    """
    API views for Label Profile data
    """
    model_class = LabelProfile
    collection_url_prefix = '/label-profiles'
    object_url_prefix = '/label-profile'


def defaults(config, **kwargs):
    base = globals()

    LabelProfileView = kwargs.get('LabelProfileView', base['LabelProfileView'])
    LabelProfileView.defaults(config)


def includeme(config):
    defaults(config)
