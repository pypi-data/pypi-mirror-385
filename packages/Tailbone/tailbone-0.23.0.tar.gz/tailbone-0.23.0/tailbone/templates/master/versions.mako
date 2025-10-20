## -*- coding: utf-8; -*-
## ##############################################################################
## 
## Default master 'versions' template, for showing an object's version history.
## 
## ##############################################################################
<%inherit file="/page.mako" />

<%def name="title()">${model_title_plural} » ${instance_title} » history</%def>

<%def name="content_title()">
  Version History
</%def>

<%def name="render_this_page()">
  ${self.page_content()}
</%def>

<%def name="page_content()">
  ${grid.render_vue_tag(**{':csrftoken': 'csrftoken'})}
</%def>

<%def name="render_vue_templates()">
  ${parent.render_vue_templates()}
  ${grid.render_vue_template()}
</%def>

<%def name="make_vue_components()">
  ${parent.make_vue_components()}
  ${grid.render_vue_finalize()}
</%def>
