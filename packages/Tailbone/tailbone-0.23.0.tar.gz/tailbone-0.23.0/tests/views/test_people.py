# -*- coding: utf-8; -*-

from tailbone.views import users as mod
from tests.util import WebTestCase


class TestPersonView(WebTestCase):

    def make_view(self):
        return mod.PersonView(self.request)

    def test_includeme(self):
        self.pyramid_config.include('tailbone.views.people')

    def test_includeme_wutta(self):
        self.config.setdefault('tailbone.use_wutta_views', 'true')
        self.pyramid_config.include('tailbone.views.people')
