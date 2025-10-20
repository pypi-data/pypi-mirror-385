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
Progress Views
"""

from tailbone.progress import get_progress_session


def progress(request):
    key = request.matchdict['key']
    session = get_progress_session(request, key,
                                   type=request.GET.get('sessiontype'))

    if session.get('complete'):

        msg = session.get('success_msg')
        if msg:
            request.session.flash(msg)

        bits = session.get('extra_session_bits')
        if bits:
            for key, value in bits.items():
                request.session[key] = value

    elif session.get('error'):
        msg = session.get('error_msg', "An unspecified error occurred.")
        request.session.flash(msg, 'error')

    return session


def cancel(request):
    key = request.matchdict['key']
    session = get_progress_session(request, key)
    session.clear()
    session['canceled'] = True
    session.save()
    msg = request.params.get('cancel_msg', "The operation was canceled.")
    request.session.flash(msg)
    return {}


def defaults(config, **kwargs):
    base = globals()

    progress = kwargs.get('progress', base['progress'])
    config.add_route('progress', '/progress/{key}')
    config.add_view(progress, route_name='progress', renderer='json')

    cancel = kwargs.get('cancel', base['cancel'])
    config.add_route('progress.cancel', '/progress/{key}/cancel')
    config.add_view(cancel, route_name='progress.cancel', renderer='json')


def includeme(config):
    defaults(config)
