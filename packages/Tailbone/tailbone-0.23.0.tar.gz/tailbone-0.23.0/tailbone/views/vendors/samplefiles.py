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
Model View for Vendor Sample Files
"""

from rattail.db.model import VendorSampleFile

from webhelpers2.html import tags

from tailbone import forms
from tailbone.views import MasterView


class VendorSampleFileView(MasterView):
    """
    Master model view for Vendor Sample Files
    """
    model_class = VendorSampleFile
    route_prefix = 'vendorsamplefiles'
    url_prefix = '/vendors/sample-files'
    downloadable = True
    has_versions = True

    grid_columns = [
        'vendor',
        'file_type',
        'effective_date',
        'filename',
        'created_by',
    ]

    form_fields = [
        'vendor',
        'file_type',
        'filename',
        'effective_date',
        'notes',
        'created_by',
    ]

    def configure_grid(self, g):
        super(VendorSampleFileView, self).configure_grid(g)
        model = self.model

        # vendor
        g.set_joiner('vendor', lambda q: q.join(model.Vendor))
        g.set_sorter('vendor', model.Vendor.name)
        g.set_filter('vendor', model.Vendor.name,
                     default_active=True, default_verb='contains')
        g.set_link('vendor')

        # filename
        g.set_link('filename')

        # effective_date
        g.set_sort_defaults('effective_date', 'desc')

    def configure_form(self, f):
        super(VendorSampleFileView, self).configure_form(f)

        # vendor
        f.set_renderer('vendor', self.render_vendor)
        if self.creating:
            f.replace('vendor', 'vendor_uuid')
            f.set_label('vendor_uuid', "Vendor")
            f.set_widget('vendor_uuid',
                         forms.widgets.make_vendor_widget(self.request))
        else:
            f.set_readonly('vendor')

        # filename
        if self.creating:
            f.replace('filename', 'file')
            f.set_type('file', 'file')
        else:
            f.set_readonly('filename')
            f.set_renderer('filename', self.render_filename)

        # effective_date
        f.set_type('effective_date', 'date_jquery')

        # notes
        f.set_type('notes', 'text')

        # created_by
        if self.creating or self.editing:
            f.remove('created_by')
        else:
            f.set_readonly('created_by')
            f.set_renderer('created_by', self.render_user)

    def objectify(self, form, data=None):
        if data is None:
            data = form.validated

        sample = super(VendorSampleFileView, self).objectify(form, data=data)

        if self.creating:
            sample.filename = data['file']['filename']
            data['file']['fp'].seek(0)
            sample.bytes = data['file']['fp'].read()
            sample.created_by = self.request.user

        return sample

    def render_filename(self, sample, field):
        filename = getattr(sample, field)
        if not filename:
            return

        size = self.readable_size(None, size=len(sample.bytes))
        text = "{} ({})".format(filename, size)
        url = self.get_action_url('download', sample)
        return tags.link_to(text, url)

    def download(self):
        """
        View for downloading a sample file.

        We override default logic to send raw bytes from DB, and avoid
        writing file to disk.
        """
        sample = self.get_instance()

        response = self.request.response
        response.content_length = len(sample.bytes)
        response.content_disposition = 'attachment; filename="{}"'.format(
            sample.filename)
        response.body = sample.bytes
        return response


def defaults(config, **kwargs):
    base = globals()

    VendorSampleFileView = kwargs.get('VendorSampleFileView', base['VendorSampleFileView'])
    VendorSampleFileView.defaults(config)


def includeme(config):
    defaults(config)
