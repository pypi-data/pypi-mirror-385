## -*- coding: utf-8; -*-
<%inherit file="/master/create.mako" />

<%def name="title()">${index_title}</%def>

<%def name="content_title()"></%def>

<%def name="page_content()">
  % if project_type:
      <b-field grouped>
        <b-field horizontal expanded label="Project Type"
                 class="is-expanded">
          ${project_type}
        </b-field>
        <once-button type="is-primary"
                     tag="a" href="${url('generated_projects.create')}"
                     text="Start Over">
        </once-button>
      </b-field>
  % endif
  ${parent.page_content()}
</%def>


${parent.body()}
