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
User Views
"""

from wuttaweb.views import users as wutta
from tailbone.views import users as tailbone
from tailbone.db import Session
from rattail.db.model import User
from tailbone.grids import Grid


class UserView(wutta.UserView):
    """
    This is the first attempt at blending newer Wutta views with
    legacy Tailbone config.

    So, this is a Wutta-based view but it should be included by a
    Tailbone app configurator.
    """
    model_class = User
    Session = Session

    # TODO: must use older grid for now, to render filters correctly
    def make_grid(self, **kwargs):
        """ """
        return Grid(self.request, **kwargs)


def defaults(config, **kwargs):
    kwargs.setdefault('UserView', UserView)
    tailbone.defaults(config, **kwargs)


def includeme(config):
    defaults(config)
