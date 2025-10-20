# -*- coding: utf-8; -*-

from unittest.mock import patch, MagicMock

from tailbone.views import users as mod
from tailbone.views.principal import PermissionsRenderer
from tests.util import WebTestCase


class TestUserView(WebTestCase):

    def make_view(self):
        return mod.UserView(self.request)

    def test_includeme(self):
        self.pyramid_config.include('tailbone.views.users')

    def test_configure_form(self):
        self.pyramid_config.include('tailbone.views.users')
        model = self.app.model
        barney = model.User(username='barney')
        self.session.add(barney)
        self.session.commit()
        view = self.make_view()

        # must use mock configure when making form
        def configure(form): pass
        form = view.make_form(instance=barney, configure=configure)

        with patch.object(view, 'viewing', new=True):
            self.assertNotIn('permissions', form.renderers)
            view.configure_form(form)
            self.assertIsInstance(form.renderers['permissions'], PermissionsRenderer)
