## -*- coding: utf-8; -*-
<%inherit file="/base.mako" />

<%def name="render_vue_templates()">
  ${parent.render_vue_templates()}
  ${self.render_vue_template_this_page()}
</%def>

<%def name="render_vue_template_this_page()">
  ## DEPRECATED; called for back-compat
  ${self.render_this_page_template()}
</%def>

<%def name="render_this_page_template()">
  <script type="text/x-template" id="this-page-template">
    <div>
      ## DEPRECATED; called for back-compat
      ${self.render_this_page()}
    </div>
  </script>
  <script>

    const ThisPage = {
        template: '#this-page-template',
        mixins: [SimpleRequestMixin],
        props: {
            configureFieldsHelp: Boolean,
        },
        computed: {},
        watch: {},
        methods: {

            changeContentTitle(newTitle) {
                this.$emit('change-content-title', newTitle)
            },
        },
    }

    const ThisPageData = {
        ## TODO: should find a better way to handle CSRF token
        csrftoken: ${json.dumps(h.get_csrf_token(request))|n},
    }

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

## nb. this is the canonical block for page content!
<%def name="page_content()"></%def>

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

  ## DEPRECATED; called for back-compat
  ${self.declare_this_page_vars()}
  ${self.modify_this_page_vars()}
</%def>

<%def name="make_vue_components()">
  ${parent.make_vue_components()}

  ## DEPRECATED; called for back-compat
  ${self.make_this_page_component()}
</%def>

<%def name="make_this_page_component()">
  ${self.finalize_this_page_vars()}
  <script>
    ThisPage.data = function() { return ThisPageData }
    Vue.component('this-page', ThisPage)
    <% request.register_component('this-page', 'ThisPage') %>
  </script>
</%def>

##############################
## DEPRECATED
##############################

<%def name="declare_this_page_vars()"></%def>

<%def name="modify_this_page_vars()"></%def>

<%def name="finalize_this_page_vars()"></%def>
