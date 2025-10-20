# -*- coding: utf-8; -*-

from tailbone.views import settings as mod
from tests.util import WebTestCase


class TestSettingView(WebTestCase):

    def test_includeme(self):
        self.pyramid_config.include('tailbone.views.settings')
