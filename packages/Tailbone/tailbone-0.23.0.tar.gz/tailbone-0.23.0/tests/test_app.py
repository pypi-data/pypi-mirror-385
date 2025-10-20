# -*- coding: utf-8; -*-

import os
from unittest import TestCase

from pyramid.config import Configurator

from rattail.exceptions import ConfigurationError
from rattail.testing import DataTestCase
from tailbone import app as mod


class TestRattailConfig(TestCase):

    config_path = os.path.abspath(
        os.path.join(os.path.dirname(__file__), 'data', 'tailbone.conf'))

    def test_settings_arg_must_include_config_path_by_default(self):
        # error raised if path not provided
        self.assertRaises(ConfigurationError, mod.make_rattail_config, {})
        # get a config object if path provided
        result = mod.make_rattail_config({'rattail.config': self.config_path})
        # nb. cannot test isinstance(RattailConfig) b/c now uses wrapper!
        self.assertIsNotNone(result)
        self.assertTrue(hasattr(result, 'get'))


class TestMakePyramidConfig(DataTestCase):

    def make_config(self, **kwargs):
        myconf = self.write_file('web.conf', """
[rattail.db]
default.url = sqlite://
""")

        self.settings = {
            'rattail.config': myconf,
            'mako.directories': 'tailbone:templates',
        }
        return mod.make_rattail_config(self.settings)

    def test_basic(self):
        model = self.app.model
        model.Base.metadata.create_all(bind=self.config.appdb_engine)

        # sanity check
        pyramid_config = mod.make_pyramid_config(self.settings)
        self.assertIsInstance(pyramid_config, Configurator)
