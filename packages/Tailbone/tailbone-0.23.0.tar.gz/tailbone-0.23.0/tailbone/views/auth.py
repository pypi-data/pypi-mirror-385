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
Auth Views
"""

import colander
from deform import widget as dfwidget
from pyramid.httpexceptions import HTTPForbidden
from webhelpers2.html import tags, literal

from tailbone import forms
from tailbone.db import Session
from tailbone.views import View
from tailbone.auth import login_user, logout_user
from tailbone.config import global_help_url


class UserLogin(colander.MappingSchema):

    username = colander.SchemaNode(colander.String())

    password = colander.SchemaNode(colander.String(),
                                   widget=dfwidget.PasswordWidget())


class AuthenticationView(View):

    def forbidden(self):
        """
        Access forbidden view.

        This is triggered whenever access is not allowed for an otherwise
        appropriate view.
        """
        next_url = self.request.get_referrer()
        msg = literal("You do not have permission to do that.")
        if not self.request.authenticated_userid:
            msg += literal("&nbsp; (Perhaps you should %s?)" %
                           tags.link_to("log in", self.request.route_url('login')))
            # Store current URL in session, for smarter redirect after login.
            self.request.session['next_url'] = self.request.current_route_url()
            next_url = self.request.route_url('login')
        self.request.session.flash(msg, 'warning', allow_duplicate=False)
        return self.redirect(next_url)

    def login(self, **kwargs):
        """
        The login view, responsible for displaying and handling the login form.
        """
        app = self.get_rattail_app()
        referrer = self.request.get_referrer(default=self.request.route_url('home'))

        # redirect if already logged in
        if self.request.user:
            self.request.session.flash("{} is already logged in".format(self.request.user), 'error')
            return self.redirect(referrer)

        form = forms.Form(schema=UserLogin(), request=self.request)
        form.save_label = "Login"
        form.show_reset = True
        form.show_cancel = False
        form.button_icon_submit = 'user'
        if form.validate():
            user = self.authenticate_user(form.validated['username'],
                                          form.validated['password'])
            if user:
                # okay now they're truly logged in
                headers = login_user(self.request, user)
                # treat URL from session as referrer, if available
                referrer = self.request.session.pop('next_url', referrer)
                return self.redirect(referrer, headers=headers)

            else:
                self.request.session.flash("Invalid username or password", 'error')

        # nb. hacky..but necessary, to add the refs, for autofocus
        # (also add key handler, so ENTER acts like TAB)
        dform = form.make_deform_form()
        dform['username'].widget.attributes = {
            'ref': 'username',
            'autocomplete': 'off',
        }
        dform['password'].widget.attributes = {'ref': 'password'}

        return {
            'form': form,
            'referrer': referrer,
            'index_title': app.get_node_title(),
            'help_url': global_help_url(self.rattail_config),
        }

    def authenticate_user(self, username, password):
        app = self.get_rattail_app()
        auth = app.get_auth_handler()
        return auth.authenticate_user(Session(), username, password)

    def logout(self, **kwargs):
        """
        View responsible for logging out the current user.

        This deletes/invalidates the current session and then redirects to the
        login page.
        """
        # truly logout the user
        headers = logout_user(self.request)

        # redirect to home page after login, if so configured
        if self.rattail_config.getbool('tailbone', 'home_after_logout', default=False):
            return self.redirect(self.request.route_url('home'), headers=headers)

        # otherwise redirect to referrer, with 'login' page as fallback
        referrer = self.request.get_referrer(default=self.request.route_url('login'))
        return self.redirect(referrer, headers=headers)

    def noop(self):
        """
        View to serve as "no-op" / ping action to reset current user's session timer
        """
        return {'status': 'ok'}

    def change_password(self):
        """
        Allows a user to change his or her password.
        """
        if not self.request.user:
            return self.redirect(self.request.route_url('home'))

        if ((self.request.user.prevent_password_change
             or self.user_is_protected(self.request.user))
            and not self.request.is_root):

            self.request.session.flash("Cannot change password for user: {}".format(
                self.request.user))
            return self.redirect(self.request.get_referrer())

        def check_user_password(node, value):
            auth = self.app.get_auth_handler()
            user = self.request.user
            if not auth.check_user_password(user, value):
                node.raise_invalid("The password is incorrect")

        schema = colander.Schema()

        schema.add(colander.SchemaNode(colander.String(),
                                       name='current_password',
                                       widget=dfwidget.PasswordWidget(),
                                       validator=check_user_password))

        schema.add(colander.SchemaNode(colander.String(),
                                       name='new_password',
                                       widget=dfwidget.CheckedPasswordWidget()))

        form = forms.Form(schema=schema, request=self.request)
        if form.validate():
            auth = self.app.get_auth_handler()
            auth.set_user_password(self.request.user, form.validated['new_password'])
            self.request.session.flash("Your password has been changed.")
            return self.redirect(self.request.get_referrer())

        return {'index_title': str(self.request.user),
                'form': form}

    def become_root(self):
        """
        Elevate the current request to 'root' for full system access.
        """
        if not self.request.is_admin:
            raise HTTPForbidden()
        self.request.user.record_event(self.enum.USER_EVENT_BECOME_ROOT)
        self.request.session['is_root'] = True
        self.request.session.flash("You have been elevated to 'root' and now have full system access")
        return self.redirect(self.request.get_referrer())

    def stop_root(self):
        """
        Lower the current request from 'root' back to normal access.
        """
        if not self.request.is_admin:
            raise HTTPForbidden()
        self.request.user.record_event(self.enum.USER_EVENT_STOP_ROOT)
        self.request.session['is_root'] = False
        self.request.session.flash("Your normal system access has been restored")
        return self.redirect(self.request.get_referrer())

    @classmethod
    def defaults(cls, config):
        rattail_config = config.registry.settings.get('rattail_config')

        # forbidden
        config.add_forbidden_view(cls, attr='forbidden')

        # login
        config.add_route('login', '/login')
        config.add_view(cls, attr='login', route_name='login', renderer='/login.mako')

        # logout
        config.add_route('logout', '/logout')
        config.add_view(cls, attr='logout', route_name='logout')

        # no-op
        config.add_route('noop', '/noop')
        config.add_view(cls, attr='noop', route_name='noop', renderer='json')

        # change password
        config.add_route('change_password', '/change-password')
        config.add_view(cls, attr='change_password', route_name='change_password', renderer='/change_password.mako')

        # become/stop root
        # TODO: these should require POST but i won't bother until
        # after butterball becomes default theme..or probably should
        # just refactor the falafel theme accordingly..?
        config.add_route('become_root', '/root/yes')
        config.add_view(cls, attr='become_root', route_name='become_root')
        config.add_route('stop_root', '/root/no')
        config.add_view(cls, attr='stop_root', route_name='stop_root')


def defaults(config, **kwargs):
    base = globals()

    AuthenticationView = kwargs.get('AuthenticationView', base['AuthenticationView'])
    AuthenticationView.defaults(config)


def includeme(config):
    defaults(config)
