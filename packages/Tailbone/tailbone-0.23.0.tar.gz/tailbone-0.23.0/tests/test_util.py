# -*- coding: utf-8; -*-

from unittest import TestCase

from pyramid import testing

from rattail.config import RattailConfig

from tailbone import util


class TestGetFormData(TestCase):

    def setUp(self):
        self.config = RattailConfig()

    def make_request(self, **kwargs):
        kwargs.setdefault('wutta_config', self.config)
        kwargs.setdefault('rattail_config', self.config)
        kwargs.setdefault('is_xhr', None)
        kwargs.setdefault('content_type', None)
        kwargs.setdefault('POST', {'foo1': 'bar'})
        kwargs.setdefault('json_body', {'foo2': 'baz'})
        return testing.DummyRequest(**kwargs)

    def test_default(self):
        request = self.make_request()
        data = util.get_form_data(request)
        self.assertEqual(data, {'foo1': 'bar'})

    def test_is_xhr(self):
        request = self.make_request(POST=None, is_xhr=True)
        data = util.get_form_data(request)
        self.assertEqual(data, {'foo2': 'baz'})

    def test_content_type(self):
        request = self.make_request(POST=None, content_type='application/json')
        data = util.get_form_data(request)
        self.assertEqual(data, {'foo2': 'baz'})
