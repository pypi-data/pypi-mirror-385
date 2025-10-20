# -*- coding: utf-8; -*-

from unittest.mock import patch

from sqlalchemy import orm

from tailbone.views.wutta import people as mod
from tests.util import WebTestCase


class TestPersonView(WebTestCase):

    def make_view(self):
        return mod.PersonView(self.request)

    def test_includeme(self):
        self.pyramid_config.include('tailbone.views.wutta.people')

    def test_get_query(self):
        view = self.make_view()

        # sanity / coverage check
        query = view.get_query(session=self.session)
        self.assertIsInstance(query, orm.Query)

    def test_configure_grid(self):
        model = self.app.model
        barney = model.User(username='barney')
        self.session.add(barney)
        self.session.commit()
        view = self.make_view()

        # sanity / coverage check
        grid = view.make_grid(model_class=model.Person)
        self.assertNotIn('first_name', grid.linked_columns)
        view.configure_grid(grid)
        self.assertIn('first_name', grid.linked_columns)

    def test_configure_form(self):
        model = self.app.model
        barney = model.Person(display_name="Barney Rubble")
        self.session.add(barney)
        self.session.commit()
        view = self.make_view()

        # email field remains when viewing
        with patch.object(view, 'viewing', new=True):
            form = view.make_form(model_instance=barney,
                                  fields=view.get_form_fields())
            self.assertIn('email', form.fields)
            view.configure_form(form)
            self.assertIn('email', form)

        # email field removed when editing
        with patch.object(view, 'editing', new=True):
            form = view.make_form(model_instance=barney,
                                  fields=view.get_form_fields())
            self.assertIn('email', form.fields)
            view.configure_form(form)
            self.assertNotIn('email', form)

    def test_render_merge_requested(self):
        model = self.app.model
        barney = model.Person(display_name="Barney Rubble")
        self.session.add(barney)
        user = model.User(username='user')
        self.session.add(user)
        self.session.commit()
        view = self.make_view()

        # null by default
        html = view.render_merge_requested(barney, 'merge_requested', None,
                                           session=self.session)
        self.assertIsNone(html)

        # unless a merge request exists
        barney2 = model.Person(display_name="Barney Rubble")
        self.session.add(barney2)
        self.session.commit()
        mr = model.MergePeopleRequest(removing_uuid=barney2.uuid,
                                      keeping_uuid=barney.uuid,
                                      requested_by=user)
        self.session.add(mr)
        self.session.commit()
        html = view.render_merge_requested(barney, 'merge_requested', None,
                                           session=self.session)
        self.assertIn('<span ', html)
