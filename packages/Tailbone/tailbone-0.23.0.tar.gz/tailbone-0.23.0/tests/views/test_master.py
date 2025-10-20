# -*- coding: utf-8; -*-

from unittest.mock import patch, MagicMock

from tailbone.views import master as mod
from wuttaweb.grids import GridAction
from tests.util import WebTestCase


class TestMasterView(WebTestCase):

    def make_view(self):
        return mod.MasterView(self.request)

    def test_make_form_kwargs(self):
        self.pyramid_config.add_route('settings.view', '/settings/{name}')
        model = self.app.model
        setting = model.Setting(name='foo', value='bar')
        self.session.add(setting)
        self.session.commit()
        with patch.multiple(mod.MasterView, create=True,
                            model_class=model.Setting):
            view = self.make_view()

            # sanity / coverage check
            kw = view.make_form_kwargs(model_instance=setting)
            self.assertIsNotNone(kw['action_url'])

    def test_make_action(self):
        model = self.app.model
        with patch.multiple(mod.MasterView, create=True,
                            model_class=model.Setting):
            view = self.make_view()
            action = view.make_action('view')
            self.assertIsInstance(action, GridAction)

    def test_index(self):
        self.pyramid_config.include('tailbone.views.common')
        self.pyramid_config.include('tailbone.views.auth')
        model = self.app.model

        # mimic view for /settings
        with patch.object(mod, 'Session', return_value=self.session):
            with patch.multiple(mod.MasterView, create=True,
                                model_class=model.Setting,
                                Session=MagicMock(return_value=self.session),
                                get_index_url=MagicMock(return_value='/settings/'),
                                get_help_url=MagicMock(return_value=None)):

                # basic
                view = self.make_view()
                response = view.index()
                self.assertEqual(response.status_code, 200)

                # then again with data, to include view action url
                data = [{'name': 'foo', 'value': 'bar'}]
                with patch.object(view, 'get_data', return_value=data):
                    response = view.index()
                    self.assertEqual(response.status_code, 200)
                    self.assertEqual(response.content_type, 'text/html')

                    # then once more as 'partial' - aka. data only
                    self.request.GET = {'partial': '1'}
                    response = view.index()
                    self.assertEqual(response.status_code, 200)
                    self.assertEqual(response.content_type, 'application/json')
