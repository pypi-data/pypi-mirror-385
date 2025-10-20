## -*- coding: utf-8; -*-
<%inherit file="/master/view.mako" />

<%def name="extra_styles()">
  ${parent.extra_styles()}
  <style type="text/css">
    .email-message-body {
        border: 1px solid #000000;
        margin-top: 2rem;
        height: 500px;
    }
  </style>
</%def>

<%def name="object_helpers()">
  ${parent.object_helpers()}
  <nav class="panel">
    <p class="panel-heading">Processing</p>
    <div class="panel-block">
      <div class="display: flex; flex-align: column;">
        % if bounce.processed:
            <p class="block">
              This bounce was processed
              ${h.pretty_datetime(request.rattail_config, bounce.processed)}
              by ${bounce.processed_by}
            </p>
            % if master.has_perm('unprocess'):
                <once-button type="is-warning"
                             tag="a" href="${url('emailbounces.unprocess', uuid=bounce.uuid)}"
                             text="Mark this bounce as UN-processed">
                </once-button>
            % endif
        % else:
            <p class="block">
              This bounce has NOT yet been processed.
            </p>
            % if master.has_perm('process'):
                <once-button type="is-primary"
                             tag="a" href="${url('emailbounces.process', uuid=bounce.uuid)}"
                             text="Mark this bounce as Processed">
                </once-button>
            % endif
        % endif
      </div>
    </div>
  </nav>
</%def>

<%def name="render_this_page()">
  ${parent.render_this_page()}
  <pre class="email-message-body">${message}</pre>
</%def>


${parent.body()}
