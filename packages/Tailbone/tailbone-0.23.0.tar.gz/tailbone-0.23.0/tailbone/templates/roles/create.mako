## -*- coding: utf-8 -*-
<%inherit file="/master/create.mako" />

<%def name="head_tags()">
  ${parent.head_tags()}
  ${h.stylesheet_link(request.static_url('tailbone:static/css/perms.css'))}
</%def>

<%def name="modify_vue_vars()">
  ${parent.modify_vue_vars()}
  <script>
    // TODO: this variable name should be more dynamic (?) since this is
    // connected to (and only here b/c of) the permissions field
    ${form.vue_component}Data.showingPermissionGroup = ''
  </script>
</%def>
