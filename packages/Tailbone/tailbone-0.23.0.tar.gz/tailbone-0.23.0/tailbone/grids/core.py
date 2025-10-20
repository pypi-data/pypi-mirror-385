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
Core Grid Classes
"""

import inspect
import logging
import warnings
from urllib.parse import urlencode

import sqlalchemy as sa
from sqlalchemy import orm

from wuttjamaican.util import UNSPECIFIED
from rattail.db.types import GPCType
from rattail.util import prettify, pretty_boolean

from pyramid.renderers import render
from webhelpers2.html import HTML, tags
from paginate_sqlalchemy import SqlalchemyOrmPage

from wuttaweb.grids import Grid as WuttaGrid, GridAction as WuttaGridAction, SortInfo
from wuttaweb.util import FieldList
from . import filters as gridfilters
from tailbone.db import Session
from tailbone.util import raw_datetime


log = logging.getLogger(__name__)


class Grid(WuttaGrid):
    """
    Base class for all grids.

    This is now a subclass of
    :class:`wuttaweb:wuttaweb.grids.base.Grid`, and exists to add
    customizations which have traditionally been part of Tailbone.

    Some of these customizations are still undocumented.  Some will
    eventually be moved to the upstream/parent class, and possibly
    some will be removed outright.  What docs we have, are shown here.

    .. _Buefy docs: https://buefy.org/documentation/table/

    .. attribute:: checkable

       Optional callback to determine if a given row is checkable,
       i.e. this allows hiding checkbox for certain rows if needed.

       This may be either a Python callable, or string representing a
       JS callable.  If the latter, according to the `Buefy docs`_:

       .. code-block:: none

          Custom method to verify if a row is checkable, works when is
          checkable.

          Function (row: Object)

       In other words this JS callback would be invoked for each data
       row in the client-side grid.

       But if a Python callable is used, then it will be invoked for
       each row object in the server-side grid.  For instance::

          def checkable(obj):
              if obj.some_property == True:
                  return True
              return False

          grid.checkable = checkable

    .. attribute:: check_handler

       Optional JS callback for the ``@check`` event of the underlying
       Buefy table component.  See the `Buefy docs`_ for more info,
       but for convenience they say this (as of writing):

       .. code-block:: none

          Triggers when the checkbox in a row is clicked and/or when
          the header checkbox is clicked

       For instance, you might set ``grid.check_handler =
       'rowChecked'`` and then define the handler within your template
       (e.g. ``/widgets/index.mako``) like so:

       .. code-block:: none

          <%def name="modify_this_page_vars()">
            ${parent.modify_this_page_vars()}
            <script type="text/javascript">

              TailboneGrid.methods.rowChecked = function(checkedList, row) {
                  if (!row) {
                      console.log("no row, so header checkbox was clicked")
                  } else {
                      console.log(row)
                      if (checkedList.includes(row)) {
                          console.log("clicking row checkbox ON")
                      } else {
                          console.log("clicking row checkbox OFF")
                      }
                  }
                  console.log(checkedList)
              }

            </script>
          </%def>

    .. attribute:: raw_renderers

       Dict of "raw" field renderers.  See also
       :meth:`set_raw_renderer()`.

       When present, these are rendered "as-is" into the grid
       template, whereas the more typical scenario involves rendering
       each field "into" a span element, like:

       .. code-block:: html

          <span v-html="RENDERED-FIELD"></span>

       So instead of injecting into a span, any "raw" fields defined
       via this dict, will be injected as-is, like:

       .. code-block:: html

          RENDERED-FIELD

       Note that each raw renderer is called only once, and *without*
       any arguments.  Likely the only use case for this, is to inject
       a Vue component into the field.  A basic example::

          from webhelpers2.html import HTML

          def myrender():
              return HTML.tag('my-component', **{'v-model': 'props.row.myfield'})

          grid = Grid(
              # ..normal constructor args here..

              raw_renderers={
                  'myfield': myrender,
              },
          )

    .. attribute row_uuid_getter::

       Optional callable to obtain the "UUID" (sic) value for each
       data row.  The default assumption as that each row object has a
       ``uuid`` attribute, but when that isn't the case, *and* the
       grid needs to support checkboxes, we must "pretend" by
       injecting some custom value to the ``uuid`` of the row data.

       If necssary, set this to a callable like so::

          def fake_uuid(row):
              return row.some_custom_key

          grid.row_uuid_getter = fake_uuid
    """

    def __init__(
            self,
            request,
            key=None,
            data=None,
            width='auto',
            model_title=None,
            model_title_plural=None,
            enums={},
            assume_local_times=False,
            invisible=[],
            raw_renderers={},
            extra_row_class=None,
            url='#',
            use_byte_string_filters=False,
            checkboxes=False,
            checked=None,
            check_handler=None,
            check_all_handler=None,
            checkable=None,
            row_uuid_getter=None,
            clicking_row_checks_box=False,
            click_handlers=None,
            main_actions=[],
            more_actions=[],
            delete_speedbump=False,
            ajax_data_url=None,
            expose_direct_link=False,
            **kwargs,
    ):
        if 'component' in kwargs:
            warnings.warn("component param is deprecated for Grid(); "
                          "please use vue_tagname param instead",
                          DeprecationWarning, stacklevel=2)
            kwargs.setdefault('vue_tagname', kwargs.pop('component'))

        if 'default_sortkey' in kwargs:
            warnings.warn("default_sortkey param is deprecated for Grid(); "
                          "please use sort_defaults param instead",
                          DeprecationWarning, stacklevel=2)
        if 'default_sortdir' in kwargs:
            warnings.warn("default_sortdir param is deprecated for Grid(); "
                          "please use sort_defaults param instead",
                          DeprecationWarning, stacklevel=2)
        if 'default_sortkey' in kwargs or 'default_sortdir' in kwargs:
            sortkey = kwargs.pop('default_sortkey', None)
            sortdir = kwargs.pop('default_sortdir', 'asc')
            if sortkey:
                kwargs.setdefault('sort_defaults', [(sortkey, sortdir)])

        if 'pageable' in kwargs:
            warnings.warn("pageable param is deprecated for Grid(); "
                          "please use paginated param instead",
                          DeprecationWarning, stacklevel=2)
            kwargs.setdefault('paginated', kwargs.pop('pageable'))

        if 'default_pagesize' in kwargs:
            warnings.warn("default_pagesize param is deprecated for Grid(); "
                          "please use pagesize param instead",
                          DeprecationWarning, stacklevel=2)
            kwargs.setdefault('pagesize', kwargs.pop('default_pagesize'))

        if 'default_page' in kwargs:
            warnings.warn("default_page param is deprecated for Grid(); "
                          "please use page param instead",
                          DeprecationWarning, stacklevel=2)
            kwargs.setdefault('page', kwargs.pop('default_page'))

        if 'searchable' in kwargs:
            warnings.warn("searchable param is deprecated for Grid(); "
                          "please use searchable_columns param instead",
                          DeprecationWarning, stacklevel=2)
            kwargs.setdefault('searchable_columns', kwargs.pop('searchable'))

        # TODO: this should not be needed once all templates correctly
        # reference grid.vue_component etc.
        kwargs.setdefault('vue_tagname', 'tailbone-grid')

        # nb. these must be set before super init, as they are
        # referenced when constructing filters
        self.assume_local_times = assume_local_times
        self.use_byte_string_filters = use_byte_string_filters

        kwargs['key'] = key
        kwargs['data'] = data
        super().__init__(request, **kwargs)

        self.model_title = model_title
        if not self.model_title and self.model_class and hasattr(self.model_class, 'get_model_title'):
            self.model_title = self.model_class.get_model_title()

        self.model_title_plural = model_title_plural
        if not self.model_title_plural:
            if self.model_class and hasattr(self.model_class, 'get_model_title_plural'):
                self.model_title_plural = self.model_class.get_model_title_plural()
            if not self.model_title_plural:
                self.model_title_plural = '{}s'.format(self.model_title)

        self.width = width
        self.enums = enums or {}
        self.renderers = self.make_default_renderers(self.renderers)
        self.raw_renderers = raw_renderers or {}
        self.invisible = invisible or []
        self.extra_row_class = extra_row_class
        self.url = url

        self.checkboxes = checkboxes
        self.checked = checked
        if self.checked is None:
            self.checked = lambda item: False
        self.check_handler = check_handler
        self.check_all_handler = check_all_handler
        self.checkable = checkable
        self.row_uuid_getter = row_uuid_getter
        self.clicking_row_checks_box = clicking_row_checks_box

        self.click_handlers = click_handlers or {}

        self.delete_speedbump = delete_speedbump

        if ajax_data_url:
            self.ajax_data_url = ajax_data_url
        elif self.request:
            self.ajax_data_url = self.request.path_url
        else:
            self.ajax_data_url = ''

        self.main_actions = main_actions or []
        if self.main_actions:
            warnings.warn("main_actions param is deprecated for Grdi(); "
                          "please use actions param instead",
                          DeprecationWarning, stacklevel=2)
            self.actions.extend(self.main_actions)
        self.more_actions = more_actions or []
        if self.more_actions:
            warnings.warn("more_actions param is deprecated for Grdi(); "
                          "please use actions param instead",
                          DeprecationWarning, stacklevel=2)
            self.actions.extend(self.more_actions)

        self.expose_direct_link = expose_direct_link
        self._whgrid_kwargs = kwargs

    @property
    def component(self):
        """ """
        warnings.warn("Grid.component is deprecated; "
                      "please use vue_tagname instead",
                      DeprecationWarning, stacklevel=2)
        return self.vue_tagname

    @property
    def component_studly(self):
        """ """
        warnings.warn("Grid.component_studly is deprecated; "
                      "please use vue_component instead",
                      DeprecationWarning, stacklevel=2)
        return self.vue_component

    def get_default_sortkey(self):
        """ """
        warnings.warn("Grid.default_sortkey is deprecated; "
                      "please use Grid.sort_defaults instead",
                      DeprecationWarning, stacklevel=2)
        if self.sort_defaults:
            return self.sort_defaults[0].sortkey

    def set_default_sortkey(self, value):
        """ """
        warnings.warn("Grid.default_sortkey is deprecated; "
                      "please use Grid.sort_defaults instead",
                      DeprecationWarning, stacklevel=2)
        if self.sort_defaults:
            info = self.sort_defaults[0]
            self.sort_defaults[0] = SortInfo(value, info.sortdir)
        else:
            self.sort_defaults = [SortInfo(value, 'asc')]

    default_sortkey = property(get_default_sortkey, set_default_sortkey)

    def get_default_sortdir(self):
        """ """
        warnings.warn("Grid.default_sortdir is deprecated; "
                      "please use Grid.sort_defaults instead",
                      DeprecationWarning, stacklevel=2)
        if self.sort_defaults:
            return self.sort_defaults[0].sortdir

    def set_default_sortdir(self, value):
        """ """
        warnings.warn("Grid.default_sortdir is deprecated; "
                      "please use Grid.sort_defaults instead",
                      DeprecationWarning, stacklevel=2)
        if self.sort_defaults:
            info = self.sort_defaults[0]
            self.sort_defaults[0] = SortInfo(info.sortkey, value)
        else:
            raise ValueError("cannot set default_sortdir without default_sortkey")

    default_sortdir = property(get_default_sortdir, set_default_sortdir)

    def get_pageable(self):
        """ """
        warnings.warn("Grid.pageable is deprecated; "
                      "please use Grid.paginated instead",
                      DeprecationWarning, stacklevel=2)
        return self.paginated

    def set_pageable(self, value):
        """ """
        warnings.warn("Grid.pageable is deprecated; "
                      "please use Grid.paginated instead",
                      DeprecationWarning, stacklevel=2)
        self.paginated = value

    pageable = property(get_pageable, set_pageable)

    def hide_column(self, key):
        """
        This *removes* a column from the grid, altogether.

        This method is deprecated; use :meth:`remove()` instead.
        """
        warnings.warn("Grid.hide_column() is deprecated; please use "
                      "Grid.remove() instead.",
                      DeprecationWarning, stacklevel=2)
        self.remove(key)

    def hide_columns(self, *keys):
        """
        This *removes* columns from the grid, altogether.

        This method is deprecated; use :meth:`remove()` instead.
        """
        self.remove(*keys)

    def set_invisible(self, key, invisible=True):
        """
        Mark the given column as "invisible" (but do not remove it).

        Use :meth:`remove()` if you actually want to remove it.
        """
        if invisible:
            if key not in self.invisible:
                self.invisible.append(key)
        else:
            if key in self.invisible:
                self.invisible.remove(key)

    def insert_before(self, field, newfield):
        self.columns.insert_before(field, newfield)

    def insert_after(self, field, newfield):
        self.columns.insert_after(field, newfield)

    def replace(self, oldfield, newfield):
        self.insert_after(oldfield, newfield)
        self.remove(oldfield)

    def set_joiner(self, key, joiner):
        """ """
        if joiner is None:
            warnings.warn("specifying None is deprecated for Grid.set_joiner(); "
                          "please use Grid.remove_joiner() instead",
                          DeprecationWarning, stacklevel=2)
            self.remove_joiner(key)
        else:
            super().set_joiner(key, joiner)

    def set_sorter(self, key, *args, **kwargs):
        """ """

        if len(args) == 1:
            if kwargs:
                warnings.warn("kwargs are ignored for Grid.set_sorter(); "
                              "please refactor your code accordingly",
                              DeprecationWarning, stacklevel=2)
            if args[0] is None:
                warnings.warn("specifying None is deprecated for Grid.set_sorter(); "
                              "please use Grid.remove_sorter() instead",
                              DeprecationWarning, stacklevel=2)
                self.remove_sorter(key)
            else:
                super().set_sorter(key, args[0])

        elif len(args) == 0:
            super().set_sorter(key)

        else:
            warnings.warn("multiple args are deprecated for Grid.set_sorter(); "
                          "please refactor your code accordingly",
                          DeprecationWarning, stacklevel=2)
            self.sorters[key] = self.make_sorter(*args, **kwargs)

    def set_filter(self, key, *args, **kwargs):
        """ """
        if len(args) == 1:
            if args[0] is None:
                warnings.warn("specifying None is deprecated for Grid.set_filter(); "
                              "please use Grid.remove_filter() instead",
                              DeprecationWarning, stacklevel=2)
                self.remove_filter(key)
                return

        # TODO: our make_filter() signature differs from upstream,
        # so must call it explicitly instead of delegating to super
        kwargs.setdefault('label', self.get_label(key))
        self.filters[key] = self.make_filter(key, *args, **kwargs)

    def set_click_handler(self, key, handler):
        if handler:
            self.click_handlers[key] = handler
        else:
            self.click_handlers.pop(key, None)

    def has_click_handler(self, key):
        return key in self.click_handlers

    def set_raw_renderer(self, key, renderer):
        """
        Set or remove the "raw" renderer for the given field.

        See :attr:`raw_renderers` for more about these.

        :param key: Field name.

        :param renderer: Either a renderer callable, or ``None``.
        """
        if renderer:
            self.raw_renderers[key] = renderer
        else:
            self.raw_renderers.pop(key, None)

    def set_type(self, key, type_):
        if type_ == 'boolean':
            self.set_renderer(key, self.render_boolean)
        elif type_ == 'currency':
            self.set_renderer(key, self.render_currency)
        elif type_ == 'datetime':
            self.set_renderer(key, self.render_datetime)
        elif type_ == 'datetime_local':
            self.set_renderer(key, self.render_datetime_local)
        elif type_ == 'enum':
            self.set_renderer(key, self.render_enum)
        elif type_ == 'gpc':
            self.set_renderer(key, self.render_gpc)
        elif type_ == 'percent':
            self.set_renderer(key, self.render_percent)
        elif type_ == 'quantity':
            self.set_renderer(key, self.render_quantity)
        elif type_ == 'duration':
            self.set_renderer(key, self.render_duration)
        elif type_ == 'duration_hours':
            self.set_renderer(key, self.render_duration_hours)
        else:
            raise ValueError("Unsupported type for column '{}': {}".format(key, type_))

    def set_enum(self, key, enum):
        if enum:
            self.enums[key] = enum
            self.set_type(key, 'enum')
            if key in self.filters:
                self.filters[key].set_value_renderer(gridfilters.EnumValueRenderer(enum))
        else:
            self.enums.pop(key, None)

    def render_generic(self, obj, column_name):
        return self.obtain_value(obj, column_name)

    def render_boolean(self, obj, column_name):
        value = self.obtain_value(obj, column_name)
        return pretty_boolean(value)

    def obtain_value(self, obj, column_name):
        """
        Try to obtain and return the value from the given object, for
        the given column name.

        :returns: The value, or ``None`` if no value was found.
        """
        # TODO: this seems a little hacky, is there a better way?
        # nb. this may only be relevant for import/export batch view?
        if isinstance(obj, sa.engine.Row):
            return obj._mapping[column_name]

        if isinstance(obj, dict):
            return obj[column_name]

        try:
            return getattr(obj, column_name)
        except AttributeError:
            pass

        try:
            return obj[column_name]
        except (TypeError, KeyError):
            pass

    def render_currency(self, obj, column_name):
        value = self.obtain_value(obj, column_name)
        if value is None:
            return ""
        if value < 0:
            return "(${:0,.2f})".format(0 - value)
        return "${:0,.2f}".format(value)

    def render_datetime(self, obj, column_name):
        value = self.obtain_value(obj, column_name)
        if value is None:
            return ""
        return raw_datetime(self.request.rattail_config, value)

    def render_datetime_local(self, obj, column_name):
        value = self.obtain_value(obj, column_name)
        if value is None:
            return ""
        app = self.request.rattail_config.get_app()
        value = app.localtime(value)
        return raw_datetime(self.request.rattail_config, value)

    def render_enum(self, obj, column_name):
        value = self.obtain_value(obj, column_name)
        if value is None:
            return ""
        enum = self.enums.get(column_name)
        if enum and value in enum:
            return str(enum[value])
        return str(value)

    def render_gpc(self, obj, column_name):
        value = self.obtain_value(obj, column_name)
        if value is None:
            return ""
        return value.pretty()

    def render_percent(self, obj, column_name):
        app = self.request.rattail_config.get_app()
        value = self.obtain_value(obj, column_name)
        return app.render_percent(value, places=3)

    def render_quantity(self, obj, column_name):
        value = self.obtain_value(obj, column_name)
        app = self.request.rattail_config.get_app()
        return app.render_quantity(value)

    def render_duration(self, obj, column_name):
        seconds = self.obtain_value(obj, column_name)
        if seconds is None:
            return ""
        app = self.request.rattail_config.get_app()
        return app.render_duration(seconds=seconds)

    def render_duration_hours(self, obj, field):
        value = self.obtain_value(obj, field)
        if value is None:
            return ""
        app = self.request.rattail_config.get_app()
        return app.render_duration(hours=value)

    def set_url(self, url):
        self.url = url

    def make_url(self, obj, i=None):
        if callable(self.url):
            return self.url(obj)
        return self.url

    def make_default_renderers(self, renderers):
        """
        Make the default set of column renderers for the grid.

        We honor any existing renderers which have already been set, but then
        we also try to supplement that by auto-assigning renderers based on
        underlying column type.  Note that this special logic only applies to
        grids with a valid :attr:`model_class`.
        """
        if self.model_class:
            mapper = orm.class_mapper(self.model_class)
            for prop in mapper.iterate_properties:
                if isinstance(prop, orm.ColumnProperty) and not prop.key.endswith('uuid'):
                    if prop.key in self.columns and prop.key not in renderers:
                        if len(prop.columns) == 1:
                            coltype = prop.columns[0].type
                            renderers[prop.key] = self.get_renderer_for_column_type(coltype)

        return renderers

    def get_renderer_for_column_type(self, coltype):
        """
        Returns an appropriate renderer according to the given SA column type.
        """
        if isinstance(coltype, sa.Boolean):
            return self.render_boolean

        if isinstance(coltype, sa.DateTime):
            if self.assume_local_times:
                return self.render_datetime_local
            else:
                return self.render_datetime

        if isinstance(coltype, GPCType):
            return self.render_gpc

        return self.render_generic

    def checkbox_column_format(self, column_number, row_number, item):
        return HTML.td(self.render_checkbox(item), class_='checkbox')

    def actions_column_format(self, column_number, row_number, item):
        return HTML.td(self.render_actions(item, row_number), class_='actions')

    # TODO: upstream should handle this..
    def make_backend_filters(self, filters=None):
        """ """
        final = self.get_default_filters()
        if filters:
            final.update(filters)
        return final

    def get_default_filters(self):
        """
        Returns the default set of filters provided by the grid.
        """
        if hasattr(self, 'default_filters'):
            if callable(self.default_filters):
                return self.default_filters()
            return self.default_filters
        filters = gridfilters.GridFilterSet()
        if self.model_class:
            mapper = orm.class_mapper(self.model_class)
            for prop in mapper.iterate_properties:
                if not isinstance(prop, orm.ColumnProperty):
                    continue
                if prop.key.endswith('uuid'):
                    continue
                if len(prop.columns) != 1:
                    continue
                column = prop.columns[0]
                if isinstance(column.type, sa.LargeBinary):
                    continue
                filters[prop.key] = self.make_filter(prop.key, column)
        return filters

    def make_filter(self, key, column, **kwargs):
        """
        Make a filter suitable for use with the given column.
        """
        factory = kwargs.pop('factory', None)
        if not factory:
            factory = gridfilters.AlchemyGridFilter
            if isinstance(column.type, sa.String):
                factory = gridfilters.AlchemyStringFilter
            elif isinstance(column.type, sa.Numeric):
                factory = gridfilters.AlchemyNumericFilter
            elif isinstance(column.type, sa.BigInteger):
                factory = gridfilters.AlchemyBigIntegerFilter
            elif isinstance(column.type, sa.Integer):
                factory = gridfilters.AlchemyIntegerFilter
            elif isinstance(column.type, sa.Boolean):
                # TODO: check column for nullable here?
                factory = gridfilters.AlchemyNullableBooleanFilter
            elif isinstance(column.type, sa.Date):
                factory = gridfilters.AlchemyDateFilter
            elif isinstance(column.type, sa.DateTime):
                if self.assume_local_times:
                    factory = gridfilters.AlchemyLocalDateTimeFilter
                else:
                    factory = gridfilters.AlchemyDateTimeFilter
            elif isinstance(column.type, GPCType):
                factory = gridfilters.AlchemyGPCFilter
        kwargs['column'] = column
        kwargs.setdefault('config', self.request.rattail_config)
        kwargs.setdefault('encode_values', self.use_byte_string_filters)
        return factory(key, **kwargs)

    def iter_filters(self):
        """
        Iterate over all filters available to the grid.
        """
        return self.filters.values()

    def iter_active_filters(self):
        """
        Iterate over all *active* filters for the grid.  Whether a filter is
        active is determined by current grid settings.
        """
        for filtr in self.iter_filters():
            if filtr.active:
                yield filtr

    def make_simple_sorter(self, key, foldcase=False):
        """ """
        warnings.warn("Grid.make_simple_sorter() is deprecated; "
                      "please use Grid.make_sorter() instead",
                      DeprecationWarning, stacklevel=2)
        return self.make_sorter(key, foldcase=foldcase)

    def get_pagesize_options(self, default=None):
        """ """
        # let upstream check config
        options = super().get_pagesize_options(default=UNSPECIFIED)
        if options is not UNSPECIFIED:
            return options

        # fallback to legacy config
        options = self.config.get_list('tailbone.grid.pagesize_options')
        if options:
            warnings.warn("tailbone.grid.pagesize_options setting is deprecated; "
                          "please set wuttaweb.grids.default_pagesize_options instead",
                          DeprecationWarning)
            options = [int(size) for size in options
                       if size.isdigit()]
            if options:
                return options

        if default:
            return default

        # use upstream default
        return super().get_pagesize_options()

    def get_pagesize(self, default=None):
        """ """
        # let upstream check config
        pagesize = super().get_pagesize(default=UNSPECIFIED)
        if pagesize is not UNSPECIFIED:
            return pagesize

        # fallback to legacy config
        pagesize = self.config.get_int('tailbone.grid.default_pagesize')
        if pagesize:
            warnings.warn("tailbone.grid.default_pagesize setting is deprecated; "
                          "please use wuttaweb.grids.default_pagesize instead",
                          DeprecationWarning)
            return pagesize

        if default:
            return default

        # use upstream default
        return super().get_pagesize()

    def get_default_pagesize(self): # pragma: no cover
        """ """
        warnings.warn("Grid.get_default_pagesize() method is deprecated; "
                      "please use Grid.get_pagesize() of Grid.page instead",
                      DeprecationWarning, stacklevel=2)

        if self.default_pagesize:
            return self.default_pagesize

        return self.get_pagesize()

    def load_settings(self, **kwargs):
        """ """
        if 'store' in kwargs:
            warnings.warn("the 'store' param is deprecated for load_settings(); "
                          "please use the 'persist' param instead",
                          DeprecationWarning, stacklevel=2)
            kwargs.setdefault('persist', kwargs.pop('store'))

        persist = kwargs.get('persist', True)

        # initial default settings
        settings = {}
        if self.sortable:
            if self.sort_defaults:
                # nb. as of writing neither Buefy nor Oruga support a
                # multi-column *default* sort; so just use first sorter
                sortinfo = self.sort_defaults[0]
                settings['sorters.length'] = 1
                settings['sorters.1.key'] = sortinfo.sortkey
                settings['sorters.1.dir'] = sortinfo.sortdir
            else:
                settings['sorters.length'] = 0
        if self.paginated:
            settings['pagesize'] = self.pagesize
            settings['page'] = self.page
        if self.filterable:
            for filtr in self.iter_filters():
                defaults = self.filter_defaults.get(filtr.key, {})
                settings[f'filter.{filtr.key}.active'] = defaults.get('active',
                                                                      filtr.default_active)
                settings[f'filter.{filtr.key}.verb'] = defaults.get('verb',
                                                                    filtr.default_verb)
                settings[f'filter.{filtr.key}.value'] = defaults.get('value',
                                                                     filtr.default_value)

        # If user has default settings on file, apply those first.
        if self.user_has_defaults():
            self.apply_user_defaults(settings)

        # If request contains instruction to reset to default filters, then we
        # can skip the rest of the request/session checks.
        if self.request.GET.get('reset-view'):
            pass

        # If request has filter settings, grab those, then grab sort/pager
        # settings from request or session.
        elif self.request_has_settings('filter'):
            self.update_filter_settings(settings, src='request')
            if self.request_has_settings('sort'):
                self.update_sort_settings(settings, src='request')
            else:
                self.update_sort_settings(settings, src='session')
            self.update_page_settings(settings)

        # If request has no filter settings but does have sort settings, grab
        # those, then grab filter settings from session, then grab pager
        # settings from request or session.
        elif self.request_has_settings('sort'):
            self.update_sort_settings(settings, src='request')
            self.update_filter_settings(settings, src='session')
            self.update_page_settings(settings)

        # NOTE: These next two are functionally equivalent, but are kept
        # separate to maintain the narrative...

        # If request has no filter/sort settings but does have pager settings,
        # grab those, then grab filter/sort settings from session.
        elif self.request_has_settings('page'):
            self.update_page_settings(settings)
            self.update_filter_settings(settings, src='session')
            self.update_sort_settings(settings, src='session')

        # If request has no settings, grab all from session.
        elif self.session_has_settings():
            self.update_filter_settings(settings, src='session')
            self.update_sort_settings(settings, src='session')
            self.update_page_settings(settings)

        # If no settings were found in request or session, don't store result.
        else:
            persist = False
            
        # Maybe store settings for next time.
        if persist:
            self.persist_settings(settings, dest='session')

        # If request contained instruction to save current settings as defaults
        # for the current user, then do that.
        if self.request.GET.get('save-current-filters-as-defaults') == 'true':
            self.persist_settings(settings, dest='defaults')

        # update ourself to reflect settings
        if self.filterable:
            for filtr in self.iter_filters():
                filtr.active = settings['filter.{}.active'.format(filtr.key)]
                filtr.verb = settings['filter.{}.verb'.format(filtr.key)]
                filtr.value = settings['filter.{}.value'.format(filtr.key)]
        if self.sortable:
            # and self.sort_on_backend:
            self.active_sorters = []
            for i in range(1, settings['sorters.length'] + 1):
                self.active_sorters.append({
                    'key': settings[f'sorters.{i}.key'],
                    'dir': settings[f'sorters.{i}.dir'],
                })
        if self.paginated:
            self.pagesize = settings['pagesize']
            self.page = settings['page']

    def user_has_defaults(self):
        """
        Check to see if the current user has default settings on file for this grid.
        """
        user = self.request.user
        if not user:
            return False

        # NOTE: we used to leverage `self.session` here, but sometimes we might
        # be showing a grid of data from another system...so always use
        # Tailbone Session now, for the settings.  hopefully that didn't break
        # anything...
        session = Session()
        if user not in session:
            # TODO: pretty sure there is no need to *merge* here..
            # but we shall see if any breakage happens maybe
            #user = session.merge(user)
            user = session.get(user.__class__, user.uuid)

        app = self.request.rattail_config.get_app()

        # user defaults should be all or nothing, so just check one key
        key = f'tailbone.{user.uuid}.grid.{self.key}.sorters.length'
        if app.get_setting(session, key) is not None:
            return True

        # TODO: this is deprecated but should work its way out of the
        # system in a little while (?)..then can remove this entirely
        key = f'tailbone.{user.uuid}.grid.{self.key}.sortkey'
        if app.get_setting(session, key) is not None:
            return True

        return False

    def apply_user_defaults(self, settings):
        """
        Update the given settings dict with user defaults, if any exist.
        """
        app = self.request.rattail_config.get_app()
        session = Session()
        prefix = f'tailbone.{self.request.user.uuid}.grid.{self.key}'

        def merge(key, normalize=lambda v: v):
            value = app.get_setting(session, f'{prefix}.{key}')
            settings[key] = normalize(value)

        if self.filterable:
            for filtr in self.iter_filters():
                merge('filter.{}.active'.format(filtr.key), lambda v: v == 'true')
                merge('filter.{}.verb'.format(filtr.key))
                merge('filter.{}.value'.format(filtr.key))

        if self.sortable:

            # first clear existing settings for *sorting* only
            # nb. this is because number of sort settings will vary
            for key in list(settings):
                if key.startswith('sorters.'):
                    del settings[key]

            # check for *deprecated* settings, and use those if present
            # TODO: obviously should stop this, but must wait until
            # all old settings have been flushed out.  which in the
            # case of user-persisted settings, could be a while...
            sortkey = app.get_setting(session, f'{prefix}.sortkey')
            if sortkey:
                settings['sorters.length'] = 1
                settings['sorters.1.key'] = sortkey
                settings['sorters.1.dir'] = app.get_setting(session, f'{prefix}.sortdir')

                # nb. re-persist these user settings per new
                # convention, so deprecated settings go away and we
                # can remove this logic after a while..
                app = self.request.rattail_config.get_app()
                model = app.model
                prefix = f'tailbone.{self.request.user.uuid}.grid.{self.key}'
                query = Session.query(model.Setting)\
                               .filter(sa.or_(
                                   model.Setting.name.like(f'{prefix}.sorters.%'),
                                   model.Setting.name == f'{prefix}.sortkey',
                                   model.Setting.name == f'{prefix}.sortdir'))
                for setting in query.all():
                    Session.delete(setting)
                Session.flush()

                def persist(key):
                    app.save_setting(Session(),
                                     f'tailbone.{self.request.user.uuid}.grid.{self.key}.{key}',
                                     settings[key])

                persist('sorters.length')
                persist('sorters.1.key')
                persist('sorters.1.dir')

            else: # the future
                merge('sorters.length', int)
                for i in range(1, settings['sorters.length'] + 1):
                    merge(f'sorters.{i}.key')
                    merge(f'sorters.{i}.dir')

        if self.paginated:
            merge('pagesize', int)
            merge('page', int)

    def request_has_settings(self, type_):
        """ """
        if super().request_has_settings(type_):
            return True

        if type_ == 'sort':

            # TODO: remove this eventually, but some links in the wild
            # may still include these params, so leave it for now
            for key in ['sortkey', 'sortdir']:
                if key in self.request.GET:
                    return True

        return False

    def session_has_settings(self):
        """
        Determine if the current session contains any settings for the grid.
        """
        # session should have all or nothing, so just check a few keys which
        # should be guaranteed present if anything has been stashed
        prefix = f'grid.{self.key}'
        for key in ['page', 'sorters.length']:
            if f'{prefix}.{key}' in self.request.session:
                return True
        return any([key.startswith(f'{prefix}.filter')
                    for key in self.request.session])

    def persist_settings(self, settings, dest='session'):
        """ """
        if dest not in ('defaults', 'session'):
            raise ValueError(f"invalid dest identifier: {dest}")

        app = self.request.rattail_config.get_app()
        model = app.model

        def persist(key, value=lambda k: settings.get(k)):
            if dest == 'defaults':
                skey = 'tailbone.{}.grid.{}.{}'.format(self.request.user.uuid, self.key, key)
                app.save_setting(Session(), skey, value(key))
            else: # dest == session
                skey = 'grid.{}.{}'.format(self.key, key)
                self.request.session[skey] = value(key)

        if self.filterable:
            for filtr in self.iter_filters():
                persist('filter.{}.active'.format(filtr.key), value=lambda k: str(settings[k]).lower())
                persist('filter.{}.verb'.format(filtr.key))
                persist('filter.{}.value'.format(filtr.key))

        if self.sortable:

            # first must clear all sort settings from dest. this is
            # because number of sort settings will vary, so we delete
            # all and then write all

            if dest == 'defaults':
                prefix = f'tailbone.{self.request.user.uuid}.grid.{self.key}'
                query = Session.query(model.Setting)\
                               .filter(sa.or_(
                                   model.Setting.name.like(f'{prefix}.sorters.%'),
                                   # TODO: remove these eventually,
                                   # but probably should wait until
                                   # all nodes have been upgraded for
                                   # (quite) a while?
                                   model.Setting.name == f'{prefix}.sortkey',
                                   model.Setting.name == f'{prefix}.sortdir'))
                for setting in query.all():
                    Session.delete(setting)
                Session.flush()

            else: # session
                # remove sort settings from user session
                prefix = f'grid.{self.key}'
                for key in list(self.request.session):
                    if key.startswith(f'{prefix}.sorters.'):
                        del self.request.session[key]
                # TODO: definitely will remove these, but leave for
                # now so they don't monkey with current user sessions
                # when next upgrade happens.  so, remove after all are
                # upgraded
                self.request.session.pop(f'{prefix}.sortkey', None)
                self.request.session.pop(f'{prefix}.sortdir', None)

            # now save sort settings to dest
            if 'sorters.length' in settings:
                persist('sorters.length')
                for i in range(1, settings['sorters.length'] + 1):
                    persist(f'sorters.{i}.key')
                    persist(f'sorters.{i}.dir')

        if self.paginated:
            persist('pagesize')
            persist('page')

    def filter_data(self, data):
        """
        Filter and return the given data set, according to current settings.
        """
        for filtr in self.iter_active_filters():

            # apply filter to data but save reference to original; if data is a
            # SQLAlchemy query and wasn't modified, we don't need to bother
            # with the underlying join (if there is one)
            original = data
            data = filtr.filter(data)
            if filtr.key in self.joiners and filtr.key not in self.joined and (
                    not isinstance(data, orm.Query) or data is not original):

                # this filter requires a join; apply that
                data = self.joiners[filtr.key](data)
                self.joined.add(filtr.key)

        return data

    def make_visible_data(self):
        """ """
        warnings.warn("grid.make_visible_data() method is deprecated; "
                      "please use grid.get_visible_data() instead",
                      DeprecationWarning, stacklevel=2)
        return self.get_visible_data()

    def render_vue_tag(self, master=None, **kwargs):
        """ """
        kwargs.setdefault('ref', 'grid')
        kwargs.setdefault(':csrftoken', 'csrftoken')

        if (master and master.deletable and master.has_perm('delete')
            and master.delete_confirm == 'simple'):
            kwargs.setdefault('@deleteActionClicked', 'deleteObject')

        return HTML.tag(self.vue_tagname, **kwargs)

    def render_vue_template(self, template='/grids/complete.mako', **context):
        """ """
        return self.render_complete(template=template, **context)

    def render_complete(self, template='/grids/complete.mako', **kwargs):
        """
        Render the grid, complete with filters.  Note that this also
        includes the context menu items and grid tools.
        """
        if 'grid_columns' not in kwargs:
            kwargs['grid_columns'] = self.get_vue_columns()

        if 'grid_data' not in kwargs:
            kwargs['grid_data'] = self.get_table_data()

        if 'static_data' not in kwargs:
            kwargs['static_data'] = self.has_static_data()

        if self.filterable and 'filters_data' not in kwargs:
            kwargs['filters_data'] = self.get_filters_data()

        if self.filterable and 'filters_sequence' not in kwargs:
            kwargs['filters_sequence'] = self.get_filters_sequence()

        context = kwargs
        context['grid'] = self
        context['request'] = self.request
        context.setdefault('allow_save_defaults', True)
        context.setdefault('view_click_handler', self.get_view_click_handler())
        html = render(template, context)
        return HTML.literal(html)

    def render_buefy(self, **kwargs):
        """ """
        warnings.warn("Grid.render_buefy() is deprecated; "
                      "please use Grid.render_complete() instead",
                      DeprecationWarning, stacklevel=2)
        return self.render_complete(**kwargs)

    def render_table_element(self, template='/grids/b-table.mako',
                             data_prop='gridData', empty_labels=False,
                             literal=False,
                             **kwargs):
        """
        This is intended for ad-hoc "small" grids with static data.  Renders
        just a ``<b-table>`` element instead of the typical "full" grid.
        """
        context = dict(kwargs)
        context['grid'] = self
        context['request'] = self.request
        context['data_prop'] = data_prop
        context['empty_labels'] = empty_labels
        if 'grid_columns' not in context:
            context['grid_columns'] = self.get_vue_columns()
        context.setdefault('paginated', False)
        if context['paginated']:
            context.setdefault('per_page', 20)
        context['view_click_handler'] = self.get_view_click_handler()
        result = render(template, context)
        if literal:
            result = HTML.literal(result)
        return result

    def get_view_click_handler(self):
        """ """
        # locate the 'view' action
        # TODO: this should be easier, and/or moved elsewhere?
        view = None
        for action in self.actions:
            if action.key == 'view':
                return getattr(action, 'click_handler', None)

    def set_filters_sequence(self, filters, only=False):
        """
        Explicitly set the sequence for grid filters, using the sequence
        provided.  If the grid currently has more filters than are mentioned in
        the given sequence, the sequence will come first and all others will be
        tacked on at the end.

        :param filters: Sequence of filter keys, i.e. field names.

        :param only: If true, then *only* those filters specified will
           be kept, and all others discarded.  If false then any
           filters not specified will still be tacked onto the end, in
           alphabetical order.
        """
        new_filters = gridfilters.GridFilterSet()
        for field in filters:
            if field in self.filters:
                new_filters[field] = self.filters.pop(field)
            else:
                log.warning("field '%s' is not in current filter set", field)
        if not only:
            for field in sorted(self.filters):
                new_filters[field] = self.filters[field]
        self.filters = new_filters

    def get_filters_sequence(self):
        """
        Returns a list of filter keys (strings) in the sequence with which they
        should be displayed in the UI.
        """
        return list(self.filters)

    def get_filters_data(self):
        """
        Returns a dict of current filters data, for use with index view.
        """
        data = {}
        for filtr in self.filters.values():

            valueless = [v for v in filtr.valueless_verbs
                         if v in filtr.verbs]

            multiple_values = [v for v in filtr.multiple_value_verbs
                               if v in filtr.verbs]

            choices = []
            choice_labels = {}
            if filtr.choices:
                choices = list(filtr.choices)
                choice_labels = dict(filtr.choices)
            elif self.enums and filtr.key in self.enums:
                choices = list(self.enums[filtr.key])
                choice_labels = self.enums[filtr.key]

            data[filtr.key] = {
                'key': filtr.key,
                'label': filtr.label,
                'active': filtr.active,
                'visible': filtr.active,
                'verbs': filtr.verbs,
                'valueless_verbs': valueless,
                'multiple_value_verbs': multiple_values,
                'verb_labels': filtr.verb_labels,
                'verb': filtr.verb or filtr.default_verb or filtr.verbs[0],
                'value': str(filtr.value) if filtr.value is not None else "",
                'data_type': filtr.data_type,
                'choices': choices,
                'choice_labels': choice_labels,
            }

        return data

    def render_actions(self, row, i): # pragma: no cover
        """ """
        warnings.warn("grid.render_actions() is deprecated!",
                      DeprecationWarning, stacklevel=2)

        actions = [self.render_action(a, row, i)
                   for a in self.actions]
        actions = [a for a in actions if a]
        return HTML.literal('').join(actions)

    def render_action(self, action, row, i): # pragma: no cover
        """ """
        warnings.warn("grid.render_action() is deprecated!",
                      DeprecationWarning, stacklevel=2)

        url = action.get_url(row, i)
        if url:
            kwargs = {'class_': action.key, 'target': action.target}
            if action.icon:
                icon = HTML.tag('span', class_='ui-icon ui-icon-{}'.format(action.icon))
                return tags.link_to(icon + action.label, url, **kwargs)
            return tags.link_to(action.label, url, **kwargs)

    def get_row_key(self, item):
        """
        Must return a unique key for the given data item's row.
        """
        mapper = orm.object_mapper(item)
        if len(mapper.primary_key) == 1:
            return getattr(item, mapper.primary_key[0].key)
        raise NotImplementedError

    def checkbox(self, item):
        """
        Returns boolean indicating whether a checkbox should be rendererd for
        the given data item's row.
        """
        return True

    def render_checkbox(self, item):
        """
        Renders a checkbox cell for the given item, if applicable.
        """
        if not self.checkbox(item):
            return ''
        return tags.checkbox('checkbox-{}-{}'.format(self.key, self.get_row_key(item)),
                             checked=self.checked(item))

    def has_static_data(self):
        """
        Should return ``True`` if the grid data can be considered "static"
        (i.e. a list of values).  Will return ``False`` otherwise, e.g. if the
        data is represented as a SQLAlchemy query.
        """
        # TODO: should make this smarter?
        if isinstance(self.data, list):
            return True
        return False

    def get_vue_columns(self):
        """ """
        columns = super().get_vue_columns()

        for column in columns:
            column['visible'] = column['field'] not in self.invisible

        return columns

    def get_table_columns(self):
        """ """
        warnings.warn("grid.get_table_columns() method is deprecated; "
                      "please use grid.get_vue_columns() instead",
                      DeprecationWarning, stacklevel=2)
        return self.get_vue_columns()

    def get_uuid_for_row(self, rowobj):

        # use custom getter if set
        if self.row_uuid_getter:
            return self.row_uuid_getter(rowobj)

        # otherwise fallback to normal uuid, if present
        if hasattr(rowobj, 'uuid'):
            return rowobj.uuid

    def get_vue_context(self):
        """ """
        return self.get_table_data()

    def get_vue_data(self):
        """ """
        table_data = self.get_table_data()
        return table_data['data']

    def get_table_data(self):
        """
        Returns a list of data rows for the grid, for use with
        client-side JS table.
        """
        if hasattr(self, '_table_data'):
            return self._table_data

        # filter / sort / paginate to get "visible" data
        raw_data = self.get_visible_data()
        data = []
        status_map = {}
        checked = []

        # we check for 'all' method and if so, assume we have a Query;
        # otherwise we assume it's something we can use len() with, which could
        # be a list or a Paginator
        if hasattr(raw_data, 'all'):
            count = raw_data.count()
        else:
            count = len(raw_data)

        # iterate over data rows
        checkable = self.checkboxes and self.checkable and callable(self.checkable)
        for i in range(count):
            rowobj = raw_data[i]

            # nb. cache 0-based index on the row, in case client-side
            # logic finds it useful
            row = {'_index': i}

            # if grid allows checkboxes, and we have logic to see if
            # any given row is checkable, add data for that here
            if checkable:
                row['_checkable'] = self.checkable(rowobj)

            # sometimes we need to include some "raw" data columns in our
            # result set, even though the column is not displayed as part of
            # the grid.  this can be used for front-end editing of row data for
            # instance, when the "display" version is different than raw data.
            # here is the hack we use for that.
            columns = list(self.columns)
            if hasattr(self, 'raw_data_columns'):
                columns.extend(self.raw_data_columns)

            # iterate over data fields
            for name in columns:

                # leverage configured rendering logic where applicable;
                # otherwise use "raw" data value as string
                value = self.obtain_value(rowobj, name)
                if self.renderers and name in self.renderers:
                    renderer = self.renderers[name]

                    # TODO: legacy renderer callables require 2 args,
                    # but wuttaweb callables require 3 args
                    sig = inspect.signature(renderer)
                    required = [param for param in sig.parameters.values()
                                if param.default == param.empty]

                    if len(required) == 2:
                        # TODO: legacy renderer
                        value = renderer(rowobj, name)
                    else: # the future
                        value = renderer(rowobj, name, value)

                if value is None:
                    value = ""

                # this value will ultimately be inserted into table
                # cell a la <td v-html="..."> so we must escape it
                # here to be safe
                row[name] = HTML.literal.escape(value)

            # maybe add UUID for convenience
            if 'uuid' not in self.columns:
                uuid = self.get_uuid_for_row(rowobj)
                if uuid:
                    row['uuid'] = uuid

            # set action URL(s) for row, as needed
            self.set_action_urls(row, rowobj, i)

            # set extra row class if applicable
            if self.extra_row_class:
                status = self.extra_row_class(rowobj, i)
                if status:
                    status_map[i] = status

            # set checked flag if applicable
            if self.checkboxes:
                if self.checked(rowobj):
                    checked.append(i)

            data.append(row)

        results = {
            'data': data,
            'row_classes': status_map,
            # TODO: deprecate / remove this
            'row_status_map': status_map,
        }

        if self.checkboxes:
            results['checked_rows'] = checked
            # TODO: this seems a bit hacky, but is required for now to
            # initialize things on the client side...
            var = '{}CurrentData'.format(self.vue_component)
            results['checked_rows_code'] = '[{}]'.format(
                ', '.join(['{}[{}]'.format(var, i) for i in checked]))

        if self.paginated and self.paginate_on_backend:
            results['pager_stats'] = self.get_vue_pager_stats()

        # TODO: is this actually needed now that we have pager_stats?
        if self.paginated and self.pager is not None:
            results['total_items'] = self.pager.item_count
            results['per_page'] = self.pager.items_per_page
            results['page'] = self.pager.page
            results['pages'] = self.pager.page_count
            results['first_item'] = self.pager.first_item
            results['last_item'] = self.pager.last_item
        else:
            results['total_items'] = count

        self._table_data = results
        return self._table_data

    # TODO: remove this when we use upstream GridAction
    def add_action(self, key, **kwargs):
        """ """
        self.actions.append(GridAction(self.request, key, **kwargs))

    def set_action_urls(self, row, rowobj, i):
        """
        Pre-generate all action URLs for the given data row.  Meant for use
        with client-side table, since we can't generate URLs from JS.
        """
        for action in self.actions:
            url = action.get_url(rowobj, i)
            row['_action_url_{}'.format(action.key)] = url


class GridAction(WuttaGridAction):
    """
    Represents a "row action" hyperlink within a grid context.

    This is a subclass of
    :class:`wuttaweb:wuttaweb.grids.base.GridAction`.

    .. warning::

       This class remains for now, to retain compatibility with
       existing code.  But at some point the WuttaWeb class will
       supersede this one entirely.

    :param target: HTML "target" attribute for the ``<a>`` tag.

    :param click_handler: Optional JS click handler for the action.
       This value will be rendered as-is within the final grid
       template, hence the JS string must be callable code.  Note
       that ``props.row`` will be available in the calling context,
       so a couple of examples:

       * ``deleteThisThing(props.row)``
       * ``$emit('do-something', props.row)``
    """

    def __init__(
            self,
            request,
            key,
            target=None,
            click_handler=None,
            **kwargs,
    ):
        # TODO: previously url default was '#' - but i don't think we
        # need that anymore?  guess we'll see..
        #kwargs.setdefault('url', '#')

        super().__init__(request, key, **kwargs)

        self.target = target
        self.click_handler = click_handler


class URLMaker(object):
    """
    URL constructor for use with SQLAlchemy grid pagers.  Logic for this was
    basically copied from the old `webhelpers.paginate` module
    """

    def __init__(self, request):
        self.request = request

    def __call__(self, page):
        params = self.request.GET.copy()
        params["page"] = page
        params["partial"] = "1"
        qs = urlencode(params, True)
        return '{}?{}'.format(self.request.path, qs)
