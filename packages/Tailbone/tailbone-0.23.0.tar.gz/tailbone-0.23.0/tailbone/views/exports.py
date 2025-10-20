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
Master class for generic export history views
"""

import os
import shutil

from pyramid.response import FileResponse
from webhelpers2.html import tags

from tailbone.views import MasterView


class ExportMasterView(MasterView):
    """
    Master class for generic export history views
    """
    creatable = False
    editable = False
    downloadable = False
    delete_export_files = False

    labels = {
        'id': "ID",
        'created_by': "Created by",
    }

    grid_columns = [
        'id',
        'created',
        'created_by',
        'record_count',
    ]

    form_fields = [
        'id',
        'created',
        'created_by',
        'record_count',
    ]

    def get_export_key(self):
        if hasattr(self, 'export_key'):
            return self.export_key

        cls = self.get_model_class()
        return cls.export_key

    def get_file_path(self, export, makedirs=False):
        return self.rattail_config.export_filepath(self.get_export_key(),
                                                   export.uuid,
                                                   export.filename,
                                                   makedirs=makedirs)

    def download_path(self, export, filename):
        # TODO: this assumes 'filename' default!
        return self.get_file_path(export)

    def configure_grid(self, g):
        super().configure_grid(g)
        model = self.model

        # id
        g.set_renderer('id', self.render_id)
        g.set_link('id')

        # filename
        g.set_link('filename')

        # created
        g.set_sort_defaults('created', 'desc')

        # created_by
        g.set_joiner('created_by',
                     lambda q: q.join(model.User).outerjoin(model.Person))
        g.set_sorter('created_by', model.Person.display_name)
        g.set_filter('created_by', model.Person.display_name)

    def render_id(self, export, field):
        return export.id_str

    def configure_form(self, f):
        super().configure_form(f)
        export = f.model_instance

        # NOTE: we try to handle the 'creating' scenario even though this class
        # doesn't officially support that; just in case a subclass does want to

        # id
        if self.creating:
            f.remove_field('id')
        else:
            f.set_readonly('id')
            f.set_renderer('id', self.render_id)
            f.set_label('id', "ID")

        # created
        if self.creating:
            f.remove_field('created')
        else:
            f.set_readonly('created')
            f.set_type('created', 'datetime')

        # created_by
        if self.creating:
            f.remove_field('created_by')
        else:
            f.set_readonly('created_by')
            f.set_renderer('created_by', self.render_created_by)
            f.set_label('created_by', "Created by")

        # record_count
        if self.creating:
            f.remove_field('record_count')
        else:
            f.set_readonly('record_count')

        # filename
        if self.editing:
            f.remove_field('filename')
        else:
            f.set_readonly('filename')
            f.set_renderer('filename', self.render_downloadable_file)

    def objectify(self, form, data=None):
        obj = super().objectify(form, data=data)
        if self.creating:
            obj.created_by = self.request.user
        return obj

    def render_created_by(self, export, field):
        user = export.created_by
        if not user:
            return ""
        text = str(user)
        if self.request.has_perm('users.view'):
            url = self.request.route_url('users.view', uuid=user.uuid)
            return tags.link_to(text, url)
        return text

    def get_download_url(self, filename):
        uuid = self.request.matchdict['uuid']
        return self.request.route_url('{}.download'.format(self.get_route_prefix()), uuid=uuid)

    def download(self):
        """
        View for downloading the export file.
        """
        export = self.get_instance()
        path = self.get_file_path(export)
        response = FileResponse(path, request=self.request)
        response.headers['Content-Length'] = str(os.path.getsize(path))
        response.headers['Content-Disposition'] = 'attachment; filename="{}"'.format(export.filename)
        return response

    def delete_instance(self, export):
        """
        Delete the export's files as well as the export itself.
        """
        # delete files for the export, if applicable
        if self.delete_export_files:
            path = self.get_file_path(export)
            dirname = os.path.dirname(path)
            if os.path.exists(dirname):
                shutil.rmtree(dirname)

        # continue w/ normal deletion
        super().delete_instance(export)
