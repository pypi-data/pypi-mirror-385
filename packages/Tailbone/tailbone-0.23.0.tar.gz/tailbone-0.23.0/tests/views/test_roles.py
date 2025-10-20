# -*- coding: utf-8; -*-

from unittest.mock import patch

from tailbone.views import roles as mod
from tests.util import WebTestCase


class TestRoleView(WebTestCase):

    def make_view(self):
        return mod.RoleView(self.request)

    def test_includeme(self):
        self.pyramid_config.include('tailbone.views.roles')

    def get_permissions(self):
        return {
            'widgets': {
                'label': "Widgets",
                'perms': {
                    'widgets.list': {
                        'label': "List widgets",
                    },
                    'widgets.polish': {
                        'label': "Polish the widgets",
                    },
                    'widgets.view': {
                        'label': "View widget",
                    },
                },
            },
        }

    def test_get_available_permissions(self):
        model = self.app.model
        auth = self.app.get_auth_handler()
        blokes = model.Role(name="Blokes")
        auth.grant_permission(blokes, 'widgets.list')
        self.session.add(blokes)
        barney = model.User(username='barney')
        barney.roles.append(blokes)
        self.session.add(barney)
        self.session.commit()
        view = self.make_view()
        all_perms = self.get_permissions()
        self.request.registry.settings['wutta_permissions'] = all_perms

        def has_perm(perm):
            if perm == 'widgets.list':
                return True
            return False

        with patch.object(self.request, 'has_perm', new=has_perm, create=True):

            # sanity check; current request has 1 perm
            self.assertTrue(self.request.has_perm('widgets.list'))
            self.assertFalse(self.request.has_perm('widgets.polish'))
            self.assertFalse(self.request.has_perm('widgets.view'))

            # when editing, user sees only the 1 perm
            with patch.object(view, 'editing', new=True):
                perms = view.get_available_permissions()
                self.assertEqual(list(perms), ['widgets'])
                self.assertEqual(list(perms['widgets']['perms']), ['widgets.list'])

            # but when viewing, same user sees all perms
            with patch.object(view, 'viewing', new=True):
                perms = view.get_available_permissions()
                self.assertEqual(list(perms), ['widgets'])
                self.assertEqual(list(perms['widgets']['perms']),
                                 ['widgets.list', 'widgets.polish', 'widgets.view'])

            # also, when admin user is editing, sees all perms
            self.request.is_admin = True
            with patch.object(view, 'editing', new=True):
                perms = view.get_available_permissions()
                self.assertEqual(list(perms), ['widgets'])
                self.assertEqual(list(perms['widgets']['perms']),
                                 ['widgets.list', 'widgets.polish', 'widgets.view'])
