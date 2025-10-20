## -*- coding: utf-8; -*-
<%inherit file="/master/view.mako" />

<%def name="modify_vue_vars()">
  ${parent.modify_vue_vars()}
  <script>
    % if custorder_xref_markers_data is not Undefined:
        ${form.vue_component}Data.custorderXrefMarkersData = ${json.dumps(custorder_xref_markers_data)|n}
    % endif
  </script>
</%def>
