## -*- coding: utf-8; -*-

<% request.register_component(form.vue_tagname, form.vue_component) %>

<script type="text/x-template" id="${form.vue_tagname}-template">

  <div>
  % if not form.readonly:
  ${h.form(form.action_url, id=dform.formid, method='post', enctype='multipart/form-data', **(form_kwargs or {}))}
  ${h.csrf_token(request)}
  % endif

  <section>
    % if form_body is not Undefined and form_body:
        ${form_body|n}
    % elif getattr(form, 'grouping', None):
        % for group in form.grouping:
            <nav class="panel">
              <p class="panel-heading">${group}</p>
              <div class="panel-block">
                <div>
                  % for field in form.grouping[group]:
                      ${form.render_field_complete(field)}
                  % endfor
                </div>
              </div>
            </nav>
        % endfor
    % else:
        % for fieldname in form.fields:
            ${form.render_vue_field(fieldname, session=session)}
        % endfor
    % endif
  </section>

  % if buttons:
      <br />
      ${buttons|n}
  % elif not form.readonly and (buttons is Undefined or (buttons is not None and buttons is not False)):
      <br />
      <div class="buttons">
        % if getattr(form, 'show_cancel', True):
            % if form.auto_disable_cancel:
                <once-button tag="a" href="${form.cancel_url or request.get_referrer()}"
                             text="Cancel">
                </once-button>
            % else:
                <b-button tag="a" href="${form.cancel_url or request.get_referrer()}">
                  Cancel
                </b-button>
            % endif
        % endif
        % if getattr(form, 'show_reset', False):
            <input type="reset" value="Reset" class="button" />
        % endif
        ## TODO: deprecate / remove the latter option here
        % if getattr(form, 'auto_disable_submit', False) or form.auto_disable_save or form.auto_disable:
            <b-button type="is-primary"
                      native-type="submit"
                      :disabled="${form.vue_component}Submitting"
                      icon-pack="fas"
                      icon-left="${form.button_icon_submit}">
              {{ ${form.vue_component}Submitting ? "Working, please wait..." : "${form.button_label_submit}" }}
            </b-button>
        % else:
            <b-button type="is-primary"
                      native-type="submit"
                      icon-pack="fas"
                      icon-left="save">
              ${form.button_label_submit}
            </b-button>
        % endif
      </div>
  % endif

  % if not form.readonly:
  ${h.end_form()}
  % endif

  % if can_edit_help:
      <b-modal has-modal-card
               :active.sync="configureFieldShowDialog">
        <div class="modal-card">

          <header class="modal-card-head">
            <p class="modal-card-title">Field: {{ configureFieldName }}</p>
          </header>

          <section class="modal-card-body">

            <b-field label="Label">
              <b-input v-model="configureFieldLabel" disabled></b-input>
            </b-field>

            <b-field label="Help Text (Markdown)">
              <b-input v-model="configureFieldMarkdown"
                       type="textarea" rows="8"
                       ref="configureFieldMarkdown">
              </b-input>
            </b-field>

          </section>

          <footer class="modal-card-foot">
            <b-button @click="configureFieldShowDialog = false">
              Cancel
            </b-button>
            <b-button type="is-primary"
                      @click="configureFieldSave()"
                      :disabled="configureFieldSaving"
                      icon-pack="fas"
                      icon-left="save">
              {{ configureFieldSaving ? "Working, please wait..." : "Save" }}
            </b-button>
          </footer>
        </div>
      </b-modal>
  % endif

  </div>
</script>

<script type="text/javascript">

  let ${form.vue_component} = {
      template: '#${form.vue_tagname}-template',
      mixins: [FormPosterMixin],
      components: {},
      props: {
          % if can_edit_help:
              configureFieldsHelp: Boolean,
          % endif
      },
      watch: {},
      computed: {},
      methods: {

          ## TODO: deprecate / remove the latter option here
          % if getattr(form, 'auto_disable_submit', False) or form.auto_disable_save or form.auto_disable:
              submit${form.vue_component}() {
                  this.${form.vue_component}Submitting = true
              },
          % endif

          % if can_edit_help:

              configureFieldInit(fieldname) {
                  this.configureFieldName = fieldname
                  this.configureFieldLabel = this.fieldLabels[fieldname]
                  this.configureFieldMarkdown = this.fieldMarkdowns[fieldname]
                  this.configureFieldShowDialog = true
                  this.$nextTick(() => {
                      this.$refs.configureFieldMarkdown.focus()
                  })
              },

              configureFieldSave() {
                  this.configureFieldSaving = true
                  let url = '${edit_help_url}'
                  let params = {
                      field_name: this.configureFieldName,
                      markdown_text: this.configureFieldMarkdown,
                  }
                  this.submitForm(url, params, response => {
                      this.configureFieldShowDialog = false
                      this.$buefy.toast.open({
                          message: "Info was saved; please refresh page to see changes.",
                          type: 'is-info',
                          duration: 4000, // 4 seconds
                      })
                      this.configureFieldSaving = false
                  }, response => {
                      this.configureFieldSaving = false
                  })
              },
          % endif
      }
  }

  let ${form.vue_component}Data = {

      ## TODO: should find a better way to handle CSRF token
      csrftoken: ${json.dumps(h.get_csrf_token(request))|n},

      % if can_edit_help:
          fieldLabels: ${json.dumps(field_labels)|n},
          fieldMarkdowns: ${json.dumps(field_markdowns)|n},
          configureFieldShowDialog: false,
          configureFieldSaving: false,
          configureFieldName: null,
          configureFieldLabel: null,
          configureFieldMarkdown: null,
      % endif

      ## TODO: ugh, this seems pretty hacky.  need to declare some data models
      ## for various field components to bind to...
      % if not form.readonly:
          % for field in form.fields:
              % if field in dform:
                  field_model_${field}: ${json.dumps(form.get_vue_field_value(field))|n},
              % endif
          % endfor
      % endif

      ## TODO: deprecate / remove the latter option here
      % if getattr(form, 'auto_disable_submit', False) or form.auto_disable_save or form.auto_disable:
          ${form.vue_component}Submitting: false,
      % endif
  }

</script>
