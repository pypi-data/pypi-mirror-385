## -*- coding: utf-8; -*-
<%inherit file="/master/create.mako" />

<%def name="extra_styles()">
  ${parent.extra_styles()}
  <style type="text/css">

    % if use_form:
        #report-description {
          margin-left: 2em;
        }
    % else:
        .report-selection {
          margin-left: 10em;
          margin-top: 3em;
        }

        .report-selection h3 {
            margin-top: 2em;
        }
    % endif

  </style>
</%def>

<%def name="render_form()">
  <div class="form">
    <p>Please select the type of report you wish to generate.</p>
    <br />
    <div style="display: flex;">
      <tailbone-form v-on:report-change="reportChanged"></tailbone-form>
      <div id="report-description">{{ reportDescription }}</div>
    </div>
  </div>
</%def>

<%def name="page_content()">
  % if use_form:
      ${parent.page_content()}
  % else:
      <div>
        <br />
        <p>Please select the type of report you wish to generate.</p>

        <div class="report-selection">
          % for key in sorted_reports:
              <% report = reports[key] %>
              <h3>${h.link_to(report.name, url('generate_specific_report', type_key=key))}</h3>
              <p>${report.__doc__}</p>
          % endfor
        </div>
      </div>
  % endif
</%def>

<%def name="modify_vue_vars()">
  ${parent.modify_vue_vars()}
  <script>

    ${form.vue_component}Data.reportDescriptions = ${json.dumps(report_descriptions)|n}

    ${form.vue_component}.methods.reportTypeChanged = function(reportType) {
        this.$emit('report-change', this.reportDescriptions[reportType])
    }

    ThisPageData.reportDescription = null

    ThisPage.methods.reportChanged = function(description) {
        this.reportDescription = description
    }

  </script>
</%def>
