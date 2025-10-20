# -*- coding: utf-8; -*-
################################################################################
#
#  Rattail -- Retail Software Framework
#  Copyright © 2010-2023 Lance Edgar
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
Views for Email Bounces
"""

import os
import datetime

from rattail.db import model
from rattail.bouncer.config import get_profile_keys

from webhelpers2.html import HTML, tags

from tailbone.views import MasterView


class EmailBounceView(MasterView):
    """
    Master view for email bounces.
    """
    model_class = model.EmailBounce
    model_title_plural = "Email Bounces"
    url_prefix = '/email-bounces'
    creatable = False
    editable = False
    downloadable = True

    labels = {
        'config_key': "Source",
        'bounce_recipient_address': "Bounced To",
        'intended_recipient_address': "Intended For",
    }

    grid_columns = [
        'config_key',
        'bounced',
        'bounce_recipient_address',
        'intended_recipient_address',
        'processed_by',
    ]

    def __init__(self, request):
        super().__init__(request)
        self.handler_options = sorted(get_profile_keys(self.rattail_config))

    def get_handler(self, bounce):
        app = self.get_rattail_app()
        return app.get_bounce_handler(bounce.config_key)

    def configure_grid(self, g):
        super().configure_grid(g)
        model = self.model

        g.filters['config_key'].set_choices(self.handler_options)
        g.filters['config_key'].default_active = True
        g.filters['config_key'].default_verb = 'equal'

        g.filters['processed'].default_active = True
        g.filters['processed'].default_verb = 'is_null'

        # processed_by
        g.set_joiner('processed_by', lambda q: q.outerjoin(model.User))
        g.set_sorter('processed_by', model.User.username)
        g.set_filter('processed_by', model.User.username)

        g.set_sort_defaults('bounced', 'desc')

        g.set_label('bounce_recipient_address', "Bounced To")
        g.set_label('intended_recipient_address', "Intended For")

        g.set_link('bounced')
        g.set_link('intended_recipient_address')

    def configure_form(self, f):
        super().configure_form(f)
        bounce = f.model_instance
        f.set_renderer('message', self.render_message_file)
        f.set_renderer('links', self.render_links)
        f.fields = [
            'config_key',
            'message',
            'bounced',
            'bounce_recipient_address',
            'intended_recipient_address',
            'links',
            'processed',
            'processed_by',
        ]
        if not bounce.processed:
            f.remove_field('processed')
            f.remove_field('processed_by')

    def render_links(self, bounce, field):
        handler = self.get_handler(bounce)
        value = list(handler.make_links(self.Session(), bounce.intended_recipient_address))
        if not value:
            return "n/a"

        links = []
        for link in value:
            label = HTML.literal("{}:&nbsp; ".format(link.type))
            anchor = tags.link_to(link.title, link.url, target='_blank')
            links.append(HTML.tag('li', label + anchor))

        return HTML.tag('ul', HTML.literal('').join(links))

    def render_message_file(self, bounce, field):
        handler = self.get_handler(bounce)
        path = handler.msgpath(bounce)
        if not path:
            return ""

        url = self.get_action_url('download', bounce)
        return self.render_file_field(path, url)

    def template_kwargs_view(self, **kwargs):
        bounce = kwargs['instance']
        kwargs['bounce'] = bounce
        handler = self.get_handler(bounce)
        kwargs['handler'] = handler
        path = handler.msgpath(bounce)
        if os.path.exists(path):
            with open(path, 'rb') as f:
                # TODO: how to determine encoding? (is utf_8 guaranteed?)
                kwargs['message'] = f.read().decode('utf_8')
        else:
            kwargs['message'] = "(file not found)"
        return kwargs

    def download_path(self, bounce, filename):
        handler = self.get_handler(bounce)
        return handler.msgpath(bounce)

    # TODO: should require POST here
    def process(self):
        """
        View for marking a bounce as processed.
        """
        bounce = self.get_instance()
        bounce.processed = datetime.datetime.utcnow()
        bounce.processed_by = self.request.user
        self.request.session.flash("Email bounce has been marked processed.")
        return self.redirect(self.get_action_url('view', bounce))

    # TODO: should require POST here
    def unprocess(self):
        """
        View for marking a bounce as *unprocessed*.
        """
        bounce = self.get_instance()
        bounce.processed = None
        bounce.processed_by = None
        self.request.session.flash("Email bounce has been marked UN-processed.")
        return self.redirect(self.get_action_url('view', bounce))

    @classmethod
    def defaults(cls, config):
        cls._bounce_defaults(config)
        cls._defaults(config)

    @classmethod
    def _bounce_defaults(cls, config):

        config.add_tailbone_permission_group('emailbounces', "Email Bounces", overwrite=False)

        # mark bounce as processed
        config.add_route('emailbounces.process', '/email-bounces/{uuid}/process')
        config.add_view(cls, attr='process', route_name='emailbounces.process',
                        permission='emailbounces.process')
        config.add_tailbone_permission('emailbounces', 'emailbounces.process',
                                       "Mark Email Bounce as processed")

        # mark bounce as *not* processed
        config.add_route('emailbounces.unprocess', '/email-bounces/{uuid}/unprocess')
        config.add_view(cls, attr='unprocess', route_name='emailbounces.unprocess',
                        permission='emailbounces.unprocess')
        config.add_tailbone_permission('emailbounces', 'emailbounces.unprocess',
                                       "Mark Email Bounce as UN-processed")


def defaults(config, **kwargs):
    base = globals()

    EmailBounceView = kwargs.get('EmailBounceView', base['EmailBounceView'])
    EmailBounceView.defaults(config)


def includeme(config):
    defaults(config)
