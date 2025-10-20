## -*- coding: utf-8; -*-
<%inherit file="/page.mako" />

<%def name="title()">changes @ ver ${transaction.id}</%def>

<%def name="extra_styles()">
  ${parent.extra_styles()}
  <style type="text/css">

    .this-page-content {
        overflow: auto;
    }

    .versions-wrapper {
        margin-left: 2rem;
    }

  </style>
</%def>

<%def name="page_content()">

  <div class="form-wrapper" style="margin: 1rem; 0;">
    <div class="form">

      <b-field label="Changed" horizontal>
        <span>${h.pretty_datetime(request.rattail_config, changed)}</span>
      </b-field>

      <b-field label="Changed by" horizontal>
        <span>${transaction.user or ''}</span>
      </b-field>

      <b-field label="IP Address" horizontal>
        <span>${transaction.remote_addr}</span>
      </b-field>

      <b-field label="Comment" horizontal>
        <span>${transaction.meta.get('comment') or ''}</span>
      </b-field>

      <b-field label="TXN ID" horizontal>
        <span>${transaction.id}</span>
      </b-field>

    </div>
  </div>

  <div class="versions-wrapper">
    % for diff in version_diffs:
        <h4 class="is-size-4 block">${diff.title}</h4>
        ${diff.render_html()}
    % endfor
  </div>
</%def>


${parent.body()}
