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
Views for app upgrades
"""

import json
import os
import re
import logging
import warnings
from collections import OrderedDict

import sqlalchemy as sa

from rattail.db.model import Upgrade
from rattail.threads import Thread

from deform import widget as dfwidget
from webhelpers2.html import tags, HTML

from tailbone.views import MasterView
from tailbone.progress import get_progress_session #, SessionProgress
from tailbone.config import should_expose_websockets


log = logging.getLogger(__name__)


class UpgradeView(MasterView):
    """
    Master view for all user events
    """
    model_class = Upgrade
    downloadable = True
    cloneable = True
    configurable = True
    executable = True
    execute_progress_template = '/upgrade.mako'
    execute_progress_initial_msg = "Upgrading"
    execute_can_cancel = False

    labels = {
        'executed_by': "Executed by",
        'status_code': "Status",
        'stdout_file': "STDOUT",
        'stderr_file': "STDERR",
    }

    grid_columns = [
        'system',
        'created',
        'description',
        # 'not_until',
        'enabled',
        'status_code',
        'executed',
        'executed_by',
    ]

    form_fields = [
        'system',
        'description',
        # 'not_until',
        # 'requirements',
        'notes',
        'created',
        'created_by',
        'enabled',
        'executing',
        'executed',
        'executed_by',
        'status_code',
        'stdout_file',
        'stderr_file',
        'exit_code',
        'package_diff',
    ]

    def __init__(self, request):
        super().__init__(request)

        if hasattr(self, 'get_handler'):
            warnings.warn("defining get_handler() is deprecated.  please "
                          "override AppHandler.get_upgrade_handler() instead",
                          DeprecationWarning, stacklevel=2)
            self.upgrade_handler = self.get_handler()

        else:
            app = self.get_rattail_app()
            self.upgrade_handler = app.get_upgrade_handler()

    @property
    def handler(self):
        warnings.warn("handler attribute is deprecated; "
                      "please use upgrade_handler instead",
                      DeprecationWarning, stacklevel=2)
        return self.upgrade_handler

    def configure_grid(self, g):
        super().configure_grid(g)
        model = self.model

        # system
        systems = self.upgrade_handler.get_all_systems()
        systems_enum = dict([(s['key'], s['label']) for s in systems])
        g.set_enum('system', systems_enum)

        g.set_joiner('executed_by', lambda q: q.join(model.User, model.User.uuid == model.Upgrade.executed_by_uuid).outerjoin(model.Person))
        g.set_sorter('executed_by', model.Person.display_name)
        g.set_enum('status_code', self.enum.UPGRADE_STATUS)
        g.set_type('created', 'datetime')
        g.set_type('executed', 'datetime')
        g.set_sort_defaults('created', 'desc')

        g.set_link('system')
        g.set_link('created')
        g.set_link('description')
        # g.set_link('not_until')
        g.set_link('executed')

    def grid_extra_class(self, upgrade, i):
        if upgrade.status_code == self.enum.UPGRADE_STATUS_FAILED:
            return 'warning'
        if upgrade.status_code == self.enum.UPGRADE_STATUS_EXECUTING:
            return 'notice'

    def template_kwargs_view(self, **kwargs):
        kwargs = super().template_kwargs_view(**kwargs)
        app = self.get_rattail_app()
        model = self.model
        upgrade = kwargs['instance']

        kwargs['system_title'] = app.get_title()
        if upgrade.system:
            system = self.upgrade_handler.get_system(upgrade.system)
            if system:
                kwargs['system_title'] = system['label']

        kwargs['show_prev_next'] = True
        kwargs['prev_url'] = None
        kwargs['next_url'] = None

        upgrades = self.Session.query(model.Upgrade)\
                               .filter(model.Upgrade.uuid != upgrade.uuid)
        older = upgrades.filter(model.Upgrade.created <= upgrade.created)\
                        .order_by(model.Upgrade.created.desc())\
                        .first()
        newer = upgrades.filter(model.Upgrade.created >= upgrade.created)\
                        .order_by(model.Upgrade.created)\
                        .first()

        if older:
            kwargs['prev_url'] = self.get_action_url('view', older)
        if newer:
            kwargs['next_url'] = self.get_action_url('view', newer)

        return kwargs

    def configure_form(self, f):
        super().configure_form(f)
        upgrade = f.model_instance

        # system
        systems = self.upgrade_handler.get_all_systems()
        systems_enum = OrderedDict([(s['key'], s['label'])
                                    for s in systems])
        f.set_enum('system', systems_enum)
        f.set_required('system')
        if self.creating:
            if len(systems) == 1:
                f.set_default('system', list(systems_enum)[0])

        # status_code
        if self.creating:
            f.remove_field('status_code')
        else:
            f.set_enum('status_code', self.enum.UPGRADE_STATUS)
            f.set_renderer('status_code', self.render_status_code)

        # executing
        if not self.editing:
            f.remove('executing')

        f.set_type('created', 'datetime')
        f.set_type('executed', 'datetime')
        # f.set_widget('not_until', dfwidget.DateInputWidget())
        f.set_widget('notes', dfwidget.TextAreaWidget(cols=80, rows=8))
        f.set_renderer('stdout_file', self.render_stdout_file)
        f.set_renderer('stderr_file', self.render_stdout_file)

        # package_diff
        if self.viewing and upgrade.executed and (
                upgrade.system == 'rattail'
                or not upgrade.system):
            f.set_renderer('package_diff', self.render_package_diff)
        else:
            f.remove_field('package_diff')

        # f.set_readonly('created')
        # f.set_readonly('created_by')
        f.set_readonly('executed')
        f.set_readonly('executed_by')
        if self.creating or self.editing:
            f.remove_field('created')
            f.remove_field('created_by')
            f.remove_field('stdout_file')
            f.remove_field('stderr_file')
            if self.creating or not upgrade.executed:
                f.remove_field('executed')
                f.remove_field('executed_by')

        elif not upgrade.executed:
            f.remove_field('executed')
            f.remove_field('executed_by')
            f.remove_field('stdout_file')
            f.remove_field('stderr_file')

        # enabled
        if not self.creating and upgrade.executed:
            f.remove('enabled')
        else:
            f.set_type('enabled', 'boolean')
            f.set_default('enabled', True)

        if not self.viewing or not upgrade.executed:
            f.remove_field('exit_code')

    def render_status_code(self, upgrade, field):
        code = getattr(upgrade, field)
        text = self.enum.UPGRADE_STATUS[code]

        if code == self.enum.UPGRADE_STATUS_EXECUTING:

            text = HTML.tag('span', c=[text])

            button = HTML.tag('b-button',
                              type='is-warning',
                              icon_pack='fas',
                              icon_left='sad-tear',
                              c=['{{ declareFailureSubmitting ? "Working, please wait..." : "Declare Failure" }}'],
                              **{':disabled': 'declareFailureSubmitting',
                                 '@click': 'declareFailureClick'})

            return HTML.tag('div', class_='level', c=[
                HTML.tag('div', class_='level-left', c=[
                    HTML.tag('div', class_='level-item', c=[text]),
                    HTML.tag('div', class_='level-item', c=[button]),
                ]),
            ])

        # just show status per normal
        return text

    def configure_clone_form(self, f):
        f.fields = ['system', 'description', 'notes', 'enabled']

    def clone_instance(self, original):
        app = self.get_rattail_app()
        cloned = self.model_class()
        cloned.system = original.system
        cloned.created = app.make_utc()
        cloned.created_by = self.request.user
        cloned.description = original.description
        cloned.notes = original.notes
        cloned.status_code = self.enum.UPGRADE_STATUS_PENDING
        cloned.enabled = original.enabled
        self.Session.add(cloned)
        self.Session.flush()
        return cloned

    def render_stdout_file(self, upgrade, fieldname):
        if fieldname.startswith('stderr'):
            filename = 'stderr.log'
        else:
            filename = 'stdout.log'
        path = self.rattail_config.upgrade_filepath(upgrade.uuid, filename=filename)
        if path:
            url = '{}?filename={}'.format(self.get_action_url('download', upgrade), filename)
            return self.render_file_field(path, url, filename=filename)
        return filename

    def render_package_diff(self, upgrade, fieldname):
        try:
            before = self.parse_requirements(upgrade, 'before')
            after = self.parse_requirements(upgrade, 'after')

            kwargs = {}
            kwargs['extra_row_attrs'] = self.get_extra_diff_row_attrs
            diff = self.make_diff(before, after,
                                  columns=["package", "old version", "new version"],
                                  render_field=self.render_diff_field,
                                  render_value=self.render_diff_value,
                                  **kwargs)

            kwargs = {}
            kwargs['@click.prevent'] = "showingPackages = 'all'"
            kwargs[':style'] = "{'font-weight': showingPackages == 'all' ? 'bold' : null}"
            all_link = tags.link_to("all", '#', **kwargs)

            kwargs = {}
            kwargs['@click.prevent'] = "showingPackages = 'diffs'"
            kwargs[':style'] = "{'font-weight': showingPackages == 'diffs' ? 'bold' : null}"
            diffs_link = tags.link_to("diffs only", '#', **kwargs)

            kwargs = {}
            showing = HTML.tag('div', c=["showing: "
                                         + all_link
                                         + " / "
                                         + diffs_link],
                               **kwargs)

            return HTML.tag('div', c=[showing + diff.render_html()])

        except:
            log.debug("failed to render package diff for upgrade: {}".format(upgrade), exc_info=True)
            return HTML.tag('div', c="(not available for this upgrade)")

    def get_extra_diff_row_attrs(self, field, attrs):
        extra = {}
        if attrs.get('class') != 'diff':
            extra['v-show'] = "showingPackages == 'all'"
        return extra

    def changelog_link(self, project, url):
        return tags.link_to(project, url, target='_blank')

    commit_hash_pattern = re.compile(r'^.{40}$')

    def get_changelog_projects(self):
        project_map = {
            'onager': 'onager',
            'pyCOREPOS': 'pycorepos',
            'rattail': 'rattail',
            'rattail_corepos': 'rattail-corepos',
            'rattail-onager': 'rattail-onager',
            'rattail_tempmon': 'rattail-tempmon',
            'rattail_woocommerce': 'rattail-woocommerce',
            'Tailbone': 'tailbone',
            'tailbone_corepos': 'tailbone-corepos',
            'tailbone-onager': 'tailbone-onager',
            'tailbone_theo': 'theo',
            'tailbone_woocommerce': 'tailbone-woocommerce',
        }

        projects = {}
        for name, repo in project_map.items():
            projects[name] = {
                'commit_url': f'https://forgejo.wuttaproject.org/rattail/{repo}/compare/{{old_version}}...{{new_version}}',
                'release_url': f'https://forgejo.wuttaproject.org/rattail/{repo}/src/tag/v{{new_version}}/CHANGELOG.md',
            }
        return projects

    def get_changelog_url(self, project, old_version, new_version):
        # cannot generate URL if new version is unknown
        if not new_version:
            return

        projects = self.get_changelog_projects()

        project_name = project
        if project_name not in projects:
            # cannot generate a changelog URL for unknown project
            return

        project = projects[project_name]

        if self.commit_hash_pattern.match(new_version):
            return project['commit_url'].format(new_version=new_version, old_version=old_version)

        elif re.match(r'^\d+\.\d+\.\d+$', new_version):
            return project['release_url'].format(new_version=new_version, old_version=old_version)

    def render_diff_field(self, field, diff):
        old_version = diff.old_value(field)
        new_version = diff.new_value(field)
        url = self.get_changelog_url(field, old_version, new_version)
        if url:
            return self.changelog_link(field, url)
        return field

    def render_diff_value(self, field, value):
        if value is None:
            return ""
        if value.startswith("u'") and value.endswith("'"):
            return value[2:1]
        return value

    def parse_requirements(self, upgrade, type_):
        packages = {}
        path = self.rattail_config.upgrade_filepath(upgrade.uuid, filename='requirements.{}.txt'.format(type_))
        with open(path, 'rt') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#'):
                    req = self.parse_requirement(line)
                    if req:
                        packages[req.name] = req.version
                    else:
                        log.warning("could not parse req from line: %s", line)
        return packages

    def parse_requirement(self, line):
        app = self.get_rattail_app()
        match = re.match(r'^.*@(.*)#egg=(.*)$', line)
        if match:
            return app.make_object(name=match.group(2), version=match.group(1))

        match = re.match(r'^(.*)==(.*)$', line)
        if match:
            return app.make_object(name=match.group(1), version=match.group(2))

    def download_path(self, upgrade, filename):
        return self.rattail_config.upgrade_filepath(upgrade.uuid, filename=filename)

    def download_content_type(self, path, filename):
        return 'text/plain'

    def before_create_flush(self, upgrade, form):
        upgrade.created_by = self.request.user
        upgrade.status_code = self.enum.UPGRADE_STATUS_PENDING

    # TODO: this was an attempt to make the progress bar survive Apache restart,
    # but it didn't work...  need to "fork" instead of waiting for execution?
    # def make_execute_progress(self):
    #     key = '{}.execute'.format(self.get_grid_key())
    #     return SessionProgress(self.request, key, session_type='file')

    def executable_instance(self, upgrade):
        if upgrade.executed:
            return False
        if upgrade.status_code != self.enum.UPGRADE_STATUS_PENDING:
            return False
        return True

    def execute_instance(self, upgrade, user, progress=None, **kwargs):
        app = self.get_rattail_app()
        session = app.get_session(upgrade)

        # record the fact that execution has begun for this ugprade
        self.upgrade_handler.mark_executing(upgrade)
        session.commit()

        # let handler execute the upgrade
        self.upgrade_handler.do_execute(upgrade, user, **kwargs)

        # success msg
        msg = "Execution has finished, for better or worse."
        if not upgrade.system or upgrade.system == 'rattail':
            msg += "  You may need to restart your web app."
        return msg

    def execute_progress(self):
        upgrade = self.get_instance()
        key = '{}.execute'.format(self.get_grid_key())
        session = get_progress_session(self.request, key)
        if session.get('complete'):
            msg = session.get('success_msg')
            if msg:
                self.request.session.flash(msg)
        elif session.get('error'):
            self.request.session.flash(session.get('error_msg', "An unspecified error occurred."), 'error')
        data = dict(session)

        path = self.rattail_config.upgrade_filepath(upgrade.uuid, filename='stdout.log')
        offset = session.get('stdout.offset', 0)
        if os.path.exists(path):
            size = os.path.getsize(path) - offset
            if size > 0:
                with open(path, 'rb') as f:
                    f.seek(offset)
                    chunk = f.read(size)
                    data['stdout'] = chunk.decode('utf8').replace('\n', '<br />')
                session['stdout.offset'] = offset + size
                session.save()

        return data

    def declare_failure(self):
        upgrade = self.get_instance()
        if upgrade.executing and upgrade.status_code == self.enum.UPGRADE_STATUS_EXECUTING:
            upgrade.executing = False
            upgrade.status_code = self.enum.UPGRADE_STATUS_FAILED
            self.request.session.flash("Upgrade was declared a failure.", 'warning')
        else:
            self.request.session.flash("Upgrade was not currently executing!  "
                                       "So it was not declared a failure.",
                                       'error')
        return self.redirect(self.get_action_url('view', upgrade))

    def delete_instance(self, upgrade):
        self.handler.delete_files(upgrade)
        super().delete_instance(upgrade)

    def configure_get_context(self, **kwargs):
        context = super().configure_get_context(**kwargs)

        context['upgrade_systems'] = self.upgrade_handler.get_all_systems()

        return context

    def configure_gather_settings(self, data):
        settings = super().configure_gather_settings(data)

        keys = []
        for system in json.loads(data['upgrade_systems']):
            key = system['key']
            if key == 'rattail':
                settings.append({'name': 'rattail.upgrades.command',
                                 'value': system['command']})
            else:
                keys.append(key)
                settings.append({'name': 'rattail.upgrades.system.{}.label'.format(key),
                                 'value': system['label']})
                settings.append({'name': 'rattail.upgrades.system.{}.command'.format(key),
                                 'value': system['command']})
        if keys:
            settings.append({'name': 'rattail.upgrades.systems',
                             'value': ', '.join(keys)})

        return settings

    def configure_remove_settings(self):
        super().configure_remove_settings()
        app = self.get_rattail_app()
        model = self.model

        to_delete = self.Session.query(model.Setting)\
                           .filter(sa.or_(
                               model.Setting.name == 'rattail.upgrades.command',
                               model.Setting.name == 'rattail.upgrades.systems',
                               model.Setting.name.like('rattail.upgrades.system.%.label'),
                               model.Setting.name.like('rattail.upgrades.system.%.command')))\
                           .all()

        for setting in to_delete:
            app.delete_setting(self.Session(), setting.name)

    @classmethod
    def defaults(cls, config):
        cls._defaults(config)
        cls._upgrade_defaults(config)

    @classmethod
    def _upgrade_defaults(cls, config):
        route_prefix = cls.get_route_prefix()
        permission_prefix = cls.get_permission_prefix()
        instance_url_prefix = cls.get_instance_url_prefix()
        model_key = cls.get_model_key()

        # execution progress
        config.add_route('{}.execute_progress'.format(route_prefix),
                         '{}/execute/progress'.format(instance_url_prefix))
        config.add_view(cls, attr='execute_progress',
                        route_name='{}.execute_progress'.format(route_prefix),
                        permission='{}.execute'.format(permission_prefix),
                        renderer='json')

        # declare failure
        config.add_route('{}.declare_failure'.format(route_prefix),
                         '{}/declare-failure'.format(instance_url_prefix),
                         request_method='POST')
        config.add_view(cls, attr='declare_failure',
                        route_name='{}.declare_failure'.format(route_prefix),
                        permission='{}.execute'.format(permission_prefix))


def defaults(config, **kwargs):
    base = globals()
    rattail_config = config.registry['rattail_config']

    UpgradeView = kwargs.get('UpgradeView', base['UpgradeView'])
    UpgradeView.defaults(config)

    if should_expose_websockets(rattail_config):
        config.include('tailbone.views.asgi.upgrades')


def includeme(config):
    defaults(config)
