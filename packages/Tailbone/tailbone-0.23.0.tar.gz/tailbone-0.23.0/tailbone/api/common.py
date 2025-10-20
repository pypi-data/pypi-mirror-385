# -*- coding: utf-8; -*-
################################################################################
#
#  Rattail -- Retail Software Framework
#  Copyright © 2010-2024 Lance Edgar
#
#  This file is part of Rattail.
#
#  Rattail is free software: you can redistribute it and/or modify it under the
#  terms of the GNU General Public License as published by the Free Software
#  Foundation, either version 3 of the License, or (at your option) any later
#  version.
#
#  Rattail is distributed in the hope that it will be useful, but WITHOUT ANY
#  WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
#  FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more
#  details.
#
#  You should have received a copy of the GNU General Public License along with
#  Rattail.  If not, see <http://www.gnu.org/licenses/>.
#
################################################################################
"""
Tailbone Web API - "Common" Views
"""

from collections import OrderedDict

from rattail.util import get_pkg_version

from cornice import Service
from cornice.service import get_services
from cornice_swagger import CorniceSwagger

from tailbone import forms
from tailbone.forms.common import Feedback
from tailbone.api import APIView, api
from tailbone.db import Session


class CommonView(APIView):
    """
    Misc. "common" views for the API.

    .. attribute:: feedback_email_key

       This is the email key which will be used when sending "user feedback"
       email.  Default value is ``'user_feedback'``.
    """
    feedback_email_key = 'user_feedback'

    @api
    def about(self):
        """
        Generic view to show "about project" info page.
        """
        packages = self.get_packages()
        return {
            'project_title': self.get_project_title(),
            'project_version': self.get_project_version(),
            'packages': packages,
            'package_names': list(packages),
        }

    def get_project_title(self):
        app = self.get_rattail_app()
        return app.get_title()

    def get_project_version(self):
        app = self.get_rattail_app()
        return app.get_version()

    def get_packages(self):
        """
        Should return the full set of packages which should be displayed on the
        'about' page.
        """
        return OrderedDict([
            ('rattail', get_pkg_version('rattail')),
            ('Tailbone', get_pkg_version('Tailbone')),
        ])

    @api
    def feedback(self):
        """
        View to handle user feedback form submits.
        """
        app = self.get_rattail_app()
        model = self.model
        # TODO: this logic was copied from tailbone.views.common and is largely
        # identical; perhaps should merge somehow?
        schema = Feedback().bind(session=Session())
        form = forms.Form(schema=schema, request=self.request)
        if form.validate():
            data = dict(form.validated)

            # figure out who the sending user is, if any
            if self.request.user:
                data['user'] = self.request.user
            elif data['user']:
                data['user'] = Session.get(model.User, data['user'])

            # TODO: should provide URL to view user
            if data['user']:
                data['user_url'] = '#' # TODO: could get from config?

            data['client_ip'] = self.request.client_addr
            email_key = data['email_key'] or self.feedback_email_key
            app.send_email(email_key, data=data)
            return {'ok': True}

        return {'error': "Form did not validate!"}

    def swagger(self):
        doc = CorniceSwagger(get_services())
        app = self.get_rattail_app()
        spec = doc.generate(f"{app.get_node_title()} API docs",
                            app.get_version(),
                            base_path='/api') # TODO
        return spec

    @classmethod
    def defaults(cls, config):
        cls._common_defaults(config)

    @classmethod
    def _common_defaults(cls, config):
        rattail_config = config.registry.settings.get('rattail_config')
        app = rattail_config.get_app()

        # about
        about = Service(name='about', path='/about')
        about.add_view('GET', 'about', klass=cls)
        config.add_cornice_service(about)

        # feedback
        feedback = Service(name='feedback', path='/feedback')
        feedback.add_view('POST', 'feedback', klass=cls,
                          permission='common.feedback')
        config.add_cornice_service(feedback)

        # swagger
        swagger = Service(name='swagger',
                          path='/swagger.json',
                          description=f"OpenAPI documentation for {app.get_title()}")
        swagger.add_view('GET', 'swagger', klass=cls,
                         permission='common.api_swagger')
        config.add_cornice_service(swagger)


def defaults(config, **kwargs):
    base = globals()

    CommonView = kwargs.get('CommonView', base['CommonView'])
    CommonView.defaults(config)


def includeme(config):
    defaults(config)
