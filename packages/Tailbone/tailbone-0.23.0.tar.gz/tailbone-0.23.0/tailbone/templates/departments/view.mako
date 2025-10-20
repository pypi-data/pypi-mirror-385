## -*- coding: utf-8; -*-
<%inherit file="/master/view.mako" />

<%def name="modify_vue_vars()">
  ${parent.modify_vue_vars()}
  <script>
    ${form.vue_component}Data.employeesData = ${json.dumps(employees_data)|n}
  </script>
</%def>
