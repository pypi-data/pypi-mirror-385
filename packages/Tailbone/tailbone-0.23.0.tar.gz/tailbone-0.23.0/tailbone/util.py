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
Utilities
"""

import datetime
import importlib
import logging
import warnings

import humanize
import markdown

from rattail.files import resource_path

import colander
from pyramid.renderers import get_renderer
from pyramid.interfaces import IRoutesMapper
from webhelpers2.html import HTML, tags

from wuttaweb.util import (get_form_data as wutta_get_form_data,
                           get_libver as wutta_get_libver,
                           get_liburl as wutta_get_liburl,
                           get_csrf_token as wutta_get_csrf_token,
                           render_csrf_token)


log = logging.getLogger(__name__)


class SortColumn(object):
    """
    Generic representation of a sort column, for use with sorting grid
    data as well as with API.
    """

    def __init__(self, field_name, model_name=None):
        self.field_name = field_name
        self.model_name = model_name


def get_csrf_token(request):
    """ """
    warnings.warn("tailbone.util.get_csrf_token() is deprecated; "
                  "please use wuttaweb.util.get_csrf_token() instead",
                  DeprecationWarning, stacklevel=2)
    return wutta_get_csrf_token(request)


def csrf_token(request, name='_csrf'):
    """ """
    warnings.warn("tailbone.util.csrf_token() is deprecated; "
                  "please use wuttaweb.util.render_csrf_token() instead",
                  DeprecationWarning, stacklevel=2)
    return render_csrf_token(request, name=name)


def get_form_data(request):
    """
    DEPECATED - use :func:`wuttaweb:wuttaweb.util.get_form_data()`
    instead.
    """
    warnings.warn("tailbone.util.get_form_data() is deprecated; "
                  "please use wuttaweb.util.get_form_data() instead",
                  DeprecationWarning, stacklevel=2)
    return wutta_get_form_data(request)


def get_global_search_options(request):
    """
    Returns global search options for current request.  Basically a
    list of all "index views" minus the ones they aren't allowed to
    access.
    """
    options = []
    pages = sorted(request.registry.settings['tailbone_index_pages'],
                   key=lambda page: page['label'])
    for page in pages:
        if not page['permission'] or request.has_perm(page['permission']):
            option = dict(page)
            option['url'] = request.route_url(page['route'])
            options.append(option)
    return options


def get_libver(request, key, fallback=True, default_only=False): # pragma: no cover
    """
    DEPRECATED - use :func:`wuttaweb:wuttaweb.util.get_libver()`
    instead.
    """
    warnings.warn("tailbone.util.get_libver() is deprecated; "
                  "please use wuttaweb.util.get_libver() instead",
                  DeprecationWarning, stacklevel=2)

    return wutta_get_libver(request, key, prefix='tailbone',
                            configured_only=not fallback,
                            default_only=default_only)


def get_liburl(request, key, fallback=True): # pragma: no cover
    """
    DEPRECATED - use :func:`wuttaweb:wuttaweb.util.get_liburl()`
    instead.
    """
    warnings.warn("tailbone.util.get_liburl() is deprecated; "
                  "please use wuttaweb.util.get_liburl() instead",
                  DeprecationWarning, stacklevel=2)

    return wutta_get_liburl(request, key, prefix='tailbone',
                            configured_only=not fallback,
                            default_only=False)


def pretty_datetime(config, value):
    """
    Formats a datetime as a "pretty" human-readable string, with a tooltip
    showing the ISO string value.

    :param config: Reference to a config object.

    :param value: A ``datetime.datetime`` instance.  Note that if this instance
       is not timezone-aware, its timezone is assumed to be UTC.
    """
    if not value:
        return ''

    app = config.get_app()

    # Make sure we're dealing with a tz-aware value.  If we're given a naive
    # value, we assume it to be local to the UTC timezone.
    if not value.tzinfo:
        value = app.make_utc(value, tzinfo=True)

    # Calculate time diff using UTC.
    time_ago = datetime.datetime.utcnow() - app.make_utc(value)

    # Convert value to local timezone.
    local = app.get_timezone()
    value = local.normalize(value.astimezone(local))

    return HTML.tag('span',
                    title=value.strftime('%Y-%m-%d %H:%M:%S %Z%z'),
                    c=humanize.naturaltime(time_ago))


def raw_datetime(config, value, verbose=False, as_date=False):
    """
    Formats a datetime as a "raw" human-readable string, with a tooltip
    showing the more human-friendly "time since" equivalent.

    :param config: Reference to a config object.

    :param value: A ``datetime.datetime`` instance.  Note that if this instance
       is not timezone-aware, its timezone is assumed to be UTC.
    """
    if not value:
        return ''

    app = config.get_app()

    # Make sure we're dealing with a tz-aware value.  If we're given a naive
    # value, we assume it to be local to the UTC timezone.
    if not value.tzinfo:
        value = app.make_utc(value, tzinfo=True)

    # Calculate time diff using UTC.
    time_ago = datetime.datetime.utcnow() - app.make_utc(value)

    # Convert value to local timezone.
    local = app.get_timezone()
    value = local.normalize(value.astimezone(local))

    kwargs = {}

    # Avoid strftime error when year falls before epoch.
    if value.year >= 1900:
        if as_date:
            kwargs['c'] = value.strftime('%Y-%m-%d')
        else:
            kwargs['c'] = value.strftime('%Y-%m-%d %I:%M:%S %p')
    else:
        kwargs['c'] = str(value)

    time_diff = app.render_time_ago(time_ago, fallback=None)
    if time_diff is not None:

        # by "verbose" we mean the result text to look like "YYYY-MM-DD (X days ago)"
        if verbose:
            kwargs['c'] = "{} ({})".format(kwargs['c'], time_diff)

        # vs. if *not* verbose, text is "YYYY-MM-DD" but we add "X days ago" as title
        else:
            kwargs['title'] = time_diff

    return HTML.tag('span', **kwargs)


def render_markdown(text, raw=False, **kwargs):
    """
    Render the given markdown text as HTML.
    """
    kwargs.setdefault('extensions', ['fenced_code', 'codehilite'])
    md = markdown.markdown(text, **kwargs)
    if raw:
        return md
    md = HTML.literal(md)
    return HTML.tag('div', class_='rendered-markdown', c=[md])


def set_app_theme(request, theme, session=None):
    """
    Set the app theme.  This modifies the *global* Mako template lookup
    directory path, i.e. theme for all users will change immediately.

    This also saves the setting for the new theme, and updates the running app
    registry settings with the new theme.
    """
    theme = get_effective_theme(request.rattail_config, theme=theme, session=session)
    theme_path = get_theme_template_path(request.rattail_config, theme=theme, session=session)

    # there's only one global template lookup; can get to it via any renderer
    # but should *not* use /base.mako since that one is about to get volatile
    renderer = get_renderer('/menu.mako')
    lookup = renderer.lookup

    # overwrite first entry in lookup's directory list
    lookup.directories[0] = theme_path

    # clear template cache for lookup object, so it will reload each (as needed)
    lookup._collection.clear()

    app = request.rattail_config.get_app()
    close = False
    if not session:
        session = app.make_session()
        close = True
    app.save_setting(session, 'tailbone.theme', theme)
    if close:
        session.commit()
        session.close()

    request.registry.settings['tailbone.theme'] = theme


def get_theme_template_path(rattail_config, theme=None, session=None):
    """
    Retrieves the template path for the given theme.
    """
    theme = get_effective_theme(rattail_config, theme=theme, session=session)
    theme_path = rattail_config.get('tailbone', 'theme.{}'.format(theme),
                                    default='tailbone:templates/themes/{}'.format(theme))
    return resource_path(theme_path)


def get_available_themes(rattail_config, include=None):
    """
    Returns a list of theme names which are available.  If config does
    not specify, some defaults will be assumed.
    """
    # get available list from config, if it has one
    available = rattail_config.getlist('tailbone', 'themes.keys')
    if not available:
        available = rattail_config.getlist('tailbone', 'themes',
                                           ignore_ambiguous=True)
        if available:
            warnings.warn("URGENT: instead of 'tailbone.themes', "
                          "you should set 'tailbone.themes.keys'",
                          DeprecationWarning, stacklevel=2)
        else:
            available = []

    # include any themes specified by caller
    if include is not None:
        for theme in include:
            if theme not in available:
                available.append(theme)

    # sort the list by name
    available.sort()

    # make default theme the first option
    if 'default' in available:
        i = available.index('default')
        available.pop(i)
    available.insert(0, 'default')

    return available


def get_effective_theme(rattail_config, theme=None, session=None):
    """
    Validates and returns the "effective" theme.  If you provide a theme, that
    will be used; otherwise it is read from database setting.
    """
    app = rattail_config.get_app()

    if not theme:
        close = False
        if not session:
            session = app.make_session()
            close = True
        theme = app.get_setting(session, 'tailbone.theme') or 'default'
        if close:
            session.close()

    # confirm requested theme is available
    available = get_available_themes(rattail_config)
    if theme not in available:
        raise ValueError("theme not available: {}".format(theme))

    return theme


def should_use_oruga(request):
    """
    Returns a flag indicating whether or not the current theme
    supports (and therefore should use) Oruga + Vue 3 as opposed to
    the default of Buefy + Vue 2.
    """
    theme = request.registry.settings.get('tailbone.theme')
    if theme and 'butterball' in theme:
        return True
    return False


def validate_email_address(address):
    """
    Perform basic validation on the given email address.  This leverages the
    ``colander`` package for actual validation logic.
    """
    node = colander.SchemaNode(typ=colander.String)
    validator = colander.Email()
    validator(node, address)
    return address


def email_address_is_valid(address):
    """
    Returns boolean indicating whether the address can validate.
    """
    try:
        validate_email_address(address)
    except colander.Invalid:
        return False
    return True


def route_exists(request, route_name):
    """
    Checks for existence of the given route name, within the running app
    config.  Returns boolean indicating whether it exists.
    """
    reg = request.registry
    mapper = reg.getUtility(IRoutesMapper)
    route = mapper.get_route(route_name)
    return bool(route)


def include_configured_views(pyramid_config):
    """
    Include arbitrary additional views based on DB settings.
    """
    rattail_config = pyramid_config.registry.settings.get('rattail_config')
    app = rattail_config.get_app()
    model = app.model
    session = app.make_session()

    # fetch all include-related settings at once
    settings = session.query(model.Setting)\
                      .filter(model.Setting.name.like('tailbone.includes.%'))\
                      .all()

    for setting in settings:
        if setting.value:
            try:
                pyramid_config.include(setting.value)
            except:
                log.warning("pyramid failed to include: %s", exc_info=True)

    session.close()
