# -*- coding: utf-8; -*-

from unittest.mock import MagicMock

from pyramid import testing

from tailbone import subscribers
from wuttaweb.menus import MenuHandler
# from wuttaweb.subscribers import new_request_set_user
from rattail.testing import DataTestCase


class WebTestCase(DataTestCase):
    """
    Base class for test suites requiring a full (typical) web app.
    """

    def setUp(self):
        self.setup_web()

    def setup_web(self):
        self.setup_db()
        self.request = self.make_request()
        self.pyramid_config = testing.setUp(request=self.request, settings={
            'wutta_config': self.config,
            'rattail_config': self.config,
            'mako.directories': ['tailbone:templates', 'wuttaweb:templates'],
            # 'pyramid_deform.template_search_path': 'wuttaweb:templates/deform',
        })

        # init web
        # self.pyramid_config.include('pyramid_deform')
        self.pyramid_config.include('pyramid_mako')
        self.pyramid_config.add_directive('add_wutta_permission_group',
                                          'wuttaweb.auth.add_permission_group')
        self.pyramid_config.add_directive('add_wutta_permission',
                                          'wuttaweb.auth.add_permission')
        self.pyramid_config.add_directive('add_tailbone_permission_group',
                                          'wuttaweb.auth.add_permission_group')
        self.pyramid_config.add_directive('add_tailbone_permission',
                                          'wuttaweb.auth.add_permission')
        self.pyramid_config.add_directive('add_tailbone_index_page',
                                          'tailbone.app.add_index_page')
        self.pyramid_config.add_directive('add_tailbone_model_view',
                                          'tailbone.app.add_model_view')
        self.pyramid_config.add_directive('add_tailbone_config_page',
                                          'tailbone.app.add_config_page')
        self.pyramid_config.add_subscriber('tailbone.subscribers.before_render',
                                           'pyramid.events.BeforeRender')
        self.pyramid_config.include('tailbone.static')

        # setup new request w/ anonymous user
        event = MagicMock(request=self.request)
        subscribers.new_request(event, session=self.session)
        # def user_getter(request, **kwargs): pass
        # new_request_set_user(event, db_session=self.session,
        #                      user_getter=user_getter)

    def tearDown(self):
        self.teardown_web()

    def teardown_web(self):
        testing.tearDown()
        self.teardown_db()

    def make_request(self, **kwargs):
        kwargs.setdefault('rattail_config', self.config)
        # kwargs.setdefault('wutta_config', self.config)
        return testing.DummyRequest(**kwargs)


class NullMenuHandler(MenuHandler):
    """
    Dummy menu handler for testing.
    """
    def make_menus(self, request, **kwargs):
        return []
