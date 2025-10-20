## -*- coding: utf-8; -*-
<%inherit file="/batch/view.mako" />

<%def name="modify_vue_vars()">
  ${parent.modify_vue_vars()}
  <script>
    ${form.vue_component}Data.taxesData = ${json.dumps(taxes_data)|n}
  </script>
</%def>
