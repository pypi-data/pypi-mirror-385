# -*- coding: utf-8; -*-

from unittest.mock import MagicMock, patch

from sqlalchemy import orm

from tailbone.grids import core as mod
from tests.util import WebTestCase


class TestGrid(WebTestCase):

    def setUp(self):
        self.setup_web()
        self.config.setdefault('rattail.web.menus.handler_spec', 'tests.util:NullMenuHandler')

    def make_grid(self, key=None, data=[], **kwargs):
        return mod.Grid(self.request, key=key, data=data, **kwargs)

    def test_basic(self):
        grid = self.make_grid('foo')
        self.assertIsInstance(grid, mod.Grid)

    def test_deprecated_params(self):

        # component
        grid = self.make_grid()
        self.assertEqual(grid.vue_tagname, 'tailbone-grid')
        grid = self.make_grid(component='blarg')
        self.assertEqual(grid.vue_tagname, 'blarg')

        # default_sortkey, default_sortdir
        grid = self.make_grid()
        self.assertEqual(grid.sort_defaults, [])
        grid = self.make_grid(default_sortkey='name')
        self.assertEqual(grid.sort_defaults, [mod.SortInfo('name', 'asc')])
        grid = self.make_grid(default_sortdir='desc')
        self.assertEqual(grid.sort_defaults, [])
        grid = self.make_grid(default_sortkey='name', default_sortdir='desc')
        self.assertEqual(grid.sort_defaults, [mod.SortInfo('name', 'desc')])

        # pageable
        grid = self.make_grid()
        self.assertFalse(grid.paginated)
        grid = self.make_grid(pageable=True)
        self.assertTrue(grid.paginated)

        # default_pagesize
        grid = self.make_grid()
        self.assertEqual(grid.pagesize, 20)
        grid = self.make_grid(default_pagesize=15)
        self.assertEqual(grid.pagesize, 15)

        # default_page
        grid = self.make_grid()
        self.assertEqual(grid.page, 1)
        grid = self.make_grid(default_page=42)
        self.assertEqual(grid.page, 42)

        # searchable
        grid = self.make_grid()
        self.assertEqual(grid.searchable_columns, set())
        grid = self.make_grid(searchable={'foo': True})
        self.assertEqual(grid.searchable_columns, {'foo'})

    def test_vue_tagname(self):

        # default
        grid = self.make_grid('foo')
        self.assertEqual(grid.vue_tagname, 'tailbone-grid')

        # can override with param
        grid = self.make_grid('foo', vue_tagname='something-else')
        self.assertEqual(grid.vue_tagname, 'something-else')

        # can still pass old param
        grid = self.make_grid('foo', component='legacy-name')
        self.assertEqual(grid.vue_tagname, 'legacy-name')

    def test_vue_component(self):

        # default
        grid = self.make_grid('foo')
        self.assertEqual(grid.vue_component, 'TailboneGrid')

        # can override with param
        grid = self.make_grid('foo', vue_tagname='something-else')
        self.assertEqual(grid.vue_component, 'SomethingElse')

        # can still pass old param
        grid = self.make_grid('foo', component='legacy-name')
        self.assertEqual(grid.vue_component, 'LegacyName')

    def test_component(self):

        # default
        grid = self.make_grid('foo')
        self.assertEqual(grid.component, 'tailbone-grid')

        # can override with param
        grid = self.make_grid('foo', vue_tagname='something-else')
        self.assertEqual(grid.component, 'something-else')

        # can still pass old param
        grid = self.make_grid('foo', component='legacy-name')
        self.assertEqual(grid.component, 'legacy-name')

    def test_component_studly(self):

        # default
        grid = self.make_grid('foo')
        self.assertEqual(grid.component_studly, 'TailboneGrid')

        # can override with param
        grid = self.make_grid('foo', vue_tagname='something-else')
        self.assertEqual(grid.component_studly, 'SomethingElse')

        # can still pass old param
        grid = self.make_grid('foo', component='legacy-name')
        self.assertEqual(grid.component_studly, 'LegacyName')

    def test_actions(self):

        # default
        grid = self.make_grid('foo')
        self.assertEqual(grid.actions, [])

        # main actions
        grid = self.make_grid('foo', main_actions=['foo'])
        self.assertEqual(grid.actions, ['foo'])

        # more actions
        grid = self.make_grid('foo', main_actions=['foo'], more_actions=['bar'])
        self.assertEqual(grid.actions, ['foo', 'bar'])

    def test_set_label(self):
        model = self.app.model
        grid = self.make_grid(model_class=model.Setting, filterable=True)
        self.assertEqual(grid.labels, {})

        # basic
        grid.set_label('name', "NAME COL")
        self.assertEqual(grid.labels['name'], "NAME COL")

        # can replace label
        grid.set_label('name', "Different")
        self.assertEqual(grid.labels['name'], "Different")
        self.assertEqual(grid.get_label('name'), "Different")

        # can update only column, not filter
        self.assertEqual(grid.labels, {'name': "Different"})
        self.assertIn('name', grid.filters)
        self.assertEqual(grid.filters['name'].label, "Different")
        grid.set_label('name', "COLUMN ONLY", column_only=True)
        self.assertEqual(grid.get_label('name'), "COLUMN ONLY")
        self.assertEqual(grid.filters['name'].label, "Different")

    def test_get_view_click_handler(self):
        model = self.app.model
        grid = self.make_grid(model_class=model.Setting)

        grid.actions.append(
            mod.GridAction(self.request, 'view',
                           click_handler='clickHandler(props.row)'))

        handler = grid.get_view_click_handler()
        self.assertEqual(handler, 'clickHandler(props.row)')

    def test_set_action_urls(self):
        model = self.app.model
        grid = self.make_grid(model_class=model.Setting)

        grid.actions.append(
            mod.GridAction(self.request, 'view', url='/blarg'))

        setting = {'name': 'foo', 'value': 'bar'}
        grid.set_action_urls(setting, setting, 0)
        self.assertEqual(setting['_action_url_view'], '/blarg')

    def test_default_sortkey(self):
        grid = self.make_grid()
        self.assertEqual(grid.sort_defaults, [])
        self.assertIsNone(grid.default_sortkey)
        grid.default_sortkey = 'name'
        self.assertEqual(grid.sort_defaults, [mod.SortInfo('name', 'asc')])
        self.assertEqual(grid.default_sortkey, 'name')
        grid.default_sortkey = 'value'
        self.assertEqual(grid.sort_defaults, [mod.SortInfo('value', 'asc')])
        self.assertEqual(grid.default_sortkey, 'value')

    def test_default_sortdir(self):
        grid = self.make_grid()
        self.assertEqual(grid.sort_defaults, [])
        self.assertIsNone(grid.default_sortdir)
        self.assertRaises(ValueError, setattr, grid, 'default_sortdir', 'asc')
        grid.sort_defaults = [mod.SortInfo('name', 'asc')]
        grid.default_sortdir = 'desc'
        self.assertEqual(grid.sort_defaults, [mod.SortInfo('name', 'desc')])
        self.assertEqual(grid.default_sortdir, 'desc')

    def test_pageable(self):
        grid = self.make_grid()
        self.assertFalse(grid.paginated)
        grid.pageable = True
        self.assertTrue(grid.paginated)
        grid.paginated = False
        self.assertFalse(grid.pageable)

    def test_get_pagesize_options(self):
        grid = self.make_grid()

        # default
        options = grid.get_pagesize_options()
        self.assertEqual(options, [5, 10, 20, 50, 100, 200])

        # override default
        options = grid.get_pagesize_options(default=[42])
        self.assertEqual(options, [42])

        # from legacy config
        self.config.setdefault('tailbone.grid.pagesize_options', '1 2 3')
        grid = self.make_grid()
        options = grid.get_pagesize_options()
        self.assertEqual(options, [1, 2, 3])

        # from new config
        self.config.setdefault('wuttaweb.grids.default_pagesize_options', '4, 5, 6')
        grid = self.make_grid()
        options = grid.get_pagesize_options()
        self.assertEqual(options, [4, 5, 6])

    def test_get_pagesize(self):
        grid = self.make_grid()

        # default
        size = grid.get_pagesize()
        self.assertEqual(size, 20)

        # override default
        size = grid.get_pagesize(default=42)
        self.assertEqual(size, 42)

        # override default options
        self.config.setdefault('wuttaweb.grids.default_pagesize_options', '10 15 30')
        grid = self.make_grid()
        size = grid.get_pagesize()
        self.assertEqual(size, 10)

        # from legacy config
        self.config.setdefault('tailbone.grid.default_pagesize', '12')
        grid = self.make_grid()
        size = grid.get_pagesize()
        self.assertEqual(size, 12)

        # from new config
        self.config.setdefault('wuttaweb.grids.default_pagesize', '15')
        grid = self.make_grid()
        size = grid.get_pagesize()
        self.assertEqual(size, 15)

    def test_set_sorter(self):
        model = self.app.model
        grid = self.make_grid(model_class=model.Setting,
                              sortable=True, sort_on_backend=True)

        # passing None will remove sorter
        self.assertIn('name', grid.sorters)
        grid.set_sorter('name', None)
        self.assertNotIn('name', grid.sorters)

        # can recreate sorter with just column name
        grid.set_sorter('name')
        self.assertIn('name', grid.sorters)
        grid.remove_sorter('name')
        self.assertNotIn('name', grid.sorters)
        grid.set_sorter('name', 'name')
        self.assertIn('name', grid.sorters)

        # can recreate sorter with model property
        grid.remove_sorter('name')
        self.assertNotIn('name', grid.sorters)
        grid.set_sorter('name', model.Setting.name)
        self.assertIn('name', grid.sorters)

        # extra kwargs are ignored
        grid.remove_sorter('name')
        self.assertNotIn('name', grid.sorters)
        grid.set_sorter('name', model.Setting.name, foo='bar')
        self.assertIn('name', grid.sorters)

        # passing multiple args will invoke make_filter() directly
        grid.remove_sorter('name')
        self.assertNotIn('name', grid.sorters)
        with patch.object(grid, 'make_sorter') as make_sorter:
            make_sorter.return_value = 42
            grid.set_sorter('name', 'foo', 'bar')
            make_sorter.assert_called_once_with('foo', 'bar')
            self.assertEqual(grid.sorters['name'], 42)

    def test_make_simple_sorter(self):
        model = self.app.model
        grid = self.make_grid(model_class=model.Setting,
                              sortable=True, sort_on_backend=True)

        # delegates to grid.make_sorter()
        with patch.object(grid, 'make_sorter') as make_sorter:
            make_sorter.return_value = 42
            sorter = grid.make_simple_sorter('name', foldcase=True)
            make_sorter.assert_called_once_with('name', foldcase=True)
            self.assertEqual(sorter, 42)

    def test_load_settings(self):
        model = self.app.model

        # nb. first use a paging grid
        grid = self.make_grid(key='foo', paginated=True, paginate_on_backend=True,
                              pagesize=20, page=1)

        # settings are loaded, applied, saved
        self.assertEqual(grid.page, 1)
        self.assertNotIn('grid.foo.page', self.request.session)
        self.request.GET = {'pagesize': '10', 'page': '2'}
        grid.load_settings()
        self.assertEqual(grid.page, 2)
        self.assertEqual(self.request.session['grid.foo.page'], 2)

        # can skip the saving step
        self.request.GET = {'pagesize': '10', 'page': '3'}
        grid.load_settings(store=False)
        self.assertEqual(grid.page, 3)
        self.assertEqual(self.request.session['grid.foo.page'], 2)

        # no error for non-paginated grid
        grid = self.make_grid(key='foo', paginated=False)
        grid.load_settings()
        self.assertFalse(grid.paginated)

        # nb. next use a sorting grid
        grid = self.make_grid(key='settings', model_class=model.Setting,
                              sortable=True, sort_on_backend=True)

        # settings are loaded, applied, saved
        self.assertEqual(grid.sort_defaults, [])
        self.assertIsNone(grid.active_sorters)
        self.request.GET = {'sort1key': 'name', 'sort1dir': 'desc'}
        grid.load_settings()
        self.assertEqual(grid.active_sorters, [{'key': 'name', 'dir': 'desc'}])
        self.assertEqual(self.request.session['grid.settings.sorters.length'], 1)
        self.assertEqual(self.request.session['grid.settings.sorters.1.key'], 'name')
        self.assertEqual(self.request.session['grid.settings.sorters.1.dir'], 'desc')

        # can skip the saving step
        self.request.GET = {'sort1key': 'name', 'sort1dir': 'asc'}
        grid.load_settings(store=False)
        self.assertEqual(grid.active_sorters, [{'key': 'name', 'dir': 'asc'}])
        self.assertEqual(self.request.session['grid.settings.sorters.length'], 1)
        self.assertEqual(self.request.session['grid.settings.sorters.1.key'], 'name')
        self.assertEqual(self.request.session['grid.settings.sorters.1.dir'], 'desc')

        # no error for non-sortable grid
        grid = self.make_grid(key='foo', sortable=False)
        grid.load_settings()
        self.assertFalse(grid.sortable)

        # with sort defaults
        grid = self.make_grid(model_class=model.Setting, sortable=True,
                              sort_on_backend=True, sort_defaults='name')
        self.assertIsNone(grid.active_sorters)
        grid.load_settings()
        self.assertEqual(grid.active_sorters, [{'key': 'name', 'dir': 'asc'}])

        # with multi-column sort defaults
        grid = self.make_grid(model_class=model.Setting, sortable=True,
                              sort_on_backend=True)
        grid.sort_defaults = [
            mod.SortInfo('name', 'asc'),
            mod.SortInfo('value', 'desc'),
        ]
        self.assertIsNone(grid.active_sorters)
        grid.load_settings()
        self.assertEqual(grid.active_sorters, [{'key': 'name', 'dir': 'asc'}])

        # load settings from session when nothing is in request
        self.request.GET = {}
        self.request.session.invalidate()
        self.assertNotIn('grid.settings.sorters.length', self.request.session)
        self.request.session['grid.settings.sorters.length'] = 1
        self.request.session['grid.settings.sorters.1.key'] = 'name'
        self.request.session['grid.settings.sorters.1.dir'] = 'desc'
        grid = self.make_grid(key='settings', model_class=model.Setting,
                              sortable=True, sort_on_backend=True,
                              paginated=True, paginate_on_backend=True)
        self.assertIsNone(grid.active_sorters)
        grid.load_settings()
        self.assertEqual(grid.active_sorters, [{'key': 'name', 'dir': 'desc'}])

    def test_persist_settings(self):
        model = self.app.model

        # nb. start out with paginated-only grid
        grid = self.make_grid(key='foo', paginated=True, paginate_on_backend=True)

        # invalid dest
        self.assertRaises(ValueError, grid.persist_settings, {}, dest='doesnotexist')

        # nb. no error if empty settings, but it saves null values
        grid.persist_settings({}, dest='session')
        self.assertIsNone(self.request.session['grid.foo.page'])

        # provided values are saved
        grid.persist_settings({'pagesize': 15, 'page': 3}, dest='session')
        self.assertEqual(self.request.session['grid.foo.page'], 3)

        # nb. now switch to sortable-only grid
        grid = self.make_grid(key='settings', model_class=model.Setting,
                              sortable=True, sort_on_backend=True)

        # no error if empty settings; does not save values
        grid.persist_settings({}, dest='session')
        self.assertNotIn('grid.settings.sorters.length', self.request.session)

        # provided values are saved
        grid.persist_settings({'sorters.length': 2,
                               'sorters.1.key': 'name',
                               'sorters.1.dir': 'desc',
                               'sorters.2.key': 'value',
                               'sorters.2.dir': 'asc'},
                              dest='session')
        self.assertEqual(self.request.session['grid.settings.sorters.length'], 2)
        self.assertEqual(self.request.session['grid.settings.sorters.1.key'], 'name')
        self.assertEqual(self.request.session['grid.settings.sorters.1.dir'], 'desc')
        self.assertEqual(self.request.session['grid.settings.sorters.2.key'], 'value')
        self.assertEqual(self.request.session['grid.settings.sorters.2.dir'], 'asc')

        # old values removed when new are saved
        grid.persist_settings({'sorters.length': 1,
                               'sorters.1.key': 'name',
                               'sorters.1.dir': 'desc'},
                              dest='session')
        self.assertEqual(self.request.session['grid.settings.sorters.length'], 1)
        self.assertEqual(self.request.session['grid.settings.sorters.1.key'], 'name')
        self.assertEqual(self.request.session['grid.settings.sorters.1.dir'], 'desc')
        self.assertNotIn('grid.settings.sorters.2.key', self.request.session)
        self.assertNotIn('grid.settings.sorters.2.dir', self.request.session)

    def test_sort_data(self):
        model = self.app.model
        sample_data = [
            {'name': 'foo1', 'value': 'ONE'},
            {'name': 'foo2', 'value': 'two'},
            {'name': 'foo3', 'value': 'ggg'},
            {'name': 'foo4', 'value': 'ggg'},
            {'name': 'foo5', 'value': 'ggg'},
            {'name': 'foo6', 'value': 'six'},
            {'name': 'foo7', 'value': 'seven'},
            {'name': 'foo8', 'value': 'eight'},
            {'name': 'foo9', 'value': 'nine'},
        ]
        for setting in sample_data:
            self.app.save_setting(self.session, setting['name'], setting['value'])
        self.session.commit()
        sample_query = self.session.query(model.Setting)

        grid = self.make_grid(model_class=model.Setting,
                              sortable=True, sort_on_backend=True,
                              sort_defaults=('name', 'desc'))
        grid.load_settings()

        # can sort a simple list of data
        sorted_data = grid.sort_data(sample_data)
        self.assertIsInstance(sorted_data, list)
        self.assertEqual(len(sorted_data), 9)
        self.assertEqual(sorted_data[0]['name'], 'foo9')
        self.assertEqual(sorted_data[-1]['name'], 'foo1')

        # can also sort a data query
        sorted_query = grid.sort_data(sample_query)
        self.assertIsInstance(sorted_query, orm.Query)
        sorted_data = sorted_query.all()
        self.assertEqual(len(sorted_data), 9)
        self.assertEqual(sorted_data[0]['name'], 'foo9')
        self.assertEqual(sorted_data[-1]['name'], 'foo1')

        # cannot sort data if sorter missing in overrides
        sorted_data = grid.sort_data(sample_data, sorters=[])
        # nb. sorted data is in same order as original sample (not sorted)
        self.assertEqual(sorted_data[0]['name'], 'foo1')
        self.assertEqual(sorted_data[-1]['name'], 'foo9')

        # multi-column sorting for list data
        sorted_data = grid.sort_data(sample_data, sorters=[{'key': 'value', 'dir': 'asc'},
                                                           {'key': 'name', 'dir': 'asc'}])
        self.assertEqual(dict(sorted_data[0]), {'name': 'foo8', 'value': 'eight'})
        self.assertEqual(dict(sorted_data[1]), {'name': 'foo3', 'value': 'ggg'})
        self.assertEqual(dict(sorted_data[3]), {'name': 'foo5', 'value': 'ggg'})
        self.assertEqual(dict(sorted_data[-1]), {'name': 'foo2', 'value': 'two'})

        # multi-column sorting for query
        sorted_query = grid.sort_data(sample_query, sorters=[{'key': 'value', 'dir': 'asc'},
                                                             {'key': 'name', 'dir': 'asc'}])
        self.assertEqual(dict(sorted_data[0]), {'name': 'foo8', 'value': 'eight'})
        self.assertEqual(dict(sorted_data[1]), {'name': 'foo3', 'value': 'ggg'})
        self.assertEqual(dict(sorted_data[3]), {'name': 'foo5', 'value': 'ggg'})
        self.assertEqual(dict(sorted_data[-1]), {'name': 'foo2', 'value': 'two'})

        # cannot sort data if sortfunc is missing for column
        grid.remove_sorter('name')
        sorted_data = grid.sort_data(sample_data, sorters=[{'key': 'value', 'dir': 'asc'},
                                                           {'key': 'name', 'dir': 'asc'}])
        # nb. sorted data is in same order as original sample (not sorted)
        self.assertEqual(sorted_data[0]['name'], 'foo1')
        self.assertEqual(sorted_data[-1]['name'], 'foo9')

    def test_render_vue_tag(self):
        model = self.app.model

        # standard
        grid = self.make_grid('settings', model_class=model.Setting)
        html = grid.render_vue_tag()
        self.assertIn('<tailbone-grid', html)
        self.assertNotIn('@deleteActionClicked', html)

        # with delete hook
        master = MagicMock(deletable=True, delete_confirm='simple')
        master.has_perm.return_value = True
        grid = self.make_grid('settings', model_class=model.Setting)
        html = grid.render_vue_tag(master=master)
        self.assertIn('<tailbone-grid', html)
        self.assertIn('@deleteActionClicked', html)

    def test_render_vue_template(self):
        # self.pyramid_config.include('tailbone.views.common')
        model = self.app.model

        # sanity check
        grid = self.make_grid('settings', model_class=model.Setting)
        html = grid.render_vue_template(session=self.session)
        self.assertIn('<b-table', html)

    def test_get_vue_columns(self):
        model = self.app.model

        # sanity check
        grid = self.make_grid('settings', model_class=model.Setting, sortable=True)
        columns = grid.get_vue_columns()
        self.assertEqual(len(columns), 2)
        self.assertEqual(columns[0]['field'], 'name')
        self.assertTrue(columns[0]['sortable'])
        self.assertEqual(columns[1]['field'], 'value')
        self.assertTrue(columns[1]['sortable'])

    def test_get_vue_data(self):
        model = self.app.model

        # sanity check
        grid = self.make_grid('settings', model_class=model.Setting)
        data = grid.get_vue_data()
        self.assertEqual(data, [])

        # calling again returns same data
        data2 = grid.get_vue_data()
        self.assertIs(data2, data)


class TestGridAction(WebTestCase):

    def test_constructor(self):

        # null by default
        action = mod.GridAction(self.request, 'view')
        self.assertIsNone(action.target)
        self.assertIsNone(action.click_handler)

        # but can set them
        action = mod.GridAction(self.request, 'view',
                                target='_blank',
                                click_handler='doSomething(props.row)')
        self.assertEqual(action.target, '_blank')
        self.assertEqual(action.click_handler, 'doSomething(props.row)')
