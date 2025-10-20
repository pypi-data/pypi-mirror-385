## -*- coding: utf-8; -*-
<%inherit file="/master/form.mako" />

<%def name="title()">${index_title} &raquo; ${report.name}</%def>

<%def name="content_title()">New Report:&nbsp; ${report.name}</%def>

<%def name="render_form()">
  <div class="form">
    <p class="block">
      ${report.__doc__}
    </p>
    % if report.help_url:
        <p class="block">
          <b-button icon-pack="fas"
                    icon-left="question-circle"
                    tag="a" target="_blank"
                    href="${report.help_url}">
            Help for this report
          </b-button>
        </p>
    % endif
    <tailbone-form></tailbone-form>
  </div>
</%def>


${parent.body()}
