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
Tools for displaying data diffs
"""

import sqlalchemy as sa
import sqlalchemy_continuum as continuum

from pyramid.renderers import render
from webhelpers2.html import HTML


class Diff(object):
    """
    Core diff class.  In sore need of documentation.

    You must provide the old and new data sets, and the set of
    relevant fields as well, if they cannot be easily introspected.

    :param old_data: Dict of "old" data values.

    :param new_data: Dict of "old" data values.

    :param fields: Sequence of relevant field names.  Note that
       both data dicts are expected to have keys which match these
       field names.  If you do not specify the fields then they
       will (hopefully) be introspected from the old or new data
       sets; however this will not work if they are both empty.

    :param monospace: If true, this flag will cause the value
       columns to be rendered in monospace font.  This is assumed
       to be helpful when comparing "raw" data values which are
       shown as e.g. ``repr(val)``.

    :param enums: Optional dict of enums for use when displaying field
       values.  If specified, keys should be field names and values
       should be enum dicts.
    """

    def __init__(self, old_data, new_data, columns=None, fields=None, enums=None,
                 render_field=None, render_value=None, nature='dirty',
                 monospace=False, extra_row_attrs=None):
        self.old_data = old_data
        self.new_data = new_data
        self.columns = columns or ["field name", "old value", "new value"]
        self.fields = fields or self.make_fields()
        self.enums = enums or {}
        self._render_field = render_field or self.render_field_default
        self.render_value = render_value or self.render_value_default
        self.nature = nature
        self.monospace = monospace
        self.extra_row_attrs = extra_row_attrs

    def make_fields(self):
        return sorted(set(self.old_data) | set(self.new_data), key=lambda x: x.lower())

    def old_value(self, field):
        return self.old_data.get(field)

    def new_value(self, field):
        return self.new_data.get(field)

    def values_differ(self, field):
        return self.new_value(field) != self.old_value(field)

    def render_html(self, template='/diff.mako', **kwargs):
        context = kwargs
        context['diff'] = self
        return HTML.literal(render(template, context))

    def get_row_attrs(self, field):
        """
        Returns a *rendered* set of extra attributes for the ``<tr>`` element
        for the given field.  May be an empty string, or a snippet of HTML
        attribute syntax, e.g.:

        .. code-block:: none

           class="diff" foo="bar"

        If you wish to supply additional attributes, please define
        :attr:`extra_row_attrs`, which can be either a static dict, or a
        callable returning a dict.
        """
        attrs = {}
        if self.values_differ(field):
            attrs['class'] = 'diff'

        if self.extra_row_attrs:
            if callable(self.extra_row_attrs):
                attrs.update(self.extra_row_attrs(field, attrs))
            else:
                attrs.update(self.extra_row_attrs)

        return HTML.render_attrs(attrs)

    def render_field(self, field):
        return self._render_field(field, self)

    def render_field_default(self, field, diff):
        return field

    def render_value_default(self, field, value):
        return repr(value)

    def render_old_value(self, field):
        value = self.old_value(field)
        return self.render_value(field, value)

    def render_new_value(self, field):
        value = self.new_value(field)
        return self.render_value(field, value)


class VersionDiff(Diff):
    """
    Special diff class, for use with version history views.  Note that
    while based on :class:`Diff`, this class uses a different
    signature for the constructor.

    :param version: Reference to a Continuum version record (object).

    :param \*args: Typical usage will not require positional args
       beyond the ``version`` param, in which case ``old_data`` and
       ``new_data`` params will be auto-determined based on the
       ``version``.  But if you specify positional args then nothing
       automatic is done, they are passed as-is to the parent
       :class:`Diff` constructor.

    :param \*\*kwargs: Remaining kwargs are passed as-is to the
       :class:`Diff` constructor.
    """

    def __init__(self, version, *args, **kwargs):
        self.version = version
        self.mapper = sa.inspect(continuum.parent_class(type(self.version)))
        self.version_mapper = sa.inspect(type(self.version))
        self.title = kwargs.pop('title', None)

        if 'nature' not in kwargs:
            if version.previous and version.operation_type == continuum.Operation.DELETE:
                kwargs['nature'] = 'deleted'
            elif version.previous:
                kwargs['nature'] = 'dirty'
            else:
                kwargs['nature'] = 'new'

        if 'fields' not in kwargs:
            kwargs['fields'] = self.get_default_fields()

        if not args:
            old_data = {}
            new_data = {}
            for field in kwargs['fields']:
                if version.previous:
                    old_data[field] = getattr(version.previous, field)
                new_data[field] = getattr(version, field)
            args = (old_data, new_data)

        super().__init__(*args, **kwargs)

    def get_default_fields(self):
        fields = sorted(self.version_mapper.columns.keys())

        unwanted = [
            'transaction_id',
            'end_transaction_id',
            'operation_type',
        ]

        return [field for field in fields
                if field not in unwanted]

    def render_version_value(self, field, value, version):
        """
        Render the cell value text for the given version/field info.

        Note that this method is used to render both sides of the diff
        (before and after values).

        :param field: Name of the field, as string.

        :param value: Raw value for the field, as obtained from ``version``.

        :param version: Reference to the Continuum version object.

        :returns: Rendered text as string, or ``None``.
        """
        text = HTML.tag('span', c=[repr(value)],
                        style='font-family: monospace;')

        # assume the enum display is all we need, if enum exists for the field
        if field in self.enums:

            # but skip the enum display if None
            display = self.enums[field].get(value)
            if display is None and value is None:
                return text

            # otherwise show enum display to the right of raw value
            display = self.enums[field].get(value, str(value))
            return HTML.tag('span', c=[
                text,
                HTML.tag('span', c=[display],
                         style='margin-left: 2rem; font-style: italic; font-weight: bold;'),
            ])

        # next we look for a relationship and may render the foreign object
        for prop in self.mapper.relationships:
            if prop.uselist:
                continue

            for col in prop.local_columns:
                if col.name != field:
                    continue

                if not hasattr(version, prop.key):
                    continue

                if col in self.mapper.primary_key:
                    continue

                ref = getattr(version, prop.key)
                if ref:
                    ref = getattr(ref, 'version_parent', None)
                    if ref:
                        return HTML.tag('span', c=[
                            text,
                            HTML.tag('span', c=[str(ref)],
                                     style='margin-left: 2rem; font-style: italic; font-weight: bold;'),
                        ])

        return text

    def render_old_value(self, field):
        if self.nature == 'new':
            return ''
        value = self.old_value(field)
        return self.render_version_value(field, value, self.version.previous)

    def render_new_value(self, field):
        if self.nature == 'deleted':
            return ''
        value = self.new_value(field)
        return self.render_version_value(field, value, self.version)

    def as_struct(self):
        values = {}
        for field in self.fields:
            values[field] = {'before': self.render_old_value(field),
                             'after': self.render_new_value(field)}

        operation = None
        if self.version.operation_type == continuum.Operation.INSERT:
            operation = 'INSERT'
        elif self.version.operation_type == continuum.Operation.UPDATE:
            operation = 'UPDATE'
        elif self.version.operation_type == continuum.Operation.DELETE:
            operation = 'DELETE'
        else:
            operation = self.version.operation_type

        return {
            'key': id(self.version),
            'model_title': self.title,
            'operation': operation,
            'diff_class': self.nature,
            'fields': self.fields,
            'values': values,
        }
