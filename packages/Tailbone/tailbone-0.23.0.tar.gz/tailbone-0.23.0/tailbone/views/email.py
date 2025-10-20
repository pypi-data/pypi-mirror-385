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
Email Views
"""

import logging
import re
import warnings

from wuttjamaican.util import parse_list

from rattail.db.model import EmailAttempt
from rattail.util import simple_error

import colander
from deform import widget as dfwidget

from tailbone import grids
from tailbone.db import Session
from tailbone.views import View, MasterView


log = logging.getLogger(__name__)


class EmailSettingView(MasterView):
    """
    Master view for email admin (settings/preview).
    """
    normalized_model_name = 'emailprofile'
    model_title = "Email Setting"
    model_key = 'key'
    url_prefix = '/settings/email'
    filterable = False
    pageable = False
    creatable = False
    deletable = False
    configurable = True
    config_title = "Email"

    grid_columns = [
        'key',
        'prefix',
        'subject',
        'to',
        'enabled',
        'hidden',
    ]

    form_fields = [
        'key',
        'fallback_key',
        'description',
        'prefix',
        'subject',
        'sender',
        'replyto',
        'to',
        'cc',
        'bcc',
        'enabled',
        'hidden',
    ]

    def __init__(self, request):
        super().__init__(request)
        self.email_handler = self.get_handler()

    @property
    def handler(self):
        warnings.warn("the `handler` property is deprecated!  "
                      "please use `email_handler` instead",
                      DeprecationWarning, stacklevel=2)
        return self.email_handler

    def get_handler(self):
        app = self.get_rattail_app()
        return app.get_email_handler()

    def get_data(self, session=None):
        data = []
        if self.has_perm('configure'):
            emails = self.email_handler.get_all_emails()
        else:
            emails = self.email_handler.get_available_emails()
        for key, Email in emails.items():
            email = Email(self.rattail_config, key)
            try:
                normalized = self.normalize(email)
            except:
                log.warning("cannot normalize email: %s", email,
                            exc_info=True)
            else:
                data.append(normalized)
        return data

    def configure_grid(self, g):
        super().configure_grid(g)

        g.sort_on_backend = False
        g.sort_multiple = False
        g.set_sort_defaults('key')

        g.set_type('enabled', 'boolean')
        g.set_link('key')
        g.set_link('subject')

        g.set_searchable('key')
        g.set_searchable('subject')

        # to
        g.set_renderer('to', self.render_to_short)

        # hidden
        if self.has_perm('configure'):
            g.set_type('hidden', 'boolean')
        else:
            g.remove('hidden')

        # toggle hidden
        if self.has_perm('configure'):
            g.actions.append(
                self.make_action('toggle_hidden', url='#', icon='ban',
                                 click_handler='toggleHidden(props.row)',
                                 factory=ToggleHidden))

    def render_to_short(self, email, column):
        profile = email['_email']
        if self.rattail_config.production():
            if profile.dynamic_to:
                if profile.dynamic_to_help:
                    return profile.dynamic_to_help

        value = email['to']
        if not value:
            return ""
        recips = parse_list(value)
        if len(recips) < 3:
            return value
        return "{}, ...".format(', '.join(recips[:2]))

    def normalize(self, email):
        def get_recips(type_):
            recips = email.get_recips(type_)
            if recips:
                return ', '.join(recips)
        data = email.obtain_sample_data(self.request)
        normal = {
            '_email': email,
            'key': email.key,
            'fallback_key': email.fallback_key,
            'description': email.__doc__,
            'prefix': email.get_prefix(data, magic=False) or '',
            'subject': email.get_subject(data, render=False) or '',
            'sender': email.get_sender() or '',
            'replyto': email.get_replyto() or '',
            'to': get_recips('to') or '',
            'cc': get_recips('cc') or '',
            'bcc': get_recips('bcc') or '',
            'enabled': email.get_enabled(),
        }
        if self.has_perm('configure'):
            normal['hidden'] = self.email_handler.email_is_hidden(email.key)
        return normal

    def get_instance(self):
        key = self.request.matchdict['key']
        return self.normalize(self.email_handler.get_email(key))

    def get_instance_title(self, email):
        return email['_email'].get_complete_subject(render=False)

    def editable_instance(self, profile):
        if self.rattail_config.demo():
            return profile['key'] != 'user_feedback'
        return True

    def deletable_instance(self, profile):
        if self.rattail_config.demo():
            return profile['key'] != 'user_feedback'
        return True

    def configure_form(self, f):
        super().configure_form(f)
        profile = f.model_instance['_email']

        # key
        f.set_readonly('key')

        # fallback_key
        f.set_readonly('fallback_key')

        # description
        f.set_readonly('description')

        # prefix
        f.set_label('prefix', "Subject Prefix")

        # subject
        f.set_label('subject', "Subject Text")

        # sender
        f.set_label('sender', "From")

        # replyto
        f.set_label('replyto', "Reply-To")

        # to
        f.set_widget('to', dfwidget.TextAreaWidget(cols=60, rows=6))
        if self.rattail_config.production():
            if profile.dynamic_to:
                f.set_readonly('to')
                if profile.dynamic_to_help:
                    f.model_instance['to'] = profile.dynamic_to_help

        # cc
        f.set_widget('cc', dfwidget.TextAreaWidget(cols=60, rows=2))

        # bcc
        f.set_widget('bcc', dfwidget.TextAreaWidget(cols=60, rows=2))

        # enabled
        f.set_type('enabled', 'boolean')

        # hidden
        if self.has_perm('configure'):
            f.set_type('hidden', 'boolean')
        else:
            f.remove('hidden')

    def make_form_schema(self):
        schema = EmailProfileSchema()

        if not self.has_perm('configure'):
            hidden = schema.get('hidden')
            schema.children.remove(hidden)

        return schema

    def save_edit_form(self, form):
        key = self.request.matchdict['key']
        data = self.form_deserialized
        app = self.get_rattail_app()
        session = self.Session()
        app.save_setting(session, 'rattail.mail.{}.prefix'.format(key), data['prefix'])
        app.save_setting(session, 'rattail.mail.{}.subject'.format(key), data['subject'])
        app.save_setting(session, 'rattail.mail.{}.from'.format(key), data['sender'])
        app.save_setting(session, 'rattail.mail.{}.replyto'.format(key), data['replyto'])
        app.save_setting(session, 'rattail.mail.{}.to'.format(key), (data['to'] or '').replace('\n', ', '))
        app.save_setting(session, 'rattail.mail.{}.cc'.format(key), (data['cc'] or '').replace('\n', ', '))
        app.save_setting(session, 'rattail.mail.{}.bcc'.format(key), (data['bcc'] or '').replace('\n', ', '))
        app.save_setting(session, 'rattail.mail.{}.enabled'.format(key), str(data['enabled']).lower())
        if self.has_perm('configure'):
            app.save_setting(session, 'rattail.mail.{}.hidden'.format(key), str(data['hidden']).lower())
        return data

    def template_kwargs_view(self, **kwargs):
        kwargs = super().template_kwargs_view(**kwargs)
        app = self.get_rattail_app()

        key = self.request.matchdict['key']
        kwargs['email'] = self.email_handler.get_email(key)

        kwargs['user_email_address'] = app.get_contact_email_address(self.request.user)

        return kwargs

    def configure_get_simple_settings(self):
        config = self.rattail_config
        return [

            # general
            {'section': 'rattail.mail',
             'option': 'handler'},
            {'section': 'rattail.mail',
             'option': 'templates'},

            # sending
            {'section': 'rattail.mail',
             'option': 'record_attempts',
             'type': bool},
            {'section': 'rattail.mail',
             'option': 'send_email_on_failure',
             'type': bool},
        ]

    def configure_get_context(self, *args, **kwargs):
        context = super().configure_get_context(*args, **kwargs)
        app = self.get_rattail_app()

        # prettify list of template paths
        templates = self.rattail_config.parse_list(
            context['simple_settings']['rattail.mail.templates'])
        context['simple_settings']['rattail.mail.templates'] = ', '.join(templates)

        context['user_email_address'] = app.get_contact_email_address(self.request.user)

        return context

    def toggle_hidden(self):
        app = self.get_rattail_app()
        data = self.request.json_body
        name = 'rattail.mail.{}.hidden'.format(data['key'])
        app.save_setting(self.Session(), name,
                         'true' if data['hidden'] else 'false')
        return {'ok': True}

    def send_test(self):
        """
        AJAX view for sending a test email.
        """
        data = self.request.json_body

        recip = data.get('recipient')
        if not recip:
            return {'error': "Must specify recipient"}

        app = self.get_rattail_app()
        app.send_email('hello', to=[recip], cc=None, bcc=None,
                       default_subject="Hello world")

        return {'ok': True}

    @classmethod
    def defaults(cls, config):
        cls._email_defaults(config)
        cls._defaults(config)

    @classmethod
    def _email_defaults(cls, config):
        route_prefix = cls.get_route_prefix()
        url_prefix = cls.get_url_prefix()
        permission_prefix = cls.get_permission_prefix()
        model_title_plural = cls.get_model_title_plural()

        # toggle hidden
        config.add_route('{}.toggle_hidden'.format(route_prefix),
                         '{}/toggle-hidden'.format(url_prefix),
                         request_method='POST')
        config.add_view(cls, attr='toggle_hidden',
                        route_name='{}.toggle_hidden'.format(route_prefix),
                        permission='{}.configure'.format(permission_prefix),
                        renderer='json')

        # send test
        config.add_route('{}.send_test'.format(route_prefix),
                         '{}/send-test'.format(url_prefix),
                         request_method='POST')
        config.add_view(cls, attr='send_test',
                        route_name='{}.send_test'.format(route_prefix),
                        permission='{}.configure'.format(permission_prefix),
                        renderer='json')


# TODO: deprecate / remove this
ProfilesView = EmailSettingView


class ToggleHidden(grids.GridAction):
    """
    Grid action for toggling the 'hidden' flag for an email profile.
    """

    def render_label(self):
        return '{{ renderLabelToggleHidden(props.row) }}'


class RecipientsType(colander.String):
    """
    Custom schema type for email recipients.  This is used to present the
    recipients as a "list" within the text area, i.e. one recipient per line.
    Then the list is collapsed to a comma-delimited string for storage.
    """

    def serialize(self, node, appstruct):
        if appstruct is colander.null:
            return colander.null
        recips = parse_list(appstruct)
        return '\n'.join(recips)

    def deserialize(self, node, cstruct):
        if cstruct == '' and self.allow_empty:
            return ''
        if not cstruct:
            return colander.null
        recips = parse_list(cstruct)
        return ', '.join(recips)


class EmailProfileSchema(colander.MappingSchema):

    prefix = colander.SchemaNode(colander.String())

    subject = colander.SchemaNode(colander.String())

    sender = colander.SchemaNode(colander.String())

    replyto = colander.SchemaNode(colander.String(), missing='')

    to = colander.SchemaNode(RecipientsType())

    cc = colander.SchemaNode(RecipientsType(), missing='')

    bcc = colander.SchemaNode(RecipientsType(), missing='')

    enabled = colander.SchemaNode(colander.Boolean())

    hidden = colander.SchemaNode(colander.Boolean())


class EmailPreview(View):
    """
    Lists available email templates, and can show previews of each.
    """

    def __init__(self, request):
        super().__init__(request)

        if hasattr(self, 'get_handler'):
            warnings.warn("defining a get_handler() method is deprecated; "
                          "please use AppHandler.get_email_handler() instead",
                          DeprecationWarning, stacklevel=2)
            self.email_handler = get_handler()
        else:
            app = self.get_rattail_app()
            self.email_handler = app.get_email_handler()

    @property
    def handler(self):
        warnings.warn("the `handler` property is deprecated!  "
                      "please use `email_handler` instead",
                      DeprecationWarning, stacklevel=2)
        return self.email_handler

    def __call__(self):

        # Forms submitted via POST are only used for sending emails.
        if self.request.method == 'POST':
            self.email_template()
            url = self.request.get_referrer(default=self.request.route_url('emailprofiles'))
            return self.redirect(url)

        # Maybe render a preview?
        key = self.request.GET.get('key')
        if key:
            type_ = self.request.GET.get('type', 'html')
            return self.preview_template(key, type_)

        assert False, "should not be here"

    def email_template(self):
        recipient = self.request.POST.get('recipient')
        if recipient:
            key = self.request.POST.get('email_key')
            if key:
                email = self.email_handler.get_email(key)

                context = self.email_handler.make_context()
                context.update(email.obtain_sample_data(self.request))

                try:
                    self.email_handler.send_message(email, context,
                                                    subject_prefix="[PREVIEW] ",
                                                    to=[recipient],
                                                    cc=None, bcc=None)
                except Exception as error:
                    self.request.session.flash(simple_error(error), 'error')
                else:
                    self.request.session.flash(
                        "Preview for '{}' was emailed to {}".format(
                            key, recipient))

    def preview_template(self, key, type_):
        email = self.email_handler.get_email(key)
        template = email.get_template(type_)

        context = self.email_handler.make_context()
        context.update(email.obtain_sample_data(self.request))

        self.request.response.text = template.render(**context)
        if type_ == 'txt':
            self.request.response.content_type = str('text/plain')
        return self.request.response

    @classmethod
    def defaults(cls, config):
        # email preview
        config.add_route('email.preview', '/email/preview/')
        config.add_view(cls, route_name='email.preview',
                        renderer='/email/preview.mako',
                        permission='emailprofiles.preview')
        config.add_tailbone_permission('emailprofiles', 'emailprofiles.preview',
                                       "Send preview email")


class EmailAttemptView(MasterView):
    """
    Master view for email attempts.
    """
    model_class = EmailAttempt
    route_prefix = 'email_attempts'
    url_prefix = '/email/attempts'
    creatable = False
    editable = False
    deletable = False

    labels = {
        'status_code': "Status",
    }

    grid_columns = [
        'key',
        'sender',
        'subject',
        'to',
        'sent',
        'status_code',
    ]

    form_fields = [
        'key',
        'sender',
        'subject',
        'to',
        'cc',
        'bcc',
        'sent',
        'status_code',
        'status_text',
    ]

    def configure_grid(self, g):
        super().configure_grid(g)

        # sent
        g.set_sort_defaults('sent', 'desc')

        # status_code
        g.set_enum('status_code', self.enum.EMAIL_ATTEMPT)

        # to
        g.set_renderer('to', self.render_to_short)

        # links
        g.set_link('key')
        g.set_link('sender')
        g.set_link('subject')
        g.set_link('to')

    to_pattern = re.compile(r'^\{(.*)\}$')

    def render_to_short(self, attempt, column):
        value = attempt.to
        if not value:
            return

        match = self.to_pattern.match(value)
        if match:
            recips = parse_list(match.group(1))
            if len(recips) > 2:
                recips = recips[:2]
                recips.append('...')
            return ', '.join(recips)

        return value

    def configure_form(self, f):
        super().configure_form(f)

        # key
        f.set_renderer('key', self.render_email_key)

        # status_code
        f.set_enum('status_code', self.enum.EMAIL_ATTEMPT)


def defaults(config, **kwargs):
    base = globals()

    EmailSettingView = kwargs.get('EmailSettingView', base['EmailSettingView'])
    EmailSettingView.defaults(config)

    EmailPreview = kwargs.get('EmailPreview', base['EmailPreview'])
    EmailPreview.defaults(config)

    EmailAttemptView = kwargs.get('EmailAttemptView', base['EmailAttemptView'])
    EmailAttemptView.defaults(config)


def includeme(config):
    defaults(config)
