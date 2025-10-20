
# Changelog
All notable changes to Tailbone will be documented in this file.

The format is based on [Keep a Changelog](http://keepachangelog.com/en/1.0.0/)
and this project adheres to [Semantic Versioning](http://semver.org/spec/v2.0.0.html).

## v0.23.0 (2025-10-19)

### Feat

- require latest rattail; drop passlib dependency

### Fix

- depend on latest rattail

## v0.22.11 (2025-09-20)

### Fix

- avoid error when row object missing field

## v0.22.10 (2025-09-20)

### Fix

- avoid error if 'default' theme not included
- fix config extension entry point

## v0.22.9 (2025-09-20)

### Fix

- small bugfixes per upstream changes

## v0.22.8 (2025-05-20)

### Fix

- add startup hack for tempmon DB model

## v0.22.7 (2025-02-19)

### Fix

- stop using old config for logo image url on login page
- fix warning msg for deprecated Grid param

## v0.22.6 (2025-02-01)

### Fix

- register vue3 form component for products -> make batch

## v0.22.5 (2024-12-16)

### Fix

- whoops this is latest rattail
- require newer rattail lib
- require newer wuttaweb
- let caller request safe HTML literal for rendered grid table

## v0.22.4 (2024-11-22)

### Fix

- avoid error in product search for duplicated key
- use vmodel for confirm password widget input

## v0.22.3 (2024-11-19)

### Fix

- avoid error for trainwreck query when not a customer

## v0.22.2 (2024-11-18)

### Fix

- use local/custom enum for continuum operations
- add basic master view for Product Costs
- show continuum operation type when viewing version history
- always define `app` attr for ViewSupplement
- avoid deprecated import

## v0.22.1 (2024-11-02)

### Fix

- fix submit button for running problem report
- avoid deprecated grid method

## v0.22.0 (2024-10-22)

### Feat

- add support for new ordering batch from parsed file

### Fix

- avoid deprecated method to suggest username

## v0.21.11 (2024-10-03)

### Fix

- custom method for adding grid action
- become/stop root should redirect to previous url

## v0.21.10 (2024-09-15)

### Fix

- update project repo links, kallithea -> forgejo
- use better icon for submit button on login page
- wrap notes text for batch view
- expose datasync consumer batch size via configure page

## v0.21.9 (2024-08-28)

### Fix

- render custom attrs in form component tag

## v0.21.8 (2024-08-28)

### Fix

- ignore session kwarg for `MasterView.make_row_grid()`

## v0.21.7 (2024-08-28)

### Fix

- avoid error when form value cannot be obtained

## v0.21.6 (2024-08-28)

### Fix

- avoid error when grid value cannot be obtained

## v0.21.5 (2024-08-28)

### Fix

- set empty string for "-new-" file configure option

## v0.21.4 (2024-08-26)

### Fix

- handle differing email profile keys for appinfo/configure

## v0.21.3 (2024-08-26)

### Fix

- show non-standard config values for app info configure email

## v0.21.2 (2024-08-26)

### Fix

- refactor waterpark base template to use wutta feedback component
- fix input/output file upload feature for configure pages, per oruga
- tweak how grid data translates to Vue template context
- merge filters into main grid template
- add basic wutta view for users
- some fixes for wutta people view
- various fixes for waterpark theme
- avoid deprecated `component` form kwarg

## v0.21.1 (2024-08-22)

### Fix

- misc. bugfixes per recent changes

## v0.21.0 (2024-08-22)

### Feat

- move "most" filtering logic for grid class to wuttaweb
- inherit from wuttaweb templates for home, login pages
- inherit from wuttaweb for AppInfoView, appinfo/configure template
- add "has output file templates" config option for master view

### Fix

- change grid reset-view param name to match wuttaweb
- move "searchable columns" grid feature to wuttaweb
- use wuttaweb to get/render csrf token
- inherit from wuttaweb for appinfo/index template
- prefer wuttaweb config for "home redirect to login" feature
- fix master/index template rendering for waterpark theme
- fix spacing for navbar logo/title in waterpark theme

## v0.20.1 (2024-08-20)

### Fix

- fix default filter verbs logic for workorder status

## v0.20.0 (2024-08-20)

### Feat

- add new 'waterpark' theme, based on wuttaweb w/ vue2 + buefy
- refactor templates to simplify base/page/form structure

### Fix

- avoid deprecated reference to app db engine

## v0.19.3 (2024-08-19)

### Fix

- add pager stats to all grid vue data (fixes view history)

## v0.19.2 (2024-08-19)

### Fix

- sort on frontend for appinfo package listing grid
- prefer attr over key lookup when getting model values
- replace all occurrences of `component_studly` => `vue_component`

## v0.19.1 (2024-08-19)

### Fix

- fix broken user auth for web API app

## v0.19.0 (2024-08-18)

### Feat

- move multi-column grid sorting logic to wuttaweb
- move single-column grid sorting logic to wuttaweb

### Fix

- fix misc. errors in grid template per wuttaweb
- fix broken permission directives in web api startup

## v0.18.0 (2024-08-16)

### Feat

- move "basic" grid pagination logic to wuttaweb
- inherit from wutta base class for Grid
- inherit most logic from wuttaweb, for GridAction

### Fix

- avoid route error in user view, when using wutta people view
- fix some more wutta compat for base template

## v0.17.0 (2024-08-15)

### Feat

- use wuttaweb for `get_liburl()` logic

## v0.16.1 (2024-08-15)

### Fix

- improve wutta People view a bit
- update references to `get_class_hierarchy()`
- tweak template for `people/view_profile` per wutta compat

## v0.16.0 (2024-08-15)

### Feat

- add first wutta-based master, for PersonView
- refactor forms/grids/views/templates per wuttaweb compat

## v0.15.6 (2024-08-13)

### Fix

- avoid `before_render` subscriber hook for web API
- simplify verbiage for batch execution panel

## v0.15.5 (2024-08-09)

### Fix

- assign convenience attrs for all views (config, app, enum, model)

## v0.15.4 (2024-08-09)

### Fix

- avoid bug when checking current theme

## v0.15.3 (2024-08-08)

### Fix

- fix timepicker `parseTime()` when value is null

## v0.15.2 (2024-08-06)

### Fix

- use auth handler, avoid legacy calls for role/perm checks

## v0.15.1 (2024-08-05)

### Fix

- move magic `b` template context var to wuttaweb

## v0.15.0 (2024-08-05)

### Feat

- move more subscriber logic to wuttaweb

### Fix

- use wuttaweb logic for `util.get_form_data()`

## v0.14.5 (2024-08-03)

### Fix

- use auth handler instead of deprecated auth functions
- avoid duplicate `partial` param when grid reloads data

## v0.14.4 (2024-07-18)

### Fix

- fix more settings persistence bug(s) for datasync/configure
- fix modals for luigi tasks page, per oruga

## v0.14.3 (2024-07-17)

### Fix

- fix auto-collapse title for viewing trainwreck txn
- allow auto-collapse of header when viewing trainwreck txn

## v0.14.2 (2024-07-15)

### Fix

- add null menu handler, for use with API apps

## v0.14.1 (2024-07-14)

### Fix

- update usage of auth handler, per rattail changes
- fix model reference in menu handler
- fix bug when making "integration" menus

## v0.14.0 (2024-07-14)

### Feat

- move core menu logic to wuttaweb

## v0.13.2 (2024-07-13)

### Fix

- fix logic bug for datasync/config settings save

## v0.13.1 (2024-07-13)

### Fix

- fix settings persistence bug(s) for datasync/configure page

## v0.13.0 (2024-07-12)

### Feat

- begin integrating WuttaWeb as upstream dependency

### Fix

- cast enum as list to satisfy deform widget

## v0.12.1 (2024-07-11)

### Fix

- refactor `config.get_model()` => `app.model`

## v0.12.0 (2024-07-09)

### Feat

- drop python 3.6 support, use pyproject.toml (again)

## v0.11.10 (2024-07-05)

### Fix

- make the Members tab optional, for profile view

## v0.11.9 (2024-07-05)

### Fix

- do not show flash message when changing app theme

- improve collapse panels for butterball theme

- expand input for butterball theme

- add xref button to customer profile, for trainwreck txn view

- add optional Transactions tab for profile view

## v0.11.8 (2024-07-04)

### Fix

- fix grid action icons for datasync/configure, per oruga

- allow view supplements to add extra links for profile employee tab

- leverage import handler method to determine command/subcommand

- add tool to make user account from profile view

## v0.11.7 (2024-07-04)

### Fix

- add stacklevel to deprecation warnings

- require zope.sqlalchemy >= 1.5

- include edit profile email/phone dialogs only if user has perms

- allow view supplements to add to profile member context

- cast enum as list to satisfy deform widget

- expand POD image URL setting input

## v0.11.6 (2024-07-01)

### Fix

- set explicit referrer when changing dbkey

- remove references, dependency for `six` package

## v0.11.5 (2024-06-30)

### Fix

- allow comma in numeric filter input

- add custom url prefix if needed, for fanstatic

- use vue 3.4.31 and oruga 0.8.12 by default

## v0.11.4 (2024-06-30)

### Fix

- start/stop being root should submit POST instead of GET

- require vendor when making new ordering batch via api

- don't escape each address for email attempts grid

## v0.11.3 (2024-06-28)

### Fix

- add link to "resolved by" user for pending products

- handle error when merging 2 records fails

## v0.11.2 (2024-06-18)

### Fix

- hide certain custorder settings if not applicable

- use different logic for buefy/oruga for product lookup keydown

- product records should be touchable

- show flash error message if resolve pending product fails

## v0.11.1 (2024-06-14)

### Fix

- revert back to setup.py + setup.cfg

## v0.11.0 (2024-06-10)

### Feat

- switch from setup.cfg to pyproject.toml + hatchling

## v0.10.16 (2024-06-10)

### Feat

- standardize how app, package versions are determined

### Fix

- avoid deprecated config methods for app/node title

## v0.10.15 (2024-06-07)

### Fix

- do *not* Use `pkg_resources` to determine package versions

## v0.10.14 (2024-06-06)

### Fix

- use `pkg_resources` to determine package versions

## v0.10.13 (2024-06-06)

### Feat

- remove old/unused scaffold for use with `pcreate`

- add 'fanstatic' support for sake of libcache assets

## v0.10.12 (2024-06-04)

### Feat

- require pyramid 2.x; remove 1.x-style auth policies

- remove version cap for deform

- set explicit referrer when changing app theme

- add `<b-tooltip>` component shim

- include extra styles from `base_meta` template for butterball

- include butterball theme by default for new apps

### Fix

- fix product lookup component, per butterball

## v0.10.11 (2024-06-03)

### Feat

- fix vue3 refresh bugs for various views

- fix grid bug for tempmon appliance view, per oruga

- fix ordering worksheet generator, per butterball

- fix inventory worksheet generator, per butterball

## v0.10.10 (2024-06-03)

### Feat

- more butterball fixes for "view profile" template

### Fix

- fix focus for `<b-select>` shim component

## v0.10.9 (2024-06-03)

### Feat

- let master view control context menu items for page

- fix the "new custorder" page for butterball

### Fix

- fix panel style for PO vs. Invoice breakdown in receiving batch

## v0.10.8 (2024-06-02)

### Feat

- add styling for checked grid rows, per oruga/butterball

- fix product view template for oruga/butterball

- allow per-user custom styles for butterball

- use oruga 0.8.9 by default

## v0.10.7 (2024-06-01)

### Feat

- add setting to allow decimal quantities for receiving

- log error if registry has no rattail config

- add column filters for import/export main grid

- escape all unsafe html for grid data

- add speedbumps for delete, set preferred email/phone in profile view

- fix file upload widget for oruga

### Fix

- fix overflow when instance header title is too long (butterball)

## v0.10.6 (2024-05-29)

### Feat

- add way to flag organic products within lookup dialog

- expose db picker for butterball theme

- expose quickie lookup for butterball theme

- fix basic problems with people profile view, per butterball

## v0.10.5 (2024-05-29)

### Feat

- add `<tailbone-timepicker>` component for oruga

## v0.10.4 (2024-05-12)

### Fix

- fix styles for grid actions, per butterball

## v0.10.3 (2024-05-10)

### Fix

- fix bug with grid date filters

## v0.10.2 (2024-05-08)

### Feat

- remove version restriction for pyramid_beaker dependency

- rename some attrs etc. for buefy components used with oruga

- fix "tools" helper for receiving batch view, per oruga

- more data type fixes for ``<tailbone-datepicker>``

- fix "view receiving row" page, per oruga

- tweak styles for grid action links, per butterball

### Fix

- fix employees grid when viewing department (per oruga)

- fix login "enter" key behavior, per oruga

- fix button text for autocomplete

## v0.10.1 (2024-04-28)

### Feat

- sort list of available themes

- update various icon names for oruga compatibility

- show "View This" button when cloning a record

- stop including 'falafel' as available theme

### Fix

- fix vertical alignment in main menu bar, for butterball

- fix upgrade execution logic/UI per oruga

## v0.10.0 (2024-04-28)

This version bump is to reflect adding support for Vue 3 + Oruga via
the 'butterball' theme.  There is likely more work to be done for that
yet, but it mostly works at this point.

### Feat

- misc. template and view logic tweaks (applicable to all themes) for
  better patterns, consistency etc.

- add initial support for Vue 3 + Oruga, via "butterball" theme


## Older Releases

Please see `docs/OLDCHANGES.rst` for older release notes.
