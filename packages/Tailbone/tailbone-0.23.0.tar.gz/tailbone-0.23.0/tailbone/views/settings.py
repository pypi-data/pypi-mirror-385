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
Settings Views
"""

import json
import re

import colander

from rattail.db.model import Setting
from rattail.settings import Setting as AppSetting
from rattail.util import import_module_path

from tailbone import forms, grids
from tailbone.db import Session
from tailbone.views import MasterView, View
from wuttaweb.util import get_libver, get_liburl
from wuttaweb.views.settings import AppInfoView as WuttaAppInfoView


class AppInfoView(WuttaAppInfoView):
    """ """
    Session = Session
    weblib_config_prefix = 'tailbone'

    # TODO: for now we override to get tailbone searchable grid
    def make_grid(self, **kwargs):
        """ """
        return grids.Grid(self.request, **kwargs)

    def configure_grid(self, g):
        """ """
        super().configure_grid(g)

        # name
        g.set_searchable('name')

        # editable_project_location
        g.set_searchable('editable_project_location')

    def configure_get_context(self, **kwargs):
        """ """
        context = super().configure_get_context(**kwargs)
        simple_settings = context['simple_settings']
        weblibs = context['weblibs']

        for weblib in weblibs:
            key = weblib['key']

            # TODO: this is only needed to migrate legacy settings to
            # use the newer wuttaweb setting names
            url = simple_settings[f'wuttaweb.liburl.{key}']
            if not url and weblib['configured_url']:
                simple_settings[f'wuttaweb.liburl.{key}'] = weblib['configured_url']

        return context

    # nb. these email settings require special handling below
    configure_profile_key_mismatches = [
        'default.subject',
        'default.to',
        'default.cc',
        'default.bcc',
        'feedback.subject',
        'feedback.to',
    ]

    def configure_get_simple_settings(self):
        """ """
        simple_settings = super().configure_get_simple_settings()

        # TODO:
        # there are several email config keys which differ between
        # wuttjamaican and rattail.  basically all of the "profile" keys
        # have a different prefix.

        # after wuttaweb has declared its settings, we examine each and
        # overwrite the value if one is defined with rattail config key.
        # (nb. this happens even if wuttjamaican key has a value!)

        # note that we *do* declare the profile mismatch keys for
        # rattail, as part of simple settings.  this ensures the
        # parent logic will always remove them when saving.  however
        # we must also include them in gather_settings() to ensure
        # they are saved to match wuttjamaican values.

        # there are also a couple of flags where rattail's default is the
        # opposite of wuttjamaican.  so we overwrite those too as needed.

        for setting in simple_settings:

            # nb. the update home page redirect setting is off by
            # default for wuttaweb, but on for tailbone
            if setting['name'] == 'wuttaweb.home_redirect_to_login':
                value = self.config.get_bool('wuttaweb.home_redirect_to_login')
                if value is None:
                    value = self.config.get_bool('tailbone.login_is_home', default=True)
                setting['value'] = value

            # nb. sending email is off by default for wuttjamaican,
            # but on for rattail
            elif setting['name'] == 'rattail.mail.send_emails':
                value = self.config.get_bool('rattail.mail.send_emails', default=True)
                setting['value'] = value

            # nb. this one is even more special, key is entirely different
            elif setting['name'] == 'rattail.email.default.sender':
                value = self.config.get('rattail.email.default.sender')
                if value is None:
                    value = self.config.get('rattail.mail.default.from')
                setting['value'] = value

            else:

                # nb. fetch alternate value for profile key mismatch
                for key in self.configure_profile_key_mismatches:
                    if setting['name'] == f'rattail.email.{key}':
                        value = self.config.get(f'rattail.email.{key}')
                        if value is None:
                            value = self.config.get(f'rattail.mail.{key}')
                        setting['value'] = value
                        break

        # nb. these are no longer used (deprecated), but we keep
        # them defined here so the tool auto-deletes them

        simple_settings.extend([
            {'name': 'tailbone.login_is_home'},
            {'name': 'tailbone.buefy_version'},
            {'name': 'tailbone.vue_version'},
        ])

        simple_settings.append({'name': 'rattail.mail.default.from'})
        for key in self.configure_profile_key_mismatches:
            simple_settings.append({'name': f'rattail.mail.{key}'})

        for key in self.get_weblibs():
            simple_settings.extend([
                {'name': f'tailbone.libver.{key}'},
                {'name': f'tailbone.liburl.{key}'},
            ])

        return simple_settings

    def configure_gather_settings(self, data, simple_settings=None):
        """ """
        settings = super().configure_gather_settings(data, simple_settings=simple_settings)

        # nb. must add legacy rattail profile settings to match new ones
        for setting in list(settings):

            if setting['name'] == 'rattail.email.default.sender':
                value = setting['value']
                settings.append({'name': 'rattail.mail.default.from',
                                 'value': value})

            else:
                for key in self.configure_profile_key_mismatches:
                    if setting['name'] == f'rattail.email.{key}':
                        value = setting['value']
                        settings.append({'name': f'rattail.mail.{key}',
                                         'value': value})
                        break

        return settings


class SettingView(MasterView):
    """
    Master view for the settings model.
    """
    model_class = Setting
    model_title = "Raw Setting"
    model_title_plural = "Raw Settings"
    bulk_deletable = True
    feedback = re.compile(r'^rattail\.mail\.user_feedback\..*')

    grid_columns = [
        'name',
        'value',
    ]

    def configure_grid(self, g):
        super().configure_grid(g)
        g.filters['name'].default_active = True
        g.filters['name'].default_verb = 'contains'
        g.set_sort_defaults('name')
        g.set_link('name')

    def configure_form(self, f):
        super().configure_form(f)
        if self.creating:
            f.set_validator('name', self.unique_name)

    def unique_name(self, node, value):
        model = self.model
        setting = self.Session.get(model.Setting, value)
        if setting:
            raise colander.Invalid(node, "Setting name must be unique")

    def editable_instance(self, setting):
        if self.rattail_config.demo():
            return not bool(self.feedback.match(setting.name))
        return True

    def after_edit(self, setting):
        # nb. force cache invalidation - normally this happens when a
        # setting is saved via app handler, but here that is being
        # bypassed and it is saved directly via standard ORM calls
        self.rattail_config.beaker_invalidate_setting(setting.name)

    def deletable_instance(self, setting):
        if self.rattail_config.demo():
            return not bool(self.feedback.match(setting.name))
        return True

    def delete_instance(self, setting):

        # nb. force cache invalidation
        self.rattail_config.beaker_invalidate_setting(setting.name)

        # otherwise delete like normal
        super().delete_instance(setting)


# TODO: deprecate / remove this
SettingsView = SettingView


class AppSettingsForm(forms.Form):

    def get_label(self, key):
        return self.labels.get(key, key)


class AppSettingsView(View):
    """
    Core view which exposes "app settings" - aka. admin-friendly settings with
    descriptions and type-specific form controls etc.
    """

    def __call__(self):
        settings = sorted(self.iter_known_settings(),
                          key=lambda setting: (setting.group,
                                               setting.namespace,
                                               setting.name))
        groups = sorted(set([setting.group for setting in settings]))
        current_group = None

        form = self.make_form(settings)
        form.cancel_url = self.request.current_route_url()
        if form.validate():
            self.save_form(form)
            group = self.request.POST.get('settings-group')
            if group is not None:
                self.request.session['appsettings.current_group'] = group
            self.request.session.flash("App Settings have been saved.")
            return self.redirect(self.request.current_route_url())

        if self.request.method == 'POST':
            current_group = self.request.POST.get('settings-group')

        if not current_group:
            current_group = self.request.session.get('appsettings.current_group')

        possible_config_options = sorted(
            self.request.registry.settings['tailbone_config_pages'],
            key=lambda p: p['label'])

        config_options = []
        for option in possible_config_options:
            perm = option.get('perm', option['route'])
            if self.request.has_perm(perm):
                option['url'] = self.request.route_url(option['route'])
                config_options.append(option)

        context = {
            'index_title': "App Settings",
            'form': form,
            'dform': form.make_deform_form(),
            'groups': groups,
            'settings': settings,
            'config_options': config_options,
        }
        context['settings_data'] = self.get_settings_data(form, groups, settings)
        # TODO: this seems hacky, and probably only needed if theme changes?
        if current_group == '(All)':
            current_group = ''
        context['current_group'] = current_group
        return context

    def get_settings_data(self, form, groups, settings):
        dform = form.make_deform_form()
        grouped = dict([(label, [])
                        for label in groups])

        for setting in settings:
            field = dform[setting.node_name]
            s = {
                'field_name': field.name,
                'label': form.get_label(field.name),
                'data_type': setting.data_type.__name__,
                'choices': setting.choices,
                'helptext': form.render_helptext(field.name) if form.has_helptext(field.name) else None,
                'error': False, # nb. may set to True below
            }

            # we want the value from the form, i.e. in case of a POST
            # request with validation errors.  we also want to make
            # sure value is JSON-compatible, but we must represent it
            # as Python value here, and it will be JSON-encoded later.
            value = form.get_vuejs_model_value(field)
            value = json.loads(value)
            s['value'] = value

            # specify error / message if applicable
            # TODO: not entirely clear to me why some field errors are
            # represented differently?
            if field.error:
                s['error'] = True
                if isinstance(field.error, colander.Invalid):
                    s['error_messages'] = [field.errormsg]
                else:
                    s['error_messages'] = field.error_messages()

            grouped[setting.group].append(s)

        data = []
        for label in groups:
            group = {'label': label, 'settings': grouped[label]}
            data.append(group)

        return data

    def make_form(self, known_settings):
        schema = colander.MappingSchema()
        helptext = {}
        for setting in known_settings:
            kwargs = {
                'name': setting.node_name,
                'default': self.get_setting_value(setting),
            }
            if kwargs['default'] is None or kwargs['default'] == '':
                kwargs['default'] = colander.null
            if not setting.required:
                kwargs['missing'] = colander.null
            if setting.choices:
                kwargs['validator'] = colander.OneOf(setting.choices)
                kwargs['widget'] = forms.widgets.JQuerySelectWidget(
                    values=[(val, val) for val in setting.choices])
            schema.add(colander.SchemaNode(self.get_node_type(setting), **kwargs))
            helptext[setting.node_name] = setting.__doc__.strip()
        return AppSettingsForm(schema=schema, request=self.request, helptext=helptext)

    def get_node_type(self, setting):
        if setting.data_type is bool:
            return colander.Bool()
        elif setting.data_type is int:
            return colander.Integer()
        return colander.String()

    def save_form(self, form):
        for setting in self.iter_known_settings():
            value = form.validated[setting.node_name]
            if value is colander.null:
                value = ''
            self.save_setting_value(setting, value)

    def iter_known_settings(self):
        """
        Iterate over all known settings.
        """
        modules = self.rattail_config.getlist('rattail', 'settings')
        if modules:
            core_only = False
        else:
            modules = ['rattail.settings']
            core_only = True

        for module in modules:
            module = import_module_path(module)
            for name in dir(module):
                obj = getattr(module, name)
                if isinstance(obj, type) and issubclass(obj, AppSetting) and obj is not AppSetting:
                    if core_only and not obj.core:
                        continue
                    # NOTE: we set this here, and reference it elsewhere
                    obj.node_name = self.get_node_name(obj)
                    yield obj

    def get_node_name(self, setting):
        return '[{}] {}'.format(setting.namespace, setting.name)

    def get_setting_value(self, setting):
        if setting.data_type is bool:
            return self.rattail_config.getbool(setting.namespace, setting.name)
        if setting.data_type is list:
            return '\n'.join(
                self.rattail_config.getlist(setting.namespace, setting.name,
                                            default=[]))
        return self.rattail_config.get(setting.namespace, setting.name)

    def save_setting_value(self, setting, value):
        existing = self.get_setting_value(setting)
        if existing != value:
            legacy_name = '{}.{}'.format(setting.namespace, setting.name)
            if setting.data_type is bool:
                value = 'true' if value else 'false'
            elif setting.data_type is list:
                entries = [self.clean_list_entry(entry)
                           for entry in value.split('\n')]
                value = ', '.join(entries)
            else:
                value = str(value)
            app = self.get_rattail_app()
            app.save_setting(Session(), legacy_name, value)

    def clean_list_entry(self, value):
        value = value.strip()
        if '"' in value and "'" in value:
            raise NotImplementedError("don't know how to handle escaping 2 "
                                      "different types of quotes!")
        if '"' in value:
            return "'{}'".format(value)
        if "'" in value:
            return '"{}"'.format(value)
        return value

    @classmethod
    def defaults(cls, config):
        config.add_route('appsettings', '/settings/app/')
        config.add_view(cls, route_name='appsettings',
                        renderer='/appsettings.mako',
                        permission='settings.edit')


def defaults(config, **kwargs):
    base = globals()

    AppInfoView = kwargs.get('AppInfoView', base['AppInfoView'])
    AppInfoView.defaults(config)

    AppSettingsView = kwargs.get('AppSettingsView', base['AppSettingsView'])
    AppSettingsView.defaults(config)

    SettingView = kwargs.get('SettingView', base['SettingView'])
    SettingView.defaults(config)


def includeme(config):
    defaults(config)
