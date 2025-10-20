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
Views for employee shifts
"""

import datetime

from rattail.db import model
from rattail.time import localtime
from rattail.util import hours_as_decimal

from webhelpers2.html import tags, HTML

from tailbone.views import MasterView


class ShiftViewMixin:

    def render_shift_length(self, shift, field):
        if not shift.start_time or not shift.end_time:
            return ""
        if shift.end_time < shift.start_time:
            return "??"
        app = self.get_rattail_app()
        length = shift.end_time - shift.start_time
        return HTML.tag('span',
                        title="{} hrs".format(hours_as_decimal(length)),
                        c=[app.render_duration(delta=length)])


class ScheduledShiftView(MasterView, ShiftViewMixin):
    """
    Master view for employee scheduled shifts.
    """
    model_class = model.ScheduledShift
    url_prefix = '/shifts/scheduled'

    grid_columns = [
        'employee',
        'store',
        'start_time',
        'end_time',
        'length',
    ]

    form_fields = [
        'employee',
        'store',
        'start_time',
        'end_time',
        'length',
    ]

    def configure_grid(self, g):
        g.joiners['employee'] = lambda q: q.join(model.Employee).join(model.Person)
        g.filters['employee'] = g.make_filter('employee', model.Person.display_name,
                                              default_active=True, default_verb='contains')

        g.set_sort_defaults('start_time', 'desc')

        g.set_renderer('length', self.render_shift_length)

        g.set_label('employee', "Employee Name")

    def configure_form(self, f):
        super().configure_form(f)

        f.set_renderer('length', self.render_shift_length)

# TODO: deprecate / remove this
ScheduledShiftsView = ScheduledShiftView


class WorkedShiftView(MasterView, ShiftViewMixin):
    """
    Master view for employee worked shifts.
    """
    model_class = model.WorkedShift
    url_prefix = '/shifts/worked'
    results_downloadable_xlsx = True
    has_versions = True

    grid_columns = [
        'employee',
        'store',
        'start_time',
        'end_time',
        'length',
    ]

    form_fields = [
        'employee',
        'store',
        'start_time',
        'end_time',
        'length',
    ]

    def configure_grid(self, g):
        super().configure_grid(g)
        model = self.model

        # employee
        g.set_joiner('employee', lambda q: q.join(model.Employee).join(model.Person))
        g.set_sorter('employee', model.Person.display_name)
        g.set_filter('employee', model.Person.display_name)

        # store
        g.set_joiner('store', lambda q: q.join(model.Store))
        g.set_sorter('store', model.Store.name)
        g.set_filter('store', model.Store.name)

        # TODO: these sorters should be automatic once we fix the schema
        g.set_sorter('start_time', model.WorkedShift.punch_in)
        g.set_sorter('end_time', model.WorkedShift.punch_out)
        # TODO: same goes for these renderers
        g.set_type('start_time', 'datetime')
        g.set_type('end_time', 'datetime')
        # (but we'll still have to set this)
        g.set_sort_defaults('start_time', 'desc')

        g.set_renderer('length', self.render_shift_length)

        g.set_label('employee', "Employee Name")
        g.set_label('store', "Store Name")
        g.set_label('punch_in', "Start Time")
        g.set_label('punch_out', "End Time")

    def get_instance_title(self, shift):
        time = shift.start_time or shift.end_time
        date = localtime(self.rattail_config, time).date()
        return "WorkedShift: {}, {}".format(shift.employee, date)

    def configure_form(self, f):
        super().configure_form(f)

        f.set_readonly('employee')
        f.set_renderer('employee', self.render_employee)

        f.set_renderer('length', self.render_shift_length)
        if self.editing:
            f.remove('length')

    def render_employee(self, shift, field):
        employee = shift.employee
        if not employee:
            return ""
        text = str(employee)
        url = self.request.route_url('employees.view', uuid=employee.uuid)
        return tags.link_to(text, url)

    def get_xlsx_fields(self):
        fields = super().get_xlsx_fields()

        # add employee name
        i = fields.index('employee_uuid')
        fields.insert(i + 1, 'employee_name')

        # add hours
        fields.append('hours')

        return fields

    def get_xlsx_row(self, shift, fields):
        row = super().get_xlsx_row(shift, fields)

        # localize start and end times (Excel requires time with no zone)
        if shift.punch_in:
            row['punch_in'] = localtime(self.rattail_config, shift.punch_in, from_utc=True, tzinfo=False)
        if shift.punch_out:
            row['punch_out'] = localtime(self.rattail_config, shift.punch_out, from_utc=True, tzinfo=False)

        # add employee name
        row['employee_name'] = shift.employee.person.display_name

        # add hours
        if shift.punch_in and shift.punch_out:
            if shift.punch_in <= shift.punch_out:
                row['hours'] = hours_as_decimal(shift.punch_out - shift.punch_in, places=4)
            else:
                row['hours'] = "??"
        elif shift.punch_in or shift.punch_out:
            row['hours'] = "??"
        else:
            row['hours'] = None

        return row

# TODO: deprecate / remove this
WorkedShiftsView = WorkedShiftView


def defaults(config, **kwargs):
    base = globals()

    ScheduledShiftView = kwargs.get('ScheduledShiftView', base['ScheduledShiftView'])
    ScheduledShiftView.defaults(config)

    WorkedShiftView = kwargs.get('WorkedShiftView', base['WorkedShiftView'])
    WorkedShiftView.defaults(config)


def includeme(config):
    defaults(config)
