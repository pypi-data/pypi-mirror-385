## -*- coding: utf-8; -*-
<%inherit file="wuttaweb:templates/page.mako" />

<%def name="render_vue_template_this_page()">
  <script type="text/x-template" id="this-page-template">
    <div style="height: 100%;">
      ## DEPRECATED; called for back-compat
      ${self.render_this_page()}
    </div>
  </script>
</%def>

## DEPRECATED; remains for back-compat
<%def name="render_this_page()">
  <div style="display: flex;">

    <div class="this-page-content" style="flex-grow: 1;">
      ${self.page_content()}
    </div>

    ## DEPRECATED; remains for back-compat
    <ul id="context-menu">
      ${self.context_menu_items()}
    </ul>
  </div>
</%def>

## DEPRECATED; remains for back-compat
<%def name="context_menu_items()">
  % if context_menu_list_items is not Undefined:
      % for item in context_menu_list_items:
          <li>${item}</li>
      % endfor
  % endif
</%def>

<%def name="modify_vue_vars()">
  ${parent.modify_vue_vars()}
  <script>

    ThisPageData.csrftoken = ${json.dumps(h.get_csrf_token(request))|n}

    % if can_edit_help:
        ThisPage.props.configureFieldsHelp = Boolean
    % endif

  </script>
</%def>
