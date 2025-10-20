## -*- coding: utf-8; -*-
<%inherit file="/page.mako" />

<%def name="object_helpers()"></%def>

<%def name="render_form_buttons()"></%def>

<%def name="render_form_template()">
  ${form.render_vue_template(buttons=capture(self.render_form_buttons))|n}
</%def>

<%def name="render_form()">
  <div class="form">
    ${form.render_vue_tag()}
  </div>
</%def>

<%def name="page_content()">
  % if main_form_collapsible:
      <${b}-collapse class="panel"
                     % if request.use_oruga:
                         v-model:open="mainFormPanelOpen"
                     % else:
                         :open.sync="mainFormPanelOpen"
                     % endif
                     >
        <template #trigger="props">
          <div class="panel-heading"
               role="button"
               style="cursor: pointer;">

            ## TODO: for some reason buefy will "reuse" the icon
            ## element in such a way that its display does not
            ## refresh.  so to work around that, we use different
            ## structure for the two icons, so buefy is forced to
            ## re-draw

            <b-icon v-if="props.open"
                    pack="fas"
                    icon="caret-down">
            </b-icon>

            <span v-if="!props.open">
              <b-icon pack="fas"
                      icon="caret-right">
              </b-icon>
            </span>

            &nbsp;
            <strong>${main_form_title}</strong>
          </div>
        </template>
        <div class="panel-block">
          <div class="form-wrapper">
            <br />
            ${self.render_form()}
          </div>
        </div>
      </${b}-collapse>
  % else:
      <div class="form-wrapper">
        <br />
        ${self.render_form()}
      </div>
  % endif
</%def>

<%def name="render_this_page()">
  <div style="display: flex; justify-content: space-between;">

    <div class="this-page-content">
      ${self.page_content()}
    </div>

    <div style="display: flex; align-items: flex-start;">

      ${before_object_helpers()}

      <div class="object-helpers">
        ${self.object_helpers()}
      </div>

      <ul id="context-menu">
        ${self.context_menu_items()}
      </ul>
    </div>

  </div>
</%def>

<%def name="before_object_helpers()"></%def>

<%def name="render_vue_templates()">
  ${parent.render_vue_templates()}
  % if form is not Undefined:
      ${self.render_form_template()}
  % endif
</%def>

<%def name="modify_vue_vars()">
  ${parent.modify_vue_vars()}
  % if main_form_collapsible:
      <script>
        ThisPageData.mainFormPanelOpen = ${'false' if main_form_autocollapse else 'true'}
      </script>
  % endif
</%def>

<%def name="make_vue_components()">
  ${parent.make_vue_components()}
  % if form is not Undefined:
      ${form.render_vue_finalize()}
  % endif
</%def>
