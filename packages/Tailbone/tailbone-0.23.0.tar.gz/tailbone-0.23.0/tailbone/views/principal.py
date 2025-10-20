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
"Principal" master view
"""

import copy
from collections import OrderedDict

from rattail.core import Object

from webhelpers2.html import HTML

from tailbone.db import Session
from tailbone.views import MasterView


class PrincipalMasterView(MasterView):
    """
    Master view base class for security principal models, i.e. User and Role.
    """

    def get_fallback_templates(self, template, **kwargs):
        return [
            '/principal/{}.mako'.format(template),
        ] + super().get_fallback_templates(template, **kwargs)

    def perm_sortkey(self, item):
        key, value = item
        return value['label'].lower()

    def find_by_perm(self):
        """
        View for finding all users who have been granted a given permission
        """
        permissions = copy.deepcopy(
            self.request.registry.settings.get('wutta_permissions', {}))

        # sort groups, and permissions for each group, for UI's sake
        sorted_perms = sorted(permissions.items(), key=self.perm_sortkey)
        for key, group in sorted_perms:
            group['perms'] = sorted(group['perms'].items(), key=self.perm_sortkey)

        # if both field values are in query string, do lookup
        principals = None
        permission_group = self.request.GET.get('permission_group')
        permission = self.request.GET.get('permission')
        grid = None
        if permission_group and permission:
            principals = self.find_principals_with_permission(self.Session(),
                                                              permission)
            grid = self.find_by_perm_make_results_grid(principals)
        else: # otherwise clear both values
            permission_group = None
            permission = None

        context = {
            'permissions': sorted_perms,
            'principals': principals,
            'principals_data': self.find_by_perm_results_data(principals),
            'grid': grid,
        }

        perms = self.get_perms_data(sorted_perms)
        context['perms_data'] = perms
        context['sorted_groups_data'] = list(perms)

        if permission_group and permission_group not in perms:
            permission_group = None
        if permission:
            if permission_group:
                group = dict([(p['permkey'], p) for p in perms[permission_group]['permissions']])
                if permission in group:
                    context['selected_permission_label'] = group[permission]['label']
                else:
                    permission = None
            else:
                permission = None

        context['selected_group'] = permission_group
        context['selected_permission'] = permission

        return self.render_to_response('find_by_perm', context)

    def get_perms_data(self, sorted_perms):
        data = OrderedDict()
        for gkey, group in sorted_perms:

            gperms = []
            for pkey, perm in group['perms']:
                gperms.append({
                    'permkey': pkey,
                    'label': perm['label'],
                })

            data[gkey] = {
                'groupkey': gkey,
                'label': group['label'],
                'permissions': gperms,
            }

        return data

    def find_by_perm_make_results_grid(self, principals):
        route_prefix = self.get_route_prefix()
        factory = self.get_grid_factory()
        g = factory(self.request,
                    key=f'{route_prefix}.results',
                    data=[],
                    columns=[],
                    actions=[
                        self.make_action('view', icon='eye',
                                         click_handler='navigateTo(props.row._url)'),
                    ])
        self.find_by_perm_configure_results_grid(g)
        return g

    def find_by_perm_configure_results_grid(self, g):
        pass

    def find_by_perm_results_data(self, principals):
        data = []
        for principal in principals or []:
            data.append(self.find_by_perm_normalize(principal))
        return data

    def find_by_perm_normalize(self, principal):
        return {
            'uuid': principal.uuid,
            '_url': self.get_action_url('view', principal),
        }

    @classmethod
    def defaults(cls, config):
        cls._principal_defaults(config)
        cls._defaults(config)

    @classmethod
    def _principal_defaults(cls, config):
        route_prefix = cls.get_route_prefix()
        url_prefix = cls.get_url_prefix()
        permission_prefix = cls.get_permission_prefix()
        model_title_plural = cls.get_model_title_plural()

        # find principal by permission
        config.add_route('{}.find_by_perm'.format(route_prefix),
                         '{}/find-by-perm'.format(url_prefix),
                         request_method='GET')
        config.add_view(cls, attr='find_by_perm',
                        route_name='{}.find_by_perm'.format(route_prefix),
                        permission='{}.find_by_perm'.format(permission_prefix))
        config.add_tailbone_permission(permission_prefix, '{}.find_by_perm'.format(permission_prefix),
                                       "Find all {} with permission X".format(model_title_plural))


class PermissionsRenderer(Object):
    permissions = None
    include_guest = False
    include_authenticated = False

    def __call__(self, principal, field):
        self.principal = principal
        return self.render()

    def render(self):
        app = self.request.rattail_config.get_app()
        auth = app.get_auth_handler()

        principal = self.principal
        html = ''
        for groupkey in sorted(self.permissions, key=lambda k: self.permissions[k]['label'].lower()):
            inner = HTML.tag('p', class_='group-label', c=self.permissions[groupkey]['label'])
            perms = self.permissions[groupkey]['perms']
            rendered = False
            for key in sorted(perms, key=lambda p: perms[p]['label'].lower()):
                checked = auth.has_permission(Session(), principal, key,
                                              include_anonymous=self.include_guest,
                                              include_authenticated=self.include_authenticated)
                if checked:
                    label = perms[key]['label']
                    span = HTML.tag('span', c="[X]" if checked else "[ ]")
                    inner += HTML.tag('p', class_='perm', c=[span, HTML(' '), label])
                    rendered = True
            if rendered:
                html += HTML.tag('div', class_='permissions-group', c=[inner])
        return HTML.tag('div', class_='permissions-outer', c=[html or "(none granted)"])
