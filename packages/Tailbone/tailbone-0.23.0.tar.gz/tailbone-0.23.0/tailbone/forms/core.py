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
Forms Core
"""

import hashlib
import json
import logging
import warnings
from collections import OrderedDict

import sqlalchemy as sa
from sqlalchemy import orm
from sqlalchemy.ext.associationproxy import AssociationProxy, ASSOCIATION_PROXY
from wuttjamaican.util import UNSPECIFIED

from rattail.util import pretty_boolean
from rattail.db.util import get_fieldnames

import colander
import deform
from colanderalchemy import SQLAlchemySchemaNode
from colanderalchemy.schema import _creation_order
from deform import widget as dfwidget
from pyramid_deform import SessionFileUploadTempStore
from pyramid.renderers import render
from webhelpers2.html import tags, HTML

from wuttaweb.util import FieldList, get_form_data, make_json_safe

from tailbone.db import Session
from tailbone.util import raw_datetime, render_markdown
from tailbone.forms import types
from tailbone.forms.widgets import (ReadonlyWidget, PlainDateWidget,
                                    JQueryDateWidget, JQueryTimeWidget,
                                    FileUploadWidget, MultiFileUploadWidget)
from tailbone.exceptions import TailboneJSONFieldError


log = logging.getLogger(__name__)


def get_association_proxy(mapper, field):
    """
    Returns the association proxy corresponding to the given field name if one
    exists, or ``None``.
    """
    try:
        desc = getattr(mapper.all_orm_descriptors, field)
    except AttributeError:
        pass
    else:
        if desc.extension_type == ASSOCIATION_PROXY:
            return desc


def get_association_proxy_target(inspector, field):
    """
    Returns the property on the main class, which represents the "target"
    for the given association proxy field name.  Typically this will refer
    to the "extension" model class.
    """
    proxy = get_association_proxy(inspector, field)
    if proxy:
        proxy_target = inspector.get_property(proxy.target_collection)
        if isinstance(proxy_target, orm.RelationshipProperty) and not proxy_target.uselist:
            return proxy_target


def get_association_proxy_column(inspector, field):
    """
    Returns the property on the proxy target class, for the column which is
    reflected by the proxy.
    """
    proxy_target = get_association_proxy_target(inspector, field)
    if proxy_target:
        if proxy_target.mapper.has_property(field):
            prop = proxy_target.mapper.get_property(field)
            if isinstance(prop, orm.ColumnProperty) and isinstance(prop.columns[0], sa.Column):
                return prop


class CustomSchemaNode(SQLAlchemySchemaNode):

    def association_proxy(self, field):
        """
        Returns the association proxy corresponding to the given field name if
        one exists, or ``None``.
        """
        return get_association_proxy(self.inspector, field)

    def association_proxy_target(self, field):
        """
        Returns the property on the main class, which represents the "target"
        for the given association proxy field name.  Typically this will refer
        to the "extension" model class.
        """
        return get_association_proxy_target(self.inspector, field)

    def association_proxy_column(self, field):
        """
        Returns the property on the proxy target class, for the column which is
        reflected by the proxy.
        """
        return get_association_proxy_column(self.inspector, field)

    def supported_association_proxy(self, field):
        """
        Returns boolean indicating whether the association proxy corresponding
        to the given field name, is "supported" with typical logic.
        """
        if not self.association_proxy_column(field):
            return False
        return True

    def add_nodes(self, includes, excludes, overrides):
        """
        Add all automatic nodes to the schema.

        .. note::
           This method was copied from upstream and modified to add automatic
           handling of "association proxy" fields.
        """
        if set(excludes) & set(includes):
            msg = 'excludes and includes are mutually exclusive.'
            raise ValueError(msg)

        # sorted to maintain the order in which the attributes
        # are defined
        properties = sorted(self.inspector.attrs, key=_creation_order)
        if excludes:
            if includes:
                raise ValueError("Must pass includes *or* excludes, but not both")
            supported = [prop.key for prop in properties
                         if prop.key not in excludes]
        elif includes:
            supported = includes
        elif includes is not None:
            supported = []

        for name in supported:
            prop = self.inspector.attrs.get(name, name)

            if name in excludes or (includes and name not in includes):
                log.debug('Attribute %s skipped imperatively', name)
                continue

            name_overrides_copy = overrides.get(name, {}).copy()

            if (isinstance(prop, orm.ColumnProperty)
                    and isinstance(prop.columns[0], sa.Column)):
                node = self.get_schema_from_column(
                    prop,
                    name_overrides_copy
                )
            elif isinstance(prop, orm.RelationshipProperty):
                if prop.mapper.class_ in self.parents_ and name not in includes:
                    continue
                node = self.get_schema_from_relationship(
                    prop,
                    name_overrides_copy
                )
            elif isinstance(prop, colander.SchemaNode):
                node = prop
            else:

                # magic for association proxy fields
                column = self.association_proxy_column(name)
                if column:
                    node = self.get_schema_from_column(column, name_overrides_copy)

                else:
                    log.debug(
                        'Attribute %s skipped due to not being '
                        'a ColumnProperty or RelationshipProperty',
                        name
                    )
                    continue

            if node is not None:
                self.add(node)

    def get_schema_from_relationship(self, prop, overrides):
        """ Build and return a :class:`colander.SchemaNode` for a relationship.
        """

        # for some reason ColanderAlchemy wants to crawl our entire ORM by
        # default, by way of relationships.  this 'excludes' hack is used to
        # prevent that, by forcing skip of 2nd-level relationships

        excludes = []
        if isinstance(prop, orm.RelationshipProperty):
            for next_prop in prop.mapper.iterate_properties:

                # don't include secondary relationships
                if isinstance(next_prop, orm.RelationshipProperty):
                    excludes.append(next_prop.key)

                # don't include fields of binary type
                elif isinstance(next_prop, orm.ColumnProperty):
                    for column in next_prop.columns:
                        if isinstance(column.type, sa.LargeBinary):
                            excludes.append(next_prop.key)

        if excludes:
            overrides['excludes'] = excludes

        return super().get_schema_from_relationship(prop, overrides)

    def dictify(self, obj):
        """ Return a dictified version of `obj` using schema information.

        .. note::
           This method was copied from upstream and modified to add automatic
           handling of "association proxy" fields.
        """
        dict_ = super().dictify(obj)
        for node in self:

            name = node.name
            if name not in dict_:
                # we're only processing association proxy fields here
                if not self.supported_association_proxy(name):
                    continue

                value = getattr(obj, name)
                if value is None:
                    if isinstance(node.typ, colander.String):
                        # colander has an issue with `None` on a String type
                        #  where it translates it into "None".  Let's check
                        #  for that specific case and turn it into a
                        #  `colander.null`.
                        dict_[name] = colander.null
                    else:
                        # A specific case this helps is with Integer where
                        #  `None` is an invalid value.  We call serialize()
                        #  to test if we have a value that will work later
                        #  for serialization and then allow it if it doesn't
                        #  raise an exception.  Hopefully this also catches
                        #  issues with user defined types and future issues.
                        try:
                            node.serialize(value)
                        except:
                            dict_[name] = colander.null
                        else:
                            dict_[name] = value
                else:
                    dict_[name] = value

        return dict_

    def objectify(self, dict_, context=None):
        """ Return an object representing ``dict_`` using schema information.

        .. note::
           This method was copied from upstream and modified to add automatic
           handling of "association proxy" fields.
        """
        mapper = self.inspector
        context = mapper.class_() if context is None else context
        for attr in dict_:
            if mapper.has_property(attr):
                prop = mapper.get_property(attr)
                if hasattr(prop, 'mapper'):
                    cls = prop.mapper.class_
                    if prop.uselist:
                        # Sequence of objects
                        value = [self[attr].children[0].objectify(obj)
                                 for obj in dict_[attr]]
                    else:
                        # Single object
                        value = self[attr].objectify(dict_[attr])
                else:
                     value = dict_[attr]
                     if value is colander.null:
                         # `colander.null` is never an appropriate
                         #  value to be placed on an SQLAlchemy object
                         #  so we translate it into `None`.
                         value = None
                setattr(context, attr, value)

            else:

                # try to process association proxy field
                if self.supported_association_proxy(attr):
                    value = dict_[attr]
                    if value is colander.null:
                        # `colander.null` is never an appropriate
                        #  value to be placed on an SQLAlchemy object
                        #  so we translate it into `None`.
                        value = None
                    setattr(context, attr, value)

                else:
                    # Ignore attributes if they are not mapped
                    log.debug(
                        'SQLAlchemySchemaNode.objectify: %s not found on '
                        '%s. This property has been ignored.',
                        attr, self
                    )
                    continue

        return context


class Form(object):
    """
    Base class for all forms.
    """
    save_label = "Submit"
    update_label = "Save"
    show_cancel = True
    auto_disable = True
    auto_disable_save = True
    auto_disable_cancel = True

    def __init__(self, fields=None, schema=None, request=None, readonly=False, readonly_fields=[],
                 model_instance=None, model_class=None, appstruct=UNSPECIFIED, nodes={}, enums={}, labels={},
                 assume_local_times=False, renderers=None, renderer_kwargs={},
                 hidden={}, widgets={}, defaults={}, validators={}, required={}, helptext={}, focus_spec=None,
                 action_url=None, cancel_url=None,
                 vue_tagname=None,
                 vuejs_component_kwargs=None, vuejs_field_converters={}, json_data={}, included_templates={},
                 # TODO: ugh this is getting out hand!
                 can_edit_help=False, edit_help_url=None, route_prefix=None,
                 **kwargs
    ):
        self.fields = None
        if fields is not None:
            self.set_fields(fields)
        self.schema = schema
        if self.fields is None and self.schema:
            self.set_fields([f.name for f in self.schema])
        self.grouping = None
        self.request = request
        self.readonly = readonly
        self.readonly_fields = set(readonly_fields or [])
        self.model_instance = model_instance
        self.model_class = model_class
        if self.model_instance and not self.model_class and not isinstance(self.model_instance, dict):
            self.model_class = type(self.model_instance)
        if self.model_class and self.fields is None:
            self.set_fields(self.make_fields())
        self.appstruct = appstruct
        self.nodes = nodes or {}
        self.enums = enums or {}
        self.labels = labels or {}
        self.assume_local_times = assume_local_times
        if renderers is None and self.model_class:
            self.renderers = self.make_renderers()
        else:
            self.renderers = renderers or {}
        self.renderer_kwargs = renderer_kwargs or {}
        self.hidden = hidden or {}
        self.widgets = widgets or {}
        self.defaults = defaults or {}
        self.validators = validators or {}
        self.required = required or {}
        self.helptext = helptext or {}
        self.dynamic_helptext = {}
        self.focus_spec = focus_spec
        self.action_url = action_url
        self.cancel_url = cancel_url

        # vue_tagname
        self.vue_tagname = vue_tagname
        if not self.vue_tagname and kwargs.get('component'):
            warnings.warn("component kwarg is deprecated for Form(); "
                          "please use vue_tagname param instead",
                          DeprecationWarning, stacklevel=2)
            self.vue_tagname = kwargs['component']
        if not self.vue_tagname:
            self.vue_tagname = 'tailbone-form'

        self.vuejs_component_kwargs = vuejs_component_kwargs or {}
        self.vuejs_field_converters = vuejs_field_converters or {}
        self.json_data = json_data or {}
        self.included_templates = included_templates or {}
        self.can_edit_help = can_edit_help
        self.edit_help_url = edit_help_url
        self.route_prefix = route_prefix

        self.button_icon_submit = kwargs.get('button_icon_submit', 'save')

    def __iter__(self):
        return iter(self.fields)

    @property
    def vue_component(self):
        """
        String name for the Vue component, e.g. ``'TailboneGrid'``.

        This is a generated value based on :attr:`vue_tagname`.
        """
        words = self.vue_tagname.split('-')
        return ''.join([word.capitalize() for word in words])

    @property
    def component(self):
        """
        DEPRECATED - use :attr:`vue_tagname` instead.
        """
        warnings.warn("Form.component is deprecated; "
                      "please use vue_tagname instead",
                      DeprecationWarning, stacklevel=2)
        return self.vue_tagname

    @property
    def component_studly(self):
        """
        DEPRECATED - use :attr:`vue_component` instead.
        """
        warnings.warn("Form.component_studly is deprecated; "
                      "please use vue_component instead",
                      DeprecationWarning, stacklevel=2)
        return self.vue_component

    def get_button_label_submit(self):
        """ """
        if hasattr(self, '_button_label_submit'):
            return self._button_label_submit

        label = getattr(self, 'submit_label', None)
        if label:
            return label

        return self.save_label

    def set_button_label_submit(self, value):
        """ """
        self._button_label_submit = value

    # wutta compat
    button_label_submit = property(get_button_label_submit,
                                   set_button_label_submit)

    def __contains__(self, item):
        return item in self.fields

    def set_fields(self, fields):
        self.fields = FieldList(fields)

    def make_fields(self):
        """
        Return a default list of fields, based on :attr:`model_class`.
        """
        if not self.model_class:
            raise ValueError("Must define model_class to use make_fields()")

        return get_fieldnames(self.request.rattail_config, self.model_class,
                              columns=True, proxies=True, relations=True)

    def set_grouping(self, items):
        self.grouping = OrderedDict(items)

    def make_renderers(self):
        """
        Return a default set of field renderers, based on :attr:`model_class`.
        """
        if not self.model_class:
            raise ValueError("Must define model_class to use make_renderers()")

        inspector = sa.inspect(self.model_class)
        renderers = {}

        # TODO: clearly this should be leaner...

        # first look at regular column fields
        for prop in inspector.iterate_properties:
            if isinstance(prop, orm.ColumnProperty):
                if len(prop.columns) == 1:
                    column = prop.columns[0]
                    if isinstance(column.type, sa.DateTime):
                        if self.assume_local_times:
                            renderers[prop.key] = self.render_datetime_local
                        else:
                            renderers[prop.key] = self.render_datetime
                    elif isinstance(column.type, sa.Boolean):
                        renderers[prop.key] = self.render_boolean

        # then look at association proxy fields
        for key, desc in inspector.all_orm_descriptors.items():
            if desc.extension_type == ASSOCIATION_PROXY:
                prop = get_association_proxy_column(inspector, key)
                if prop:
                    column = prop.columns[0]
                    if isinstance(column.type, sa.DateTime):
                        renderers[key] = self.render_datetime
                    elif isinstance(column.type, sa.Boolean):
                        renderers[key] = self.render_boolean

        return renderers

    def append(self, field):
        self.fields.append(field)

    def insert(self, index, field):
        self.fields.insert(index, field)

    def insert_before(self, field, newfield):
        self.fields.insert_before(field, newfield)

    def insert_after(self, field, newfield):
        self.fields.insert_after(field, newfield)

    def replace(self, field, newfield):
        self.insert_after(field, newfield)
        self.remove(field)

    def remove(self, *args):
        for arg in args:
            if arg in self.fields:
                self.fields.remove(arg)

    # TODO: deprecare / remove this
    def remove_field(self, key):
        self.remove(key)

    # TODO: deprecare / remove this
    def remove_fields(self, *args):
        self.remove(*args)

    def make_schema(self):
        if not self.schema:

            if not self.model_class:
                # TODO
                raise NotImplementedError

            mapper = orm.class_mapper(self.model_class)

            # first filter our "full" field list so we ignore certain ones.  in
            # particular we don't want readonly fields in the schema, or any
            # which appear to be "private"
            includes = [f for f in self.fields
                        if f not in self.readonly_fields
                        and not f.startswith('_')
                        and f != 'versions']

            # derive list of "auto included" fields.  this is all "included"
            # fields which are part of the SQLAlchemy ORM for the object
            auto_includes = []
            property_keys = [p.key for p in mapper.iterate_properties]
            inspector = sa.inspect(self.model_class)
            for field in includes:
                if field in self.nodes:
                    continue    # these are explicitly set; no magic wanted
                if field in property_keys:
                    auto_includes.append(field)
                elif get_association_proxy(inspector, field):
                    auto_includes.append(field)

            # make schema - only include *property* fields at this point
            schema = CustomSchemaNode(self.model_class, includes=auto_includes)

            # for now, must manually add any "extra" fields?  this includes all
            # association proxy fields, not sure how other fields will behave
            for field in includes:
                if field not in schema:
                    node = self.nodes.get(field)
                    if not node:
                        node = colander.SchemaNode(colander.String(), name=field, missing='')
                    if not node.name:
                        node.name = field
                    schema.add(node)

            # apply any label overrides
            for key, label in self.labels.items():
                if key in schema:
                    schema[key].title = label

            # apply any widget overrides
            for key, widget in self.widgets.items():
                if key in schema:
                    schema[key].widget = widget

            # TODO: we are now doing this when making deform.Form, in which
            # case, do we still need to do it here?
            # apply any default values
            for key, default in self.defaults.items():
                if key in schema:
                    schema[key].default = default

            # apply any validators
            for key, validator in self.validators.items():
                if key is None:
                    # this one is form-wide
                    schema.validator = validator
                elif key in schema:
                    schema[key].validator = validator

            # apply required flags
            for key, required in self.required.items():
                if key in schema:
                    if required:
                        schema[key].missing = colander.required
                    else:
                        schema[key].missing = None # TODO?

            self.schema = schema

        return self.schema

    def set_label(self, key, label):
        self.labels[key] = label

        # update schema if necessary
        if self.schema and key in self.schema:
            self.schema[key].title = label

    def get_label(self, key):
        config = self.request.rattail_config
        app = config.get_app()
        return self.labels.get(key, app.make_title(key))

    def set_readonly(self, key, readonly=True):
        if readonly:
            self.readonly_fields.add(key)
        else:
            if key in self.readonly_fields:
                self.readonly_fields.remove(key)

    def set_node(self, key, nodeinfo, **kwargs):
        if isinstance(nodeinfo, colander.SchemaNode):
            node = nodeinfo
        else:
            kwargs.setdefault('name', key)
            node = colander.SchemaNode(nodeinfo, **kwargs)
        self.nodes[key] = node

        # must explicitly replace node, if we already have a schema
        if self.schema:
            self.schema[key] = node

    def set_type(self, key, type_, **kwargs):

        if type_ == 'datetime':
            self.set_renderer(key, self.render_datetime)

        elif type_ == 'datetime_falafel':
            self.set_renderer(key, self.render_datetime)
            self.set_node(key, types.FalafelDateTime(request=self.request))
            if kwargs.get('helptext'):
                app = self.request.rattail_config.get_app()
                timezone = app.get_timezone()
                self.set_helptext(key, f"NOTE: all times are local to {timezone}")

        elif type_ == 'datetime_local':
            self.set_renderer(key, self.render_datetime_local)
        elif type_ == 'date_plain':
            self.set_widget(key, PlainDateWidget())
        elif type_ == 'date_jquery':
            # TODO: is this safe / a good idea?
            # self.set_node(key, colander.Date())
            self.set_widget(key, JQueryDateWidget())

        elif type_ == 'time_jquery':
            self.set_node(key, types.JQueryTime())
            self.set_widget(key, JQueryTimeWidget())

        elif type_ == 'time_falafel':
            self.set_node(key, types.FalafelTime(request=self.request))

        elif type_ == 'duration':
            self.set_renderer(key, self.render_duration)
        elif type_ == 'boolean':
            self.set_renderer(key, self.render_boolean)
            self.set_widget(key, dfwidget.CheckboxWidget())
        elif type_ == 'currency':
            self.set_renderer(key, self.render_currency)
        elif type_ == 'quantity':
            self.set_renderer(key, self.render_quantity)
        elif type_ == 'percent':
            self.set_renderer(key, self.render_percent)
        elif type_ == 'gpc':
            self.set_renderer(key, self.render_gpc)
        elif type_ == 'enum':
            self.set_renderer(key, self.render_enum)
        elif type_ == 'codeblock':
            self.set_renderer(key, self.render_codeblock)
            self.set_widget(key, dfwidget.TextAreaWidget(cols=80, rows=8))
        elif type_ == 'text':
            self.set_renderer(key, self.render_pre_sans_serif)
            self.set_widget(key, dfwidget.TextAreaWidget(cols=80, rows=8))
        elif type_ == 'text_wrapped':
            self.set_renderer(key, self.render_pre_sans_serif_wrapped)
            self.set_widget(key, dfwidget.TextAreaWidget(cols=80, rows=8))
        elif type_ == 'file':
            tmpstore = SessionFileUploadTempStore(self.request)
            kw = {'widget': FileUploadWidget(tmpstore, request=self.request),
                  'title': self.get_label(key)}
            if 'required' in kwargs and not kwargs['required']:
                kw['missing'] = colander.null
            self.set_node(key, colander.SchemaNode(deform.FileData(), **kw))
        elif type_ == 'multi_file':
            tmpstore = SessionFileUploadTempStore(self.request)
            file_node = colander.SchemaNode(deform.FileData(),
                                            name='upload')

            kw = {'name': key,
                  'title': self.get_label(key),
                  'widget': MultiFileUploadWidget(tmpstore)}
            # if 'required' in kwargs and not kwargs['required']:
            #     kw['missing'] = colander.null
            if kwargs.get('validate_unique'):
                kw['validator'] = self.validate_multiple_files_unique
            files_node = colander.SequenceSchema(file_node, **kw)
            self.set_node(key, files_node)
        else:
            raise ValueError("unknown type for '{}' field: {}".format(key, type_))

    def validate_multiple_files_unique(self, node, value):

        # get SHA256 hash for each file; error if duplicates encountered
        hashes = {}
        for fileinfo in value:
            fp = fileinfo['fp']
            fp.seek(0)
            filehash = hashlib.sha256(fp.read()).hexdigest()
            if filehash in hashes:
                node.raise_invalid(f"Duplicate file detected: {fileinfo['filename']}")
            hashes[filehash] = fileinfo

    def set_enum(self, key, enum, empty=None):
        if enum:
            self.enums[key] = enum
            self.set_type(key, 'enum')
            values = list(enum.items())
            if empty:
                values.insert(0, empty)
            self.set_widget(key, dfwidget.SelectWidget(values=values))
        else:
            self.enums.pop(key, None)

    def get_enum(self, key):
        return self.enums.get(key)

    # TODO: i don't think this is actually being used anywhere..?
    def set_enum_value(self, key, enum_key, enum_value):
        enum = self.enums.get(key)
        if enum:
            enum[enum_key] = enum_value

    def set_renderer(self, key, renderer):
        if renderer is None:
            if key in self.renderers:
                del self.renderers[key]
        else:
            self.renderers[key] = renderer

    def add_renderer_kwargs(self, key, kwargs):
        self.renderer_kwargs.setdefault(key, {}).update(kwargs)

    def get_renderer_kwargs(self, key):
        return self.renderer_kwargs.get(key, {})

    def set_renderer_kwargs(self, key, kwargs):
        self.renderer_kwargs[key] = kwargs

    def set_input_handler(self, key, value):
        """
        Convenience method to assign "input handler" callback code for
        the given field.
        """
        self.add_renderer_kwargs(key, {'input_handler': value})

    def set_hidden(self, key, hidden=True):
        self.hidden[key] = hidden

    def set_widget(self, key, widget):
        self.widgets[key] = widget

        # update schema if necessary
        if self.schema and key in self.schema:
            self.schema[key].widget = widget

    def set_validator(self, key, validator):
        """
        Set the validator for the schema node represented by the given
        key.

        :param key: Normally this the name of one of the fields
           contained in the form.  It can also be ``None`` in which
           case the validator pertains to the form at large instead of
           one of the fields.

        :param validator: Callable which accepts ``(node, value)``
           args.
        """
        self.validators[key] = validator

        # we normally apply the validator when creating the schema, so
        # if this form already has a schema, then go ahead and apply
        # the validator to it
        if self.schema and key in self.schema:
            self.schema[key].validator = validator

    def set_required(self, key, required=True):
        """
        Set whether or not value is required for a given field.
        """
        self.required[key] = required

    def set_default(self, key, value):
        """
        Set the default value for a given field.
        """
        self.defaults[key] = value

    def set_helptext(self, key, value, dynamic=False):
        """
        Set the help text for a given field.
        """
        # nb. must avoid newlines, they cause some weird "blank page" error?!
        self.helptext[key] = value.replace('\n', ' ')
        if value and dynamic:
            self.dynamic_helptext[key] = True
        else:
            self.dynamic_helptext.pop(key, None)

    def has_helptext(self, key):
        """
        Returns boolean indicating whether the given field has accompanying
        help text.
        """
        return key in self.helptext

    def render_helptext(self, key):
        """
        Render the help text for the given field.
        """
        text = self.helptext[key]
        text = text.replace('"', '&quot;')
        return HTML.literal(text)

    def set_vuejs_field_converter(self, field, converter):
        self.vuejs_field_converters[field] = converter

    def render(self, **kwargs):
        warnings.warn("Form.render() is deprecated (for now?); "
                      "please use Form.render_deform() instead",
                      DeprecationWarning, stacklevel=2)
        return self.render_deform(**kwargs)

    def get_deform(self):
        """ """
        return self.make_deform_form()

    def make_deform_form(self):
        if not hasattr(self, 'deform_form'):

            schema = self.make_schema()

            # TODO: we are still also doing this when making the schema, but
            # seems like this should be the right place instead?
            # apply any default values
            for key, default in self.defaults.items():
                if key in schema:
                    schema[key].default = default

            # get initial form values from model instance
            kwargs = {}
            # TODO: ugh, this is necessary to avoid some logic
            # which assumes a ColanderAlchemy schema i think?
            if self.appstruct is not UNSPECIFIED:
                if self.appstruct:
                    kwargs['appstruct'] = self.appstruct
            elif self.model_instance:
                if self.model_class:
                    kwargs['appstruct'] = schema.dictify(self.model_instance)
                else:
                    kwargs['appstruct'] = self.model_instance

            # create form
            form = deform.Form(schema, **kwargs)
            form.tailbone_form = self

            # set readonly widget where applicable
            for field in self.readonly_fields:
                if field in form:
                    form[field].widget = ReadonlyWidget()

            self.deform_form = form

        return self.deform_form

    def render_vue_template(self, template='/forms/deform.mako', **context):
        """ """
        output = self.render_deform(template=template, **context)
        return HTML.literal(output)

    def render_deform(self, dform=None, template=None, **kwargs):
        if not template:
            template = '/forms/deform.mako'

        if dform is None:
            dform = self.make_deform_form()

        # TODO: would perhaps be nice to leverage deform's default rendering
        # someday..? i.e. using Chameleon *.pt templates
        # return dform.render()

        context = kwargs
        context['form'] = self
        context['dform'] = dform
        context.setdefault('can_edit_help', self.can_edit_help)
        if context['can_edit_help']:
            context.setdefault('edit_help_url', self.edit_help_url)
            context['field_labels'] = self.get_field_labels()
            context['field_markdowns'] = self.get_field_markdowns()
        context.setdefault('form_kwargs', {})
        # TODO: deprecate / remove the latter option here
        if self.auto_disable_save or self.auto_disable:
            context['form_kwargs'].setdefault('ref', self.vue_component)
            context['form_kwargs']['@submit'] = 'submit{}'.format(self.vue_component)
        if self.focus_spec:
            context['form_kwargs']['data-focus'] = self.focus_spec
        context['request'] = self.request
        context['readonly_fields'] = self.readonly_fields
        context['render_field_readonly'] = self.render_field_readonly
        return render(template, context)

    def get_field_labels(self):
        return dict([(field, self.get_label(field))
                     for field in self])

    def get_field_markdowns(self, session=None):
        app = self.request.rattail_config.get_app()
        model = app.model
        session = session or Session()

        if not hasattr(self, 'field_markdowns'):
            infos = session.query(model.TailboneFieldInfo)\
                           .filter(model.TailboneFieldInfo.route_prefix == self.route_prefix)\
                           .all()
            self.field_markdowns = dict([(info.field_name, info.markdown_text)
                                         for info in infos])

        return self.field_markdowns

    def get_vue_field_value(self, key):
        """ """
        if key not in self.fields:
            return

        dform = self.get_deform()
        if key not in dform:
            return

        field = dform[key]
        return make_json_safe(field.cstruct)

    def get_vuejs_model_value(self, field):
        """
        This method must return "raw" JS which will be assigned as the initial
        model value for the given field.  This JS will be written as part of
        the overall response, to be interpreted on the client side.
        """
        if field.name in self.vuejs_field_converters:
            convert = self.vuejs_field_converters[field.name]
            value = convert(field.cstruct)
            return json.dumps(value)

        if isinstance(field.schema.typ, colander.Set):
            if field.cstruct is colander.null:
                return '[]'

        try:
            return self.jsonify_value(field.cstruct)
        except Exception as error:
            raise TailboneJSONFieldError(field.name, error)

    def jsonify_value(self, value):
        """
        Take a Python value and convert to JSON
        """
        if value is colander.null:
            return 'null'

        if isinstance(value, dfwidget.filedict):
            # TODO: we used to always/only return 'null' here but hopefully
            # this also works, to show existing filename when present
            if value and value['filename']:
                return json.dumps({'name': value['filename']})
            return 'null'

        elif isinstance(value, list) and all([isinstance(f, dfwidget.filedict)
                                              for f in value]):
            return json.dumps([{'name': f['filename']}
                               for f in value])

        app = self.request.rattail_config.get_app()
        value = app.json_friendly(value)
        return json.dumps(value)

    def get_error_messages(self, field):
        if field.error:
            return field.error.messages()

        error = self.make_deform_form().error
        if error:
            if isinstance(error, colander.Invalid):
                if error.node.name == field.name:
                    return error.messages()

    def messages_json(self, messages):
        dump = json.dumps(messages)
        dump = dump.replace("'", '&apos;')
        return dump

    def field_visible(self, field):
        if self.hidden and self.hidden.get(field):
            return False
        return True

    def set_vuejs_component_kwargs(self, **kwargs):
        self.vuejs_component_kwargs.update(kwargs)

    def render_vue_tag(self, **kwargs):
        """ """
        return self.render_vuejs_component(**kwargs)

    def render_vuejs_component(self, **kwargs):
        """
        Render the Vue.js component HTML for the form.

        Most typically this is something like:

        .. code-block:: html

           <tailbone-form :configure-fields-help="configureFieldsHelp">
           </tailbone-form>
        """
        kw = dict(self.vuejs_component_kwargs)
        kw.update(kwargs)
        if self.can_edit_help:
            kw.setdefault(':configure-fields-help', 'configureFieldsHelp')
        return HTML.tag(self.vue_tagname, **kw)

    def set_json_data(self, key, value):
        """
        Establish a data value for use in client-side JS.  This value
        will be JSON-encoded and made available to the
        `<tailbone-form>` component within the client page.
        """
        self.json_data[key] = value

    def include_template(self, template, context):
        """
        Declare a JS template as required by the current form.  This
        template will then be included in the final page, so all
        widgets behave correctly.
        """
        self.included_templates[template] = context

    def render_included_templates(self):
        templates = []
        for template, context in self.included_templates.items():
            context = dict(context)
            context['form'] = self
            templates.append(HTML.literal(render(template, context)))
        return HTML.literal('\n').join(templates)

    def render_vue_field(self, fieldname, **kwargs):
        """ """
        return self.render_field_complete(fieldname, **kwargs)

    def render_field_complete(self, fieldname, bfield_attrs={},
                              session=None):
        """
        Render the given field completely, i.e. with ``<b-field>``
        wrapper.  Note that this is meant to render *editable* fields,
        i.e. showing a widget, unless the field input is hidden.  In
        other words it's not for "readonly" fields.
        """
        dform = self.make_deform_form()
        field = dform[fieldname] if fieldname in dform else None

        include = bool(field)
        if self.readonly or (not field and fieldname in self.readonly_fields):
            include = True
        if not include:
            return

        if self.field_visible(fieldname):
            label = self.get_label(fieldname)
            markdowns = self.get_field_markdowns(session=session)

            # these attrs will be for the <b-field> (*not* the widget)
            attrs = {
                ':horizontal': 'true',
            }

            # add some magic for file input fields
            if field and isinstance(field.schema.typ, deform.FileData):
                attrs['class_'] = 'file'

            # next we will build array of messages to display..some
            # fields always show a "helptext" msg, and some may have
            # validation errors..
            field_type = None
            messages = []

            # show errors if present
            error_messages = self.get_error_messages(field) if field else None
            if error_messages:
                field_type = 'is-danger'
                messages.extend(error_messages)

            # show helptext if present
            # TODO: older logic did this only if field was *not*
            # readonly, perhaps should add that back..
            if self.has_helptext(fieldname):
                messages.append(self.render_helptext(fieldname))

            # ..okay now we can declare the field messages and type
            if field_type:
                attrs['type'] = field_type
            if messages:
                if len(messages) == 1:
                    msg = messages[0]
                    if msg.startswith('`') and msg.endswith('`'):
                        attrs[':message'] = msg
                    else:
                        attrs['message'] = msg
                else:
                    # nb. must pass an array as JSON string
                    attrs[':message'] = '[{}]'.format(', '.join([
                        "'{}'".format(msg.replace("'", r"\'"))
                        for msg in messages]))

            # merge anything caller provided
            attrs.update(bfield_attrs)

            # render the field widget or whatever
            if self.readonly or fieldname in self.readonly_fields:
                html = self.render_field_value(fieldname) or HTML.tag('span')
                if type(html) is str:
                    html = HTML.tag('span', c=[html])
            elif field:
                html = field.serialize(**self.get_renderer_kwargs(fieldname))
                html = HTML.literal(html)

            # may need a complex label
            label_contents = [label]

            # add 'help' icon/tooltip if defined
            if markdowns.get(fieldname):
                icon = HTML.tag('b-icon', size='is-small', pack='fas',
                                icon='question-circle')
                tooltip = render_markdown(markdowns[fieldname])

                # nb. must apply hack to get <template #content> as final result
                tooltip_template = HTML.tag('template', c=[tooltip],
                                            **{'#content': 1})
                tooltip_template = tooltip_template.replace(
                    HTML.literal('<template #content="1"'),
                    HTML.literal('<template #content'))

                tooltip = HTML.tag('b-tooltip',
                                   type='is-white',
                                   size='is-large',
                                   multilined='multilined',
                                   c=[icon, tooltip_template])
                label_contents.append(HTML.literal('&nbsp; &nbsp;'))
                label_contents.append(tooltip)

            # add 'configure' icon if allowed
            if self.can_edit_help:
                icon = HTML.tag('b-icon', size='is-small', pack='fas',
                                icon='cog')
                icon = HTML.tag('a', title="Configure field", c=[icon],
                                **{'@click.prevent': "configureFieldInit('{}')".format(fieldname),
                                   'v-show': 'configureFieldsHelp'})
                label_contents.append(HTML.literal('&nbsp; &nbsp;'))
                label_contents.append(icon)

            # only declare label template if it's complex
            html = [html]
            # TODO: figure out why complex label does not work for oruga
            if self.request.use_oruga:
                attrs['label'] = label
            else:
                if len(label_contents) > 1:

                    # nb. must apply hack to get <template #label> as final result
                    label_template = HTML.tag('template', c=label_contents,
                                              **{'#label': 1})
                    label_template = label_template.replace(
                        HTML.literal('<template #label="1"'),
                        HTML.literal('<template #label'))
                    html.insert(0, label_template)

                else: # simple label
                    attrs['label'] = label

            # and finally wrap it all in a <b-field>
            return HTML.tag('b-field', c=html, **attrs)

        elif field: # hidden field

            # can just do normal thing for these
            # TODO: again, why does serialize() not return literal?
            return HTML.literal(field.serialize())

    # TODO: this was copied from wuttaweb; can remove when we align
    # Form class structure
    def render_vue_finalize(self):
        """ """
        set_data = f"{self.vue_component}.data = function() {{ return {self.vue_component}Data }}"
        make_component = f"Vue.component('{self.vue_tagname}', {self.vue_component})"
        return HTML.tag('script', c=['\n',
                                     HTML.literal(set_data),
                                     '\n',
                                     HTML.literal(make_component),
                                     '\n'])

    def render_field_readonly(self, field_name, **kwargs):
        """
        Render the given field completely, but in read-only fashion.

        Note that this method will generate the wrapper div and label, as well
        as the field value.
        """
        if field_name not in self.fields:
            return ''

        label = kwargs.get('label')
        if not label:
            label = self.get_label(field_name)

        value = self.render_field_value(field_name) or ''

        if not self.request.use_oruga:

            label = HTML.tag('label', label, for_=field_name)
            field_div = HTML.tag('div', class_='field', c=[value])
            contents = [label, field_div]

            if self.has_helptext(field_name):
                contents.append(HTML.tag('span', class_='instructions',
                                         c=[self.render_helptext(field_name)]))

            return HTML.tag('div', class_='field-wrapper {}'.format(field_name), c=contents)

        # nb. for some reason we must wrap once more for oruga,
        # otherwise it splits up the field?!
        value = HTML.tag('span', c=[value])

        # oruga uses <o-field>
        return HTML.tag('o-field', label=label, c=[value], **{':horizontal': 'true'})

    def render_field_value(self, field_name):
        record = self.model_instance
        if self.renderers and field_name in self.renderers:
            return self.renderers[field_name](record, field_name)
        return self.render_generic(record, field_name)

    def render_generic(self, record, field_name):
        value = self.obtain_value(record, field_name)
        if value is None:
            return ""
        return str(value)

    def render_datetime(self, record, field_name):
        value = self.obtain_value(record, field_name)
        if value is None:
            return ""
        return raw_datetime(self.request.rattail_config, value)

    def render_datetime_local(self, record, field_name):
        value = self.obtain_value(record, field_name)
        if value is None:
            return ""
        app = self.request.rattail_config.get_app()
        value = app.localtime(value)
        return raw_datetime(self.request.rattail_config, value)

    def render_duration(self, record, field_name):
        seconds = self.obtain_value(record, field_name)
        if seconds is None:
            return ""
        app = self.request.rattail_config.get_app()
        return app.render_duration(seconds=seconds)

    def render_boolean(self, record, field_name):
        value = self.obtain_value(record, field_name)
        return pretty_boolean(value)

    def render_currency(self, record, field_name):
        value = self.obtain_value(record, field_name)
        if value is None:
            return ""
        try:
            if value < 0:
                return "(${:0,.2f})".format(0 - value)
            return "${:0,.2f}".format(value)
        except ValueError:
            return str(value)

    def render_quantity(self, obj, field):
        value = self.obtain_value(obj, field)
        if value is None:
            return ""
        app = self.request.rattail_config.get_app()
        return app.render_quantity(value)

    def render_percent(self, obj, field):
        app = self.request.rattail_config.get_app()
        value = self.obtain_value(obj, field)
        return app.render_percent(value, places=3)

    def render_gpc(self, obj, field):
        value = self.obtain_value(obj, field)
        if value is None:
            return ""
        return value.pretty()

    def render_enum(self, record, field_name):
        value = self.obtain_value(record, field_name)
        if value is None:
            return ""
        enum = self.enums.get(field_name)
        if enum and value in enum:
            return str(enum[value])
        return str(value)

    def render_codeblock(self, record, field_name):
        value = self.obtain_value(record, field_name)
        if value is None:
            return ""
        return HTML.tag('pre', value)

    def render_pre_sans_serif(self, record, field_name, wrapped=False):
        value = self.obtain_value(record, field_name)
        if value is None:
            return ""

        kwargs = {
            'c': value,
            # this uses a Bulma helper class, for which we also add
            # custom styles to our "default" base.css (for jquery
            # theme)
            'class_': 'is-family-sans-serif',
        }

        if wrapped:
            kwargs['style'] = 'white-space: pre-wrap;'

        return HTML.tag('pre', **kwargs)

    def render_pre_sans_serif_wrapped(self, record, field_name):
        return self.render_pre_sans_serif(record, field_name, wrapped=True)

    def obtain_value(self, record, field_name):
        if record:

            if isinstance(record, dict):
                return record[field_name]

            try:
                return getattr(record, field_name)
            except AttributeError:
                pass

            try:
                return record[field_name]
            except TypeError:
                pass

        # TODO: is this always safe to do?
        elif self.defaults and field_name in self.defaults:
            return self.defaults[field_name]

    def validate(self, *args, **kwargs):
        """
        Try to validate the form.

        This should work whether data was submitted as classic POST
        data, or as JSON body.

        :returns: ``True`` if form data is valid, otherwise ``False``.
        """
        if 'newstyle' in kwargs:
            warnings.warn("the `newstyle` kwarg is no longer used "
                          "for Form.validate()",
                          DeprecationWarning, stacklevel=2)

        if hasattr(self, 'validated'):
            del self.validated
        if self.request.method != 'POST':
            return False

        controls = get_form_data(self.request).items()

        # unfortunately the normal form logic (i.e. peppercorn) is
        # expecting all values to be strings, whereas if our data
        # came from JSON body, may have given us some Pythonic
        # objects.  so here we must convert them *back* to strings
        # TODO: this seems like a hack, i must be missing something
        # TODO: also this uses same "JSON" check as get_form_data()
        if self.request.is_xhr and not self.request.POST:
            controls = [[key, val] for key, val in controls]
            for i in range(len(controls)):
                key, value = controls[i]
                if value is None:
                    controls[i][1] = ''
                elif value is True:
                    controls[i][1] = 'true'
                elif value is False:
                    controls[i][1] = 'false'
                elif not isinstance(value, str):
                    controls[i][1] = str(value)

        dform = self.make_deform_form()
        try:
            self.validated = dform.validate(controls)
            return True
        except deform.ValidationFailure:
            return False


@colander.deferred
def upload_widget(node, kw):
    request = kw['request']
    tmpstore = SessionFileUploadTempStore(request)
    return dfwidget.FileUploadWidget(tmpstore)


class SimpleFileImport(colander.Schema):
    """
    Schema for simple file import.  Note that you must bind your ``request``
    object to this schema, i.e.::

       schema = SimpleFileImport().bind(request=request)
    """
    filename = colander.SchemaNode(deform.FileData(),
                                   widget=upload_widget)
