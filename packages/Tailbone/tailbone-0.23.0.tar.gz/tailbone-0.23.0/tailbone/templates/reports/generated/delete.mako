## -*- coding: utf-8; -*-
<%inherit file="/master/delete.mako" />

<%def name="modify_vue_vars()">
  ${parent.modify_vue_vars()}
  <script>
    % if params_data is not Undefined:
        ${form.vue_component}Data.paramsData = ${json.dumps(params_data)|n}
    % endif
  </script>
</%def>
