# -*- coding: utf-8; -*-

from unittest.mock import MagicMock

from pyramid import testing

from tailbone import subscribers as mod
from tests.util import DataTestCase


class TestNewRequest(DataTestCase):

    def setUp(self):
        self.setup_db()
        self.request = self.make_request()
        self.pyramid_config = testing.setUp(request=self.request, settings={
            'wutta_config': self.config,
        })

    def tearDown(self):
        self.teardown_db()
        testing.tearDown()

    def make_request(self, **kwargs):
        return testing.DummyRequest(**kwargs)

    def make_event(self):
        return MagicMock(request=self.request)

    def test_continuum_remote_addr(self):
        event = self.make_event()

        # nothing happens
        mod.new_request(event, session=self.session)
        self.assertFalse(hasattr(self.session, 'continuum_remote_addr'))

        # unless request has client_addr
        self.request.client_addr = '127.0.0.1'
        mod.new_request(event, session=self.session)
        self.assertEqual(self.session.continuum_remote_addr, '127.0.0.1')

    def test_register_component(self):
        event = self.make_event()

        # function added
        self.assertFalse(hasattr(self.request, 'register_component'))
        mod.new_request(event, session=self.session)
        self.assertTrue(callable(self.request.register_component))

        # call function
        self.request.register_component('tailbone-datepicker', 'TailboneDatepicker')
        self.assertEqual(self.request._tailbone_registered_components,
                         {'tailbone-datepicker': 'TailboneDatepicker'})

        # duplicate registration ignored
        self.request.register_component('tailbone-datepicker', 'TailboneDatepicker')
        self.assertEqual(self.request._tailbone_registered_components,
                         {'tailbone-datepicker': 'TailboneDatepicker'})
