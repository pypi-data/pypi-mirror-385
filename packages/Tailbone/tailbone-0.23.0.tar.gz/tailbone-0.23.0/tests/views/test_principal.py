# -*- coding: utf-8; -*-

from unittest.mock import patch, MagicMock

from tailbone.views import principal as mod
from tests.util import WebTestCase


class TestPrincipalMasterView(WebTestCase):

    def make_view(self):
        return mod.PrincipalMasterView(self.request)

    def test_find_by_perm(self):
        model = self.app.model
        self.config.setdefault('rattail.web.menus.handler_spec', 'tests.util:NullMenuHandler')
        self.pyramid_config.include('tailbone.views.common')
        self.pyramid_config.include('tailbone.views.auth')
        self.pyramid_config.add_route('roles', '/roles/')
        with patch.multiple(mod.PrincipalMasterView, create=True,
                            model_class=model.Role,
                            get_help_url=MagicMock(return_value=None),
                            get_help_markdown=MagicMock(return_value=None),
                            can_edit_help=MagicMock(return_value=False)):

            # sanity / coverage check
            view = self.make_view()
            response = view.find_by_perm()
            self.assertEqual(response.status_code, 200)
