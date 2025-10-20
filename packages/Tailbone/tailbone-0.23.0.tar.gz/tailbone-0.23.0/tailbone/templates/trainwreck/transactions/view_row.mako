## -*- coding: utf-8; -*-
<%inherit file="/master/view_row.mako" />

<%def name="modify_vue_vars()">
  ${parent.modify_vue_vars()}
  <script>
    % if discounts_data is not Undefined:
        ${form.vue_component}Data.discountsData = ${json.dumps(discounts_data)|n}
    % endif
  </script>
</%def>
