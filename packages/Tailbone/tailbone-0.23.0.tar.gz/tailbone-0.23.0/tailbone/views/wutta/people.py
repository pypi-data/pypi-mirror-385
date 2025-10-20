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
Person Views
"""

import colander
import sqlalchemy as sa
from webhelpers2.html import HTML

from wuttaweb.views import people as wutta
from tailbone.views import people as tailbone
from tailbone.db import Session
from rattail.db.model import Person
from tailbone.grids import Grid


class PersonView(wutta.PersonView):
    """
    This is the first attempt at blending newer Wutta views with
    legacy Tailbone config.

    So, this is a Wutta-based view but it should be included by a
    Tailbone app configurator.
    """
    model_class = Person
    Session = Session

    labels = {
        'display_name': "Full Name",
    }

    grid_columns = [
        'display_name',
        'first_name',
        'last_name',
        'phone',
        'email',
        'merge_requested',
    ]

    filter_defaults = {
        'display_name': {'active': True, 'verb': 'contains'},
    }
    sort_defaults = 'display_name'

    form_fields = [
        'first_name',
        'middle_name',
        'last_name',
        'display_name',
        'phone',
        'email',
        # TODO
        # 'address',
    ]

    ##############################
    # CRUD methods
    ##############################

    # TODO: must use older grid for now, to render filters correctly
    def make_grid(self, **kwargs):
        """ """
        return Grid(self.request, **kwargs)

    def configure_grid(self, g):
        """ """
        super().configure_grid(g)

        # display_name
        g.set_link('display_name')

        # merge_requested
        g.set_label('merge_requested', "MR")
        g.set_renderer('merge_requested', self.render_merge_requested)

    def configure_form(self, f):
        """ """
        super().configure_form(f)

        # email
        if self.creating or self.editing:
            f.remove('email')
        else:
            # nb. avoid colanderalchemy
            f.set_node('email', colander.String())

        # phone
        if self.creating or self.editing:
            f.remove('phone')
        else:
            # nb. avoid colanderalchemy
            f.set_node('phone', colander.String())

    ##############################
    # support methods
    ##############################

    def render_merge_requested(self, person, key, value, session=None):
        """ """
        model = self.app.model
        session = session or self.Session()
        merge_request = session.query(model.MergePeopleRequest)\
                               .filter(sa.or_(
                                   model.MergePeopleRequest.removing_uuid == person.uuid,
                                   model.MergePeopleRequest.keeping_uuid == person.uuid))\
                               .filter(model.MergePeopleRequest.merged == None)\
                               .first()
        if merge_request:
            return HTML.tag('span',
                            class_='has-text-danger has-text-weight-bold',
                            title="A merge has been requested for this person.",
                            c="MR")


def defaults(config, **kwargs):
    kwargs.setdefault('PersonView', PersonView)
    tailbone.defaults(config, **kwargs)


def includeme(config):
    defaults(config)
