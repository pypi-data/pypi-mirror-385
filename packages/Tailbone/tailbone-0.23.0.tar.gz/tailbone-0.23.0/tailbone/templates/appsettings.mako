## -*- coding: utf-8; -*-
<%inherit file="/page.mako" />

<%def name="title()">App Settings</%def>

<%def name="content_title()"></%def>

<%def name="context_menu_items()">
  % if request.has_perm('settings.list'):
      <li>${h.link_to("View Raw Settings", url('settings'))}</li>
  % endif
</%def>

<%def name="page_content()">
  <app-settings :groups="groups" :showing-group="showingGroup"></app-settings>
</%def>

<%def name="render_vue_templates()">
  ${parent.render_vue_templates()}
  <script type="text/x-template" id="app-settings-template">

    <div class="form">
      ${h.form(form.action_url, id=dform.formid, method='post', **{'@submit': 'submitForm'})}
      ${h.csrf_token(request)}

      % if dform.error:
          <b-notification type="is-warning">
            Please see errors below.
          </b-notification>
          <b-notification type="is-warning">
            ${dform.error}
          </b-notification>
      % endif

      <div class="app-wrapper">

        <div class="level">

          <div class="level-left">
            <div class="level-item">
              <b-field label="Showing Group">
                <b-select name="settings-group"
                          v-model="showingGroup">
                  <option value="">(All)</option>
                  <option v-for="group in groups"
                          :key="group.label"
                          :value="group.label">
                    {{ group.label }}
                  </option>
                </b-select>
              </b-field>
            </div>
          </div>

          <div class="level-right"
               v-if="configOptions.length">
            <div class="level-item">
              <b-field label="Go To Configure...">
                <b-select v-model="gotoConfigureURL"
                          @input="gotoConfigure()">
                  <option v-for="option in configOptions"
                          :key="option.url"
                          :value="option.url">
                    {{ option.label }}
                  </option>
                </b-select>
              </b-field>
            </div>
          </div>

        </div>

        <div v-for="group in groups"
             class="card"
             v-show="!showingGroup || showingGroup == group.label"
             style="margin-bottom: 1rem;">
          <header class="card-header">
            <p class="card-header-title">{{ group.label }}</p>
          </header>
          <div class="card-content">
            <div v-for="setting in group.settings"
                 ## TODO: not sure how the error handling looks now?
                 ## :class="'field-wrapper' + (setting.error ? ' with-error' : '')"
                 >

              <div style="margin-bottom: 2rem;">

                <b-field horizontal
                         :label="setting.label"
                         :type="setting.error ? 'is-danger' : null"
                         ## TODO: what if there are multiple error messages?
                         :message="setting.error ? setting.error_messages[0] : null">

                  <b-checkbox v-if="setting.data_type == 'bool'"
                              :name="setting.field_name"
                              :id="setting.field_name"
                              v-model="setting.value"
                              native-value="true">
                    {{ setting.value || false }}
                  </b-checkbox>

                  <b-input v-else-if="setting.data_type == 'list'"
                           type="textarea"
                           :name="setting.field_name"
                           v-model="setting.value">
                  </b-input>

                  <b-select v-else-if="setting.choices"
                            :name="setting.field_name"
                            :id="setting.field_name"
                            v-model="setting.value">
                    <option v-for="choice in setting.choices"
                            :value="choice">
                      {{ choice }}
                    </option>
                  </b-select>

                  <b-input v-else
                           :name="setting.field_name"
                           :id="setting.field_name"
                           v-model="setting.value" />

                </b-field>

                <span v-if="setting.helptext"
                      v-html="setting.helptext"
                      class="instructions">
                </span>
              </div>

            </div>
          </div><!-- card-content -->
        </div><!-- card -->

        <div class="buttons">
          <once-button tag="a" href="${form.cancel_url}"
                       text="Cancel">
          </once-button>
          <b-button type="is-primary"
                    native-type="submit"
                    :disabled="formSubmitting">
            {{ formButtonText }}
          </b-button>
        </div>

      </div><!-- app-wrapper -->

      ${h.end_form()}
    </div>
  </script>
</%def>


<%def name="modify_vue_vars()">
  ${parent.modify_vue_vars()}
  <script>
    ThisPageData.groups = ${json.dumps(settings_data)|n}
    ThisPageData.showingGroup = ${json.dumps(current_group or '')|n}
  </script>
</%def>

<%def name="make_vue_components()">
  ${parent.make_vue_components()}
  <script>

    Vue.component('app-settings', {
        template: '#app-settings-template',
        props: {
            groups: Array,
            showingGroup: String
        },
        data() {
            return {
                formSubmitting: false,
                formButtonText: ${json.dumps(getattr(form, 'submit_label', getattr(form, 'save_label', "Submit")))|n},
                configOptions: ${json.dumps(config_options)|n},
                gotoConfigureURL: null,
            }
        },
        methods: {
            submitForm() {
                this.formSubmitting = true
                this.formButtonText = "Working, please wait..."
            },
            gotoConfigure() {
                if (this.gotoConfigureURL) {
                    location.href = this.gotoConfigureURL
                }
            },
        }
    })

  </script>
</%def>
