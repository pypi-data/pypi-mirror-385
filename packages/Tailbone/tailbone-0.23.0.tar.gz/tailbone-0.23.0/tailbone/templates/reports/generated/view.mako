## -*- coding: utf-8; -*-
<%inherit file="/master/view.mako" />

<%def name="object_helpers()">
  % if master.has_perm('create'):
      <nav class="panel">
        <p class="panel-heading">Tools</p>
        <div class="panel-block buttons">
          <div style="display: flex; flex-direction: column;">
          <once-button type="is-primary"
                       % if rerun_report_url:
                       tag="a" href="${rerun_report_url}"
                       % else:
                       disabled title="Unknown report type"
                       % endif
                       text="Re-run This Report"
                       icon-pack="fas"
                       icon-left="arrow-circle-right">
          </once-button>
          </div>
        </div>
      </nav>
  % endif
</%def>

<%def name="modify_vue_vars()">
  ${parent.modify_vue_vars()}
  <script>
    % if params_data is not Undefined:
        ${form.vue_component}Data.paramsData = ${json.dumps(params_data)|n}
    % endif
  </script>
</%def>
