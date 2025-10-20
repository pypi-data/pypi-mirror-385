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
Project views
"""

from collections import OrderedDict

import colander
from deform import widget as dfwidget

from rattail.projects import (PythonProjectGenerator,
                              PoserProjectGenerator,
                              RattailAdjacentProjectGenerator)

from tailbone import forms
from tailbone.views import MasterView


class GeneratedProjectView(MasterView):
    """
    View for generating new project source code
    """
    model_title = "Generated Project"
    model_key = 'folder'
    route_prefix = 'generated_projects'
    url_prefix = '/generated-projects'
    listable = False
    viewable = False
    editable = False
    deletable = False

    def __init__(self, request):
        super(GeneratedProjectView, self).__init__(request)
        self.project_handler = self.get_project_handler()

    def get_project_handler(self):
        app = self.get_rattail_app()
        return app.get_project_handler()

    def create(self):
        supported = self.project_handler.get_supported_project_generators()
        supported_keys = list(supported)

        project_type = self.request.matchdict.get('project_type')
        if project_type:
            form = self.make_project_form(project_type)
            if form.validate():
                zipped = self.generate_project(project_type, form)
                return self.file_response(zipped)

        else: # no project_type

            # make form to accept user choice of report type
            schema = colander.Schema()
            values = [(typ, typ) for typ in supported_keys]
            schema.add(colander.SchemaNode(name='project_type',
                                           typ=colander.String(),
                                           validator=colander.OneOf(supported_keys),
                                           widget=dfwidget.SelectWidget(values=values)))
            form = forms.Form(schema=schema, request=self.request)
            form.submit_label = "Continue"

            # if form validates, then user has chosen a project type, so
            # we redirect to the appropriate "generate project" page
            if form.validate():
                raise self.redirect(self.request.route_url(
                    'generate_specific_project',
                    project_type=form.validated['project_type']))

        return self.render_to_response('create', {
            'index_title': "Generate Project",
            'project_type': project_type,
            'form': form,
        })

    def generate_project(self, project_type, form):
        context = dict(form.validated)
        output = self.project_handler.generate_project(project_type,
                                                       context=context)
        return self.project_handler.zip_output(output)

    def make_project_form(self, project_type):

        # make form
        schema = self.project_handler.make_project_schema(project_type)
        form = forms.Form(schema=schema, request=self.request)
        form.auto_disable = False
        form.auto_disable_save = False
        form.submit_label = "Generate Project"
        form.cancel_url = self.request.route_url('generated_projects.create')

        # apply normal config
        self.configure_form_common(form, project_type)

        # let supplemental views further configure form
        for supp in self.iter_view_supplements():
            configure = getattr(supp, 'configure_form_{}'.format(project_type), None)
            if configure:
                configure(form)

        # if master view has more configure logic, do that too
        configure = getattr(self, 'configure_form_{}'.format(project_type), None)
        if configure:
            configure(form)

        return form

    def configure_form_common(self, form, project_type):
        generator = self.project_handler.get_project_generator(project_type,
                                                               require=True)

        # python-based projects
        if isinstance(generator, PythonProjectGenerator):
            self.configure_form_python(form)

        # rattail-adjacent projects
        if isinstance(generator, RattailAdjacentProjectGenerator):
            self.configure_form_rattail_adjacent(form)

        # poser-based projects
        if isinstance(generator, PoserProjectGenerator):
            self.configure_form_poser(form)

    def configure_form_python(self, f):

        f.set_grouping([
            ("Naming", [
                'name',
                'pkg_name',
                'pypi_name',
            ]),
        ])

        # name
        f.set_label('name', "Project Name")
        f.set_helptext('name', "Human-friendly name generally used to refer to this project.")
        f.set_default('name', "Poser Plus")

        # pkg_name
        f.set_label('pkg_name', "Package Name in Python")
        f.set_helptext('pkg_name', "`For example, ~/src/${field_model_pkg_name.replace(/_/g, '-')}/${field_model_pkg_name}/__init__.py`",
                       dynamic=True)
        f.set_default('pkg_name', "poser_plus")

        # pypi_name
        f.set_label('pypi_name', "Package Name for PyPI")
        f.set_helptext('pypi_name', "It's a good idea to use org name as namespace prefix here")
        f.set_default('pypi_name', "Acme-Poser-Plus")

    def configure_form_rattail_adjacent(self, f):

        # extends_config
        f.set_label('extends_config', "Extend Config")
        f.set_helptext('extends_config', "Needed to customize default config values etc.")
        f.set_default('extends_config', True)

        # has_cli
        f.set_label('has_cli', "Use Separate CLI")
        f.set_helptext('has_cli', "`Needed for e.g. '${field_model_pkg_name} install' command.`",
                       dynamic=True)
        f.set_default('has_cli', True)

        # extends_db
        f.set_label('extends_db', "Extend DB Schema")
        f.set_helptext('extends_db', "For adding custom tables/columns to the core schema")
        f.set_default('extends_db', True)

    def configure_form_poser(self, f):

        # organization
        f.set_helptext('organization', 'For use with branding etc.')
        f.set_default('organization', "Acme Foods")

        # has_db
        f.set_label('has_db', "Use Rattail DB")
        f.set_helptext('has_db', "Note that a DB is required for the Web App")
        f.set_default('has_db', True)

        # has_batch_schema
        f.set_label('has_batch_schema', "Add Batch Schema")
        f.set_helptext('has_batch_schema', 'Usually not needed - it\'s for "dynamic" (e.g. import/export) batches')

        # has_web
        f.set_label('has_web', "Use Tailbone Web App")
        f.set_default('has_web', True)

        # has_web_api
        f.set_label('has_web_api', "Use Tailbone Web API")
        f.set_helptext('has_web_api', "Needed for e.g. Vue.js SPA mobile apps")

        # has_datasync
        f.set_label('has_datasync', "Use DataSync Service")

        # uses_fabric
        f.set_label('uses_fabric', "Use Fabric")
        f.set_default('uses_fabric', True)

    def configure_form_rattail(self, f):

        f.set_grouping([
            ("Naming", [
                'name',
                'pkg_name',
                'pypi_name',
                'organization',
            ]),
            ("Core", [
                'extends_config',
                'has_cli',
            ]),
            ("Database", [
                'has_db',
                'extends_db',
                'has_batch_schema',
            ]),
            ("Web", [
                'has_web',
                'has_web_api',
            ]),
            ("Integrations", [
                # 'integrates_catapult',
                # 'integrates_corepos',
                # 'integrates_locsms',
                'has_datasync',
            ]),
            ("Deployment", [
                'uses_fabric',
            ]),
        ])

        # # integrates_catapult
        # f.set_label('integrates_catapult', "Integrate w/ Catapult")
        # f.set_helptext('integrates_catapult', "Add schema, import/export logic etc. for ECRS Catapult")

        # # integrates_corepos
        # f.set_label('integrates_corepos', "Integrate w/ CORE-POS")
        # f.set_helptext('integrates_corepos', "Add schema, import/export logic etc. for CORE-POS")

        # # integrates_locsms
        # f.set_label('integrates_locsms', "Integrate w/ LOC SMS")
        # f.set_helptext('integrates_locsms', "Add schema, import/export logic etc. for LOC SMS")

    def configure_form_rattail_integration(self, f):

        f.set_grouping([
            ("Naming", [
                'integration_name',
                'integration_url',
                'name',
                'pkg_name',
                'pypi_name',
            ]),
            ("Options", [
                'extends_config',
                'extends_db',
                'has_cli',
            ]),
        ])

        # default settings
        f.set_default('name', 'rattail-foo')
        f.set_default('pkg_name', 'rattail_foo')
        f.set_default('pypi_name', 'rattail-foo')
        f.set_default('has_cli', False)

        # integration_name
        f.set_helptext('integration_name', "Name of the system to be integrated")
        f.set_default('integration_name', "Foo")

        # integration_url
        f.set_label('integration_url', "Integration URL")
        f.set_helptext('integration_url', "Reference URL for the system to be integrated")
        f.set_default('integration_url', "https://www.example.com/")

    def configure_form_rattail_shopfoo(self, f):

        # first do normal integration setup
        self.configure_form_rattail_integration(f)

        f.set_grouping([
            ("Naming", [
                'integration_name',
                'integration_url',
                'name',
                'pkg_name',
                'pypi_name',
            ]),
            ("Options", [
                'has_cli',
            ]),
        ])

        # default settings
        f.set_default('integration_name', 'Shopfoo')
        f.set_default('name', 'rattail-shopfoo')
        f.set_default('pkg_name', 'rattail_shopfoo')
        f.set_default('pypi_name', 'rattail-shopfoo')
        f.set_default('has_cli', False)

    def configure_form_tailbone_integration(self, f):

        f.set_grouping([
            ("Naming", [
                'integration_name',
                'integration_url',
                'name',
                'pkg_name',
                'pypi_name',
            ]),
            ("Options", [
                'has_static_files',
            ]),
        ])

        # integration_name
        f.set_helptext('integration_name', "Name of the system to be integrated")
        f.set_default('integration_name', "Foo")

        # integration_url
        f.set_label('integration_url', "Integration URL")
        f.set_helptext('integration_url', "Reference URL for the system to be integrated")
        f.set_default('integration_url', "https://www.example.com/")

        # has_static_files
        f.set_helptext('has_static_files', "Register a subfolder for static files (images etc.)")

    def configure_form_tailbone_shopfoo(self, f):

        # first do normal integration setup
        self.configure_form_tailbone_integration(f)

        f.set_grouping([
            ("Naming", [
                'integration_name',
                'integration_url',
                'name',
                'pkg_name',
                'pypi_name',
            ]),
        ])

        # default settings
        f.set_default('integration_name', 'Shopfoo')
        f.set_default('name', 'tailbone-shopfoo')
        f.set_default('pkg_name', 'tailbone_shopfoo')
        f.set_default('pypi_name', 'tailbone-shopfoo')

    def configure_form_byjove(self, f):

        f.set_grouping([
            ("Naming", [
                'system_name',
                'name',
                'slug',
            ]),
        ])

        # system_name
        f.set_default('system_name', "Okay Then")
        f.set_helptext('system_name',
                       "Name of overall system to which mobile app belongs.")

        # name
        f.set_label('name', "Mobile App Name")
        f.set_default('name', "Okay Then Mobile")
        f.set_helptext('name', "Display name for the mobile app.")

        # slug
        f.set_default('slug', "okay-then-mobile")
        f.set_helptext('slug', "Used for NPM-compatible project name etc.")

    def configure_form_fabric(self, f):

        f.set_grouping([
            ("Naming", [
                'name',
                'pkg_name',
                'pypi_name',
                'organization',
            ]),
            ("Theo", [
                'integrates_with',
            ]),
        ])

        # naming defaults
        f.set_default('name', "Acme Fabric")
        f.set_default('pkg_name', "acmefab")
        f.set_default('pypi_name', "Acme-Fabric")

        # organization
        f.set_helptext('organization', 'For use with branding etc.')
        f.set_default('organization', "Acme Foods")

        # integrates_with
        f.set_helptext('integrates_with', "Which POS system should Theo integrate with, if any")
        f.set_enum('integrates_with', OrderedDict([
            ('', "(nothing)"),
            ('catapult', "ECRS Catapult"),
            ('corepos', "CORE-POS"),
            ('locsms', "LOC SMS")
        ]))
        f.set_default('integrates_with', '')

    @classmethod
    def defaults(cls, config):
        cls._defaults(config)
        cls._generated_project_defaults(config)

    @classmethod
    def _generated_project_defaults(cls, config):
        url_prefix = cls.get_url_prefix()
        permission_prefix = cls.get_permission_prefix()

        # generate project (accept custom params, truly create)
        config.add_route('generate_specific_project',
                         '{}/new/{{project_type}}'.format(url_prefix))
        config.add_view(cls, attr='create',
                        route_name='generate_specific_project',
                        permission='{}.create'.format(permission_prefix))


def defaults(config, **kwargs):
    base = globals()

    GeneratedProjectView = kwargs.get('GeneratedProjectView', base['GeneratedProjectView'])
    GeneratedProjectView.defaults(config)


def includeme(config):
    defaults(config)
