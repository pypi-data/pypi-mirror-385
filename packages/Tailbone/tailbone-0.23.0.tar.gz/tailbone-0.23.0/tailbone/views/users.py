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
User Views
"""

import sqlalchemy as sa
from sqlalchemy import orm

from rattail.db.model import User, UserEvent

import colander
from deform import widget as dfwidget
from webhelpers2.html import HTML, tags

from tailbone import forms
from tailbone.views import MasterView, View
from tailbone.views.principal import PrincipalMasterView, PermissionsRenderer
from tailbone.util import raw_datetime


class UserView(PrincipalMasterView):
    """
    Master view for the User model.
    """
    model_class = User
    has_versions = True
    touchable = True
    mergeable = True

    labels = {
        'api_tokens': "API Tokens",
    }

    grid_columns = [
        'username',
        'person',
        'active',
        'local_only',
    ]

    form_fields = [
        'username',
        'person',
        'first_name_',
        'last_name_',
        'display_name_',
        'active',
        'active_sticky',
        'set_password',
        'prevent_password_change',
        'api_tokens',
        'roles',
        'permissions',
    ]

    has_rows = True
    model_row_class = UserEvent
    rows_title = "User Events"
    rows_viewable = False

    row_grid_columns = [
        'type_code',
        'occurred',
    ]

    def __init__(self, request):
        super().__init__(request)
        app = self.get_rattail_app()

        # always get a reference to the auth/merge handler
        self.auth_handler = app.get_auth_handler()
        self.merge_handler = self.auth_handler

    def get_context_menu_items(self, user=None):
        items = super().get_context_menu_items(user)

        if self.viewing:

            if self.has_perm('preferences'):
                url = self.get_action_url('preferences', user)
                items.append(tags.link_to("Edit User Preferences", url))

        return items

    def query(self, session):
        query = super().query(session)
        model = self.model

        # bring in the related Person(s)
        query = query.outerjoin(model.Person)\
                     .options(orm.joinedload(model.User.person))

        return query

    def configure_grid(self, g):
        super().configure_grid(g)
        model = self.model

        del g.filters['salt']
        g.filters['username'].default_active = True
        g.filters['username'].default_verb = 'contains'
        g.filters['active'].default_active = True
        g.filters['active'].default_verb = 'is_true'
        g.filters['person'] = g.make_filter('person', model.Person.display_name,
                                            default_active=True, default_verb='contains')

        # password
        g.set_filter('password', model.User.password,
                     verbs=['is_null', 'is_not_null'])

        g.set_sorter('person', model.Person.display_name)
        g.set_sorter('first_name', model.Person.first_name)
        g.set_sorter('last_name', model.Person.last_name)
        g.set_sorter('display_name', model.Person.display_name)
        g.set_sort_defaults('username')

        g.set_label('person', "Person's Name")

        g.set_link('username')
        g.set_link('person')
        g.set_link('first_name')
        g.set_link('last_name')
        g.set_link('display_name')

    def grid_extra_class(self, user, i):
        if not user.active:
            return 'warning'

    def editable_instance(self, user):
        """
        If the given user is "protected" then we only allow edit if current
        user is "root".  But if the given user is not protected, this simply
        returns ``True``.
        """
        if self.request.is_root:
            return True
        return not self.user_is_protected(user)

    def deletable_instance(self, user):
        """
        If the given user is "protected" then we only allow delete if current
        user is "root".  But if the given user is not protected, this simply
        returns ``True``.
        """
        if self.request.is_root:
            return True
        return not self.user_is_protected(user)

    def unique_username(self, node, value):
        model = self.model
        query = self.Session.query(model.User)\
                            .filter(model.User.username == value)
        if self.editing:
            user = self.get_instance()
            query = query.filter(model.User.uuid != user.uuid)
        if query.count():
            raise colander.Invalid(node, "Username must be unique")

    def valid_person(self, node, value):
        """
        Make sure ``value`` corresponds to an existing
        ``Person.uuid``.
        """
        if value:
            model = self.model
            person = self.Session.get(model.Person, value)
            if not person:
                raise colander.Invalid(node, "Person not found (you must *select* a record)")

    def configure_form(self, f):
        super().configure_form(f)
        model = self.model
        user = f.model_instance

        # username
        f.set_validator('username', self.unique_username)

        # person
        f.set_renderer('person', self.render_person)
        if self.creating or self.editing:
            if 'person' in f.fields:
                f.replace('person', 'person_uuid')
                f.set_node('person_uuid', colander.String(), missing=colander.null)
                person_display = ""
                if self.request.method == 'POST':
                    if self.request.POST.get('person_uuid'):
                        person = self.Session.get(model.Person, self.request.POST['person_uuid'])
                        if person:
                            person_display = str(person)
                elif self.editing:
                    person_display = str(user.person or '')
                try:
                    people_url = self.request.route_url('people.autocomplete')
                except KeyError:
                    pass        # TODO: wutta compat
                else:
                    f.set_widget('person_uuid', forms.widgets.JQueryAutocompleteWidget(
                        field_display=person_display, service_url=people_url))
                f.set_validator('person_uuid', self.valid_person)
                f.set_label('person_uuid', "Person")

        # person name(s)
        if self.editing:
            # must explicitly set default, for "custom" field names
            f.set_default('first_name_', user.first_name or "")
            f.set_default('last_name_', user.last_name or "")
            f.set_default('display_name_', user.display_name or "")
        elif not self.creating:
            # must provide custom renderer as well
            f.set_renderer('first_name_', self.render_person_name)
            f.set_renderer('last_name_', self.render_person_name)
            f.set_renderer('display_name_', self.render_person_name)

        # set_password
        if self.editing and user.prevent_password_change and not self.request.is_root:
            f.remove('set_password')
        else:
            f.set_widget('set_password', dfwidget.CheckedPasswordWidget())
        # if self.creating:
        #     f.set_required('password')

        # api_tokens
        if self.creating or self.editing or self.deleting:
            f.remove('api_tokens')
        elif self.has_perm('manage_api_tokens'):
            f.set_renderer('api_tokens', self.render_api_tokens)
            f.set_vuejs_component_kwargs(**{':apiTokens': 'apiTokens',
                                            '@api-new-token': 'apiNewToken',
                                            '@api-token-delete': 'apiTokenDelete'})
        else:
            f.remove('api_tokens')

        # roles
        f.set_renderer('roles', self.render_roles)
        if self.creating or self.editing:
            if not self.has_perm('edit_roles'):
                f.remove_field('roles')
            else:
                roles = self.get_possible_roles().all()
                role_values = [(s.uuid, str(s)) for s in roles]
                f.set_node('roles', colander.Set())
                size = len(roles)
                if size < 3:
                    size = 3
                elif size > 20:
                    size = 20
                f.set_widget('roles', dfwidget.SelectWidget(multiple=True,
                                                            size=size,
                                                            values=role_values))
                if self.editing:
                    f.set_default('roles', [r.uuid for r in user.roles])
        elif not self.has_perm('view_roles'):
            f.remove_field('roles')

        f.set_label('display_name', "Full Name")

        # # hm this should work according to MDN but doesn't seem to...
        # # https://developer.mozilla.org/en-US/docs/Web/Security/Securing_your_site/Turning_off_form_autocompletion
        # fs.username.attrs(autocomplete='new-password')
        # fs.password.attrs(autocomplete='new-password')
        # fs.confirm_password.attrs(autocomplete='new-password')

        if self.viewing:
            permissions = self.request.registry.settings.get('wutta_permissions', {})
            f.set_renderer('permissions', PermissionsRenderer(request=self.request,
                                                              permissions=permissions,
                                                              include_anonymous=True,
                                                              include_authenticated=True))
        else:
            f.remove('permissions')

        if self.viewing or self.deleting:
            f.remove('set_password')

    def render_api_tokens(self, user, field):
        route_prefix = self.get_route_prefix()
        permission_prefix = self.get_permission_prefix()

        factory = self.get_grid_factory()
        g = factory(
            self.request,
            key=f'{route_prefix}.api_tokens',
            data=[],
            columns=['description', 'created'],
            actions=[
                self.make_action('delete', icon='trash',
                                 click_handler="$emit('api-token-delete', props.row)")])

        button = self.make_button("New", is_primary=True,
                                  icon_left='plus',
                                  **{'@click': "$emit('api-new-token')"})

        table = HTML.literal(
            g.render_table_element(data_prop='apiTokens'))

        return HTML.tag('div', c=[button, table])

    def add_api_token(self):
        user = self.get_instance()
        data = self.request.json_body

        token = self.auth_handler.add_api_token(user, data['description'])
        self.Session.flush()

        return {'ok': True,
                'raw_token': token.token_string,
                'tokens': self.get_api_tokens(user)}

    def delete_api_token(self):
        model = self.model
        user = self.get_instance()
        data = self.request.json_body

        token = self.Session.get(model.UserAPIToken, data['uuid'])
        if not token:
            return {'error': "API token not found"}

        if token.user is not user:
            return {'error': "API token not found"}

        self.auth_handler.delete_api_token(token)
        self.Session.flush()

        return {'ok': True,
                'tokens': self.get_api_tokens(user)}

    def template_kwargs_view(self, **kwargs):
        kwargs = super().template_kwargs_view(**kwargs)
        user = kwargs['instance']

        kwargs['api_tokens_data'] = self.get_api_tokens(user)

        return kwargs

    def get_api_tokens(self, user):
        tokens = []
        for token in reversed(user.api_tokens):
            tokens.append({
                'uuid': token.uuid,
                'description': token.description,
                'created': raw_datetime(self.rattail_config, token.created),
            })
        return tokens

    def get_possible_roles(self):
        app = self.get_rattail_app()
        auth = app.get_auth_handler()
        model = app.model

        # some roles should never have users "belong" to them
        excluded = [
            auth.get_role_anonymous(self.Session()).uuid,
            auth.get_role_authenticated(self.Session()).uuid,
        ]

        # only allow "root" user to change true admin role membership
        if not self.request.is_root:
            excluded.append(auth.get_role_administrator(self.Session()).uuid)

        # basic list, minus exclusions so far
        roles = self.Session.query(model.Role)\
                            .filter(~model.Role.uuid.in_(excluded))

        # only allow "admin" user to change admin-ish role memberships
        if not self.request.is_admin:
            roles = roles.filter(sa.or_(
                model.Role.adminish == False,
                model.Role.adminish == None))

        return roles.order_by(model.Role.name)

    def objectify(self, form, data=None):
        app = self.get_rattail_app()
        auth = app.get_auth_handler()
        model = app.model

        # create/update user as per normal
        if data is None:
            data = form.validated
        user = super().objectify(form, data)

        # create/update person as needed
        names = {}
        if 'first_name_' in form and data['first_name_']:
            names['first'] = data['first_name_']
        if 'last_name_' in form and data['last_name_']:
            names['last'] = data['last_name_']
        if 'display_name_' in form and data['display_name_']:
            names['full'] = data['display_name_']
        # we will not have a person reference yet, when creating new user.  if
        # that is the case, go ahead and load it, if specified.
        if self.creating and user.person_uuid:
            self.Session.add(user)
            self.Session.flush()
        # note, do *not* create new person unless name(s) provided
        if not user.person and any([n for n in names.values()]):
            user.person = model.Person()
        if user.person:
            app = self.get_rattail_app()
            handler = app.get_people_handler()
            handler.update_names(user.person, **names)

        # force "local only" flag unless global access granted
        if self.secure_global_objects:
            if not self.has_perm('view_global'):
                user.person.local_only = True

        # maybe set user password
        if 'set_password' in form and data['set_password']:
            auth.set_user_password(user, data['set_password'])

        # update roles for user
        self.update_roles(user, data)

        return user

    def update_roles(self, user, data):
        if not self.has_perm('edit_roles'):
            return
        if 'roles' not in data:
            return

        app = self.get_rattail_app()
        auth = app.get_auth_handler()
        model = app.model
        old_roles = set([r.uuid for r in user.roles])
        new_roles = data['roles']
        admin = auth.get_role_administrator(self.Session())

        # add any new roles for the user, taking care not to add the admin role
        # unless acting as root
        for uuid in new_roles:
            if uuid not in old_roles:
                if self.request.is_root or uuid != admin.uuid:
                    user._roles.append(model.UserRole(role_uuid=uuid))

                    # also record a change to the role, for datasync.
                    # this is done "just in case" the role is to be
                    # synced to all nodes
                    if self.Session().rattail_record_changes:
                        self.Session.add(model.Change(class_name='Role',
                                                      instance_uuid=uuid,
                                                      deleted=False))

        # remove any roles which were *not* specified, although must take care
        # not to remove admin role, unless acting as root
        for uuid in old_roles:
            if uuid not in new_roles:
                if self.request.is_root or uuid != admin.uuid:
                    role = self.Session.get(model.Role, uuid)
                    user.roles.remove(role)

                    # also record a change to the role, for datasync.
                    # this is done "just in case" the role is to be
                    # synced to all nodes
                    if self.Session().rattail_record_changes:
                        self.Session.add(model.Change(class_name='Role',
                                                      instance_uuid=uuid,
                                                      deleted=False))

    def render_person(self, user, field):
        person = user.person
        if not person:
            return ""
        text = str(person)
        url = self.request.route_url('people.view', uuid=person.uuid)
        return tags.link_to(person, url)

    def render_person_name(self, user, field):
        if not field.endswith('_'):
            return ""
        name = getattr(user, field[:-1], None)
        if not name:
            return ""
        return str(name)

    def render_roles(self, user, field):
        roles = sorted(user.roles, key=lambda r: r.name)
        items = []
        for role in roles:
            text = role.name
            url = self.request.route_url('roles.view', uuid=role.uuid)
            items.append(HTML.tag('li', c=[tags.link_to(text, url)]))
        return HTML.tag('ul', c=items)

    def get_row_data(self, user):
        model = self.model
        return self.Session.query(model.UserEvent)\
                           .filter(model.UserEvent.user == user)

    def configure_row_grid(self, g):
        super().configure_row_grid(g)
        g.width = 'half'
        g.filterable = False
        g.set_sort_defaults('occurred', 'desc')
        g.set_enum('type_code', self.enum.USER_EVENT)
        g.set_label('type_code', "Event Type")

    def get_version_child_classes(self):
        model = self.model
        return [
            (model.UserRole, 'user_uuid'),
        ]

    def find_principals_with_permission(self, session, permission):
        app = self.get_rattail_app()
        auth = app.get_auth_handler()
        model = self.model

        # TODO: this should search Permission table instead, and work backward to User?
        all_users = session.query(model.User)\
                           .filter(model.User.active == True)\
                           .order_by(model.User.username)\
                           .options(orm.joinedload(model.User._roles)\
                                    .joinedload(model.UserRole.role)\
                                    .joinedload(model.Role._permissions))
        users = []
        for user in all_users:
            if auth.has_permission(session, user, permission):
                users.append(user)
        return users

    def find_by_perm_configure_results_grid(self, g):
        g.append('username')
        g.set_link('username')

        g.append('person')
        g.set_link('person')

    def find_by_perm_normalize(self, user):
        data = super().find_by_perm_normalize(user)

        data['username'] = user.username
        data['person'] = str(user.person or '')

        return data

    def preferences(self, user=None):
        """
        View to modify preferences for a particular user.
        """
        current_user = True
        if not user:
            current_user = False
            user = self.get_instance()

        # TODO: this is of course largely copy/pasted from the
        # MasterView.configure() method..should refactor?
        if self.request.method == 'POST':
            if self.request.POST.get('remove_settings'):
                self.preferences_remove_settings(user)
                self.request.session.flash("Settings have been removed.")
                return self.redirect(self.request.current_route_url())
            else:
                data = self.request.POST

                # then gather/save settings
                settings = self.preferences_gather_settings(data, user)
                self.preferences_remove_settings(user)
                self.configure_save_settings(settings)
                self.request.session.flash("Settings have been saved.")
                return self.redirect(self.request.current_route_url())

        context = self.preferences_get_context(user, current_user)
        return self.render_to_response('preferences', context)

    def my_preferences(self):
        """
        View to modify preferences for the current user.
        """
        user = self.request.user
        if not user:
            raise self.forbidden()
        return self.preferences(user=user)

    def preferences_get_context(self, user, current_user):
        simple_settings = self.preferences_get_simple_settings(user)
        context = self.configure_get_context(simple_settings=simple_settings,
                                             input_file_templates=False)

        instance_title = self.get_instance_title(user)
        context.update({
            'user': user,
            'instance': user,
            'instance_title': instance_title,
            'instance_url': self.get_action_url('view', user),
            'config_title': instance_title,
            'config_preferences': True,
            'current_user': current_user,
        })

        if current_user:
            context.update({
                'index_url': None,
                'index_title': instance_title,
            })

        # theme style options
        options = [{'value': None, 'label': "default"}]
        styles = self.rattail_config.getlist('tailbone', 'themes.styles',
                                             default=[])
        for name in styles:
            css = None
            if self.request.use_oruga:
                css = self.rattail_config.get(f'tailbone.themes.bb_style.{name}')
            if not css:
                css = self.rattail_config.get(f'tailbone.themes.style.{name}')
            if css:
                options.append({'value': css, 'label': name})
        context['theme_style_options'] = options

        return context

    def preferences_get_simple_settings(self, user):
        """
        This method is conceptually the same as for
        :meth:`~tailbone.views.master.MasterView.configure_get_simple_settings()`.
        See its docs for more info.

        The only difference here is that we are given a user account,
        so the settings involved should only pertain to that user.
        """
        # TODO: can stop pre-fetching this value only once we are
        # confident all settings have been updated in the wild
        user_css = self.rattail_config.get(f'tailbone.{user.uuid}', 'user_css')
        if not user_css:
            user_css = self.rattail_config.get(f'tailbone.{user.uuid}', 'buefy_css')

        return [

            # display
            {'section': f'tailbone.{user.uuid}',
             'option': 'user_css',
             'value': user_css,
             'save_if_empty': False},
        ]

    def preferences_gather_settings(self, data, user):
        simple_settings = self.preferences_get_simple_settings(user)
        settings = self.configure_gather_settings(
            data, simple_settings=simple_settings, input_file_templates=False)

        # TODO: ugh why does user_css come back as 'default' instead of None?
        final_settings = []
        for setting in settings:
            if setting['name'].endswith('.user_css'):
                if setting['value'] == 'default':
                    continue
            final_settings.append(setting)

        return final_settings

    def preferences_remove_settings(self, user):
        app = self.get_rattail_app()
        simple_settings = self.preferences_get_simple_settings(user)
        self.configure_remove_settings(simple_settings=simple_settings,
                                       input_file_templates=False)
        app.delete_setting(self.Session(), f'tailbone.{user.uuid}.buefy_css')

    @classmethod
    def defaults(cls, config):
        cls._user_defaults(config)
        cls._principal_defaults(config)
        cls._defaults(config)

    @classmethod
    def _user_defaults(cls, config):
        """
        Provide extra default configuration for the User master view.
        """
        route_prefix = cls.get_route_prefix()
        permission_prefix = cls.get_permission_prefix()
        instance_url_prefix = cls.get_instance_url_prefix()
        model_title = cls.get_model_title()

        # view/edit roles
        config.add_tailbone_permission(permission_prefix, '{}.view_roles'.format(permission_prefix),
                                       "View the Roles to which a {} belongs".format(model_title))
        config.add_tailbone_permission(permission_prefix, '{}.edit_roles'.format(permission_prefix),
                                       "Edit the Roles to which a {} belongs".format(model_title))

        # manage API tokens
        config.add_tailbone_permission(permission_prefix,
                                       '{}.manage_api_tokens'.format(permission_prefix),
                                       "Manage API tokens for any {}".format(model_title))
        config.add_route('{}.add_api_token'.format(route_prefix),
                         '{}/add-api-token'.format(instance_url_prefix),
                         request_method='POST')
        config.add_view(cls, attr='add_api_token',
                        route_name='{}.add_api_token'.format(route_prefix),
                        permission='{}.manage_api_tokens'.format(permission_prefix),
                        renderer='json')
        config.add_route('{}.delete_api_token'.format(route_prefix),
                         '{}/delete-api-token'.format(instance_url_prefix),
                         request_method='POST')
        config.add_view(cls, attr='delete_api_token',
                        route_name='{}.delete_api_token'.format(route_prefix),
                        permission='{}.manage_api_tokens'.format(permission_prefix),
                        renderer='json')

        # edit preferences for any user
        config.add_tailbone_permission(permission_prefix,
                                       '{}.preferences'.format(permission_prefix),
                                       "Edit preferences for any {}".format(model_title))
        config.add_route('{}.preferences'.format(route_prefix),
                         '{}/preferences'.format(instance_url_prefix))
        config.add_view(cls, attr='preferences',
                        route_name='{}.preferences'.format(route_prefix),
                        permission='{}.preferences'.format(permission_prefix))

        # edit "my" preferences (for current user)
        config.add_route('my.preferences',
                         '/my/preferences')
        config.add_view(cls, attr='my_preferences',
                        route_name='my.preferences')


# TODO: deprecate / remove this
UsersView = UserView


class UserEventView(MasterView):
    """
    Master view for all user events
    """
    model_class = UserEvent
    url_prefix = '/user-events'
    viewable = False
    creatable = False
    editable = False
    deletable = False

    grid_columns = [
        'user',
        'person',
        'type_code',
        'occurred',
    ]

    def get_data(self, session=None):
        query = super().get_data(session=session)
        model = self.model
        return query.join(model.User)

    def configure_grid(self, g):
        super().configure_grid(g)
        model = self.model
        g.set_joiner('person', lambda q: q.outerjoin(model.Person))
        g.set_sorter('user', model.User.username)
        g.set_sorter('person', model.Person.display_name)
        g.filters['user'] = g.make_filter('user', model.User.username)
        g.filters['person'] = g.make_filter('person', model.Person.display_name)
        g.set_enum('type_code', self.enum.USER_EVENT)
        g.set_type('occurred', 'datetime')
        g.set_renderer('user', self.render_user)
        g.set_renderer('person', self.render_person)
        g.set_sort_defaults('occurred', 'desc')
        g.set_label('user', "Username")
        g.set_label('type_code', "Event Type")

    def render_user(self, event, column):
        return event.user.username

    def render_person(self, event, column):
        if event.user.person:
            return event.user.person.display_name

# TODO: deprecate / remove this
UserEventsView = UserEventView


def defaults(config, **kwargs):
    base = globals()

    UserView = kwargs.get('UserView', base['UserView'])
    UserView.defaults(config)

    UserEventView = kwargs.get('UserEventView', base['UserEventView'])
    UserEventView.defaults(config)


def includeme(config):
    wutta_config = config.registry.settings['wutta_config']
    if wutta_config.get_bool('tailbone.use_wutta_views', default=False, usedb=False):
        config.include('tailbone.views.wutta.users')
    else:
        defaults(config)
