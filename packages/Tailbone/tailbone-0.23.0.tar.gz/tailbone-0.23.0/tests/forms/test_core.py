# -*- coding: utf-8; -*-

from unittest.mock import patch

import deform
from pyramid import testing

from tailbone.forms import core as mod
from tests.util import WebTestCase


class TestForm(WebTestCase):

    def setUp(self):
        self.setup_web()
        self.config.setdefault('rattail.web.menus.handler_spec', 'tests.util:NullMenuHandler')

    def make_form(self, **kwargs):
        kwargs.setdefault('request', self.request)
        return mod.Form(**kwargs)

    def test_basic(self):
        form = self.make_form()
        self.assertIsInstance(form, mod.Form)

    def test_vue_tagname(self):

        # default
        form = self.make_form()
        self.assertEqual(form.vue_tagname, 'tailbone-form')

        # can override with param
        form = self.make_form(vue_tagname='something-else')
        self.assertEqual(form.vue_tagname, 'something-else')

        # can still pass old param
        form = self.make_form(component='legacy-name')
        self.assertEqual(form.vue_tagname, 'legacy-name')

    def test_vue_component(self):

        # default
        form = self.make_form()
        self.assertEqual(form.vue_component, 'TailboneForm')

        # can override with param
        form = self.make_form(vue_tagname='something-else')
        self.assertEqual(form.vue_component, 'SomethingElse')

        # can still pass old param
        form = self.make_form(component='legacy-name')
        self.assertEqual(form.vue_component, 'LegacyName')

    def test_component(self):

        # default
        form = self.make_form()
        self.assertEqual(form.component, 'tailbone-form')

        # can override with param
        form = self.make_form(vue_tagname='something-else')
        self.assertEqual(form.component, 'something-else')

        # can still pass old param
        form = self.make_form(component='legacy-name')
        self.assertEqual(form.component, 'legacy-name')

    def test_component_studly(self):

        # default
        form = self.make_form()
        self.assertEqual(form.component_studly, 'TailboneForm')

        # can override with param
        form = self.make_form(vue_tagname='something-else')
        self.assertEqual(form.component_studly, 'SomethingElse')

        # can still pass old param
        form = self.make_form(component='legacy-name')
        self.assertEqual(form.component_studly, 'LegacyName')

    def test_button_label_submit(self):
        form = self.make_form()

        # default
        self.assertEqual(form.button_label_submit, "Submit")

        # can set submit_label
        with patch.object(form, 'submit_label', new="Submit Label", create=True):
            self.assertEqual(form.button_label_submit, "Submit Label")

        # can set save_label
        with patch.object(form, 'save_label', new="Save Label"):
            self.assertEqual(form.button_label_submit, "Save Label")

        # can set button_label_submit
        form.button_label_submit = "New Label"
        self.assertEqual(form.button_label_submit, "New Label")

    def test_get_deform(self):
        model = self.app.model

        # sanity check
        form = self.make_form(model_class=model.Setting)
        dform = form.get_deform()
        self.assertIsInstance(dform, deform.Form)

    def test_render_vue_tag(self):
        model = self.app.model

        # sanity check
        form = self.make_form(model_class=model.Setting)
        html = form.render_vue_tag()
        self.assertIn('<tailbone-form', html)

    def test_render_vue_template(self):
        self.pyramid_config.include('tailbone.views.common')
        model = self.app.model

        # sanity check
        form = self.make_form(model_class=model.Setting)
        html = form.render_vue_template(session=self.session)
        self.assertIn('<form ', html)

    def test_get_vue_field_value(self):
        model = self.app.model
        form = self.make_form(model_class=model.Setting)

        # TODO: yikes what a hack (?)
        dform = form.get_deform()
        dform.set_appstruct({'name': 'foo', 'value': 'bar'})

        # null for missing field
        value = form.get_vue_field_value('doesnotexist')
        self.assertIsNone(value)

        # normal value is returned
        value = form.get_vue_field_value('name')
        self.assertEqual(value, 'foo')

        # but not if we remove field from deform
        # TODO: what is the use case here again?
        dform.children.remove(dform['name'])
        value = form.get_vue_field_value('name')
        self.assertIsNone(value)

    def test_render_vue_field(self):
        model = self.app.model

        # sanity check
        form = self.make_form(model_class=model.Setting)
        html = form.render_vue_field('name', session=self.session)
        self.assertIn('<b-field ', html)
