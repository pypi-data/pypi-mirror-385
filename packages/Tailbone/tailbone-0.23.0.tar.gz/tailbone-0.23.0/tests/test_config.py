# -*- coding: utf-8; -*-

from tailbone import config as mod
from tests.util import DataTestCase


class TestConfigExtension(DataTestCase):

    def test_basic(self):
        # sanity / coverage check
        ext = mod.ConfigExtension()
        ext.configure(self.config)
