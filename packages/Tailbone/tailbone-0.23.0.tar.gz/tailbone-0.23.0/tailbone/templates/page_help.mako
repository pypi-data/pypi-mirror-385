## -*- coding: utf-8; -*-

<%def name="render_template()">
  <script type="text/x-template" id="page-help-template">
    <div>

      % if help_url or help_markdown:

          % if request.use_oruga:
              <o-button icon-left="question-circle"
                        % if help_markdown:
                        @click="displayInit()"
                        % elif help_url:
                        tag="a" href="${help_url}"
                        target="_blank"
                        % endif
                        >
                Help
              </o-button>

              % if can_edit_help:
                  ## TODO: this dropdown is duplicated, below
                  <o-dropdown position="bottom-left"
                              ## TODO: why does click not work here?!
                              :triggers="['click', 'hover']">
                    <template #trigger>
                      <o-button>
                        <o-icon icon="cog" />
                      </o-button>
                    </template>
                    <o-dropdown-item label="Edit Page Help"
                                     @click="configureInit()" />
                    <o-dropdown-item label="Edit Fields Help"
                                     @click="configureFieldsInit()" />
                  </o-dropdown>
              % endif

          % else:
              ## buefy
              <b-field>
                <p class="control">
                  <b-button icon-pack="fas"
                            icon-left="question-circle"
                            % if help_markdown:
                            @click="displayInit()"
                            % elif help_url:
                            tag="a" href="${help_url}"
                            target="_blank"
                            % endif
                            >
                    Help
                  </b-button>
                </p>
                % if can_edit_help:
                    ## TODO: this dropdown is duplicated, below
                    <b-dropdown aria-role="list"  position="is-bottom-left">
                      <template #trigger="{ active }">
                        <b-button>
                          <span><i class="fa fa-cog"></i></span>
                        </b-button>
                      </template>
                      <b-dropdown-item aria-role="listitem"
                                       @click="configureInit()">
                        Edit Page Help
                      </b-dropdown-item>
                      <b-dropdown-item aria-role="listitem"
                                       @click="configureFieldsInit()">
                        Edit Fields Help
                      </b-dropdown-item>
                    </b-dropdown>
                % endif
              </b-field>
          % endif:

      % elif can_edit_help:

          ## TODO: this dropdown is duplicated, above
          % if request.use_oruga:
              <o-dropdown position="bottom-left"
                          ## TODO: why does click not work here?!
                          :triggers="['click', 'hover']">
                <template #trigger>
                  <o-button>
                    <o-icon icon="question-circle" />
                    <o-icon icon="cog" />
                  </o-button>
                </template>
                <o-dropdown-item label="Edit Page Help"
                                 @click="configureInit()" />
                <o-dropdown-item label="Edit Fields Help"
                                 @click="configureFieldsInit()" />
              </o-dropdown>
          % else:
              <b-field>
                <p class="control">
                  <b-dropdown aria-role="list"  position="is-bottom-left">
                    <template #trigger>
                      <b-button>
                        % if request.use_oruga:
                            <o-icon icon="question-circle" />
                            <o-icon icon="cog" />
                        % else:
                        <span><i class="fa fa-question-circle"></i></span>
                        <span><i class="fa fa-cog"></i></span>
                        % endif
                      </b-button>
                    </template>
                    <b-dropdown-item aria-role="listitem"
                                     @click="configureInit()">
                      Edit Page Help
                    </b-dropdown-item>
                    <b-dropdown-item aria-role="listitem"
                                     @click="configureFieldsInit()">
                      Edit Fields Help
                    </b-dropdown-item>
                  </b-dropdown>
                </p>
              </b-field>
          % endif
      % endif

      % if help_markdown:
          <${b}-modal has-modal-card
                      % if request.use_oruga:
                      v-model:active="displayShowDialog"
                      % else:
                      :active.sync="displayShowDialog"
                      % endif
                      >
            <div class="modal-card">

              <header class="modal-card-head">
                <p class="modal-card-title">${index_title}</p>
              </header>

              <section class="modal-card-body">
                ${h.render_markdown(help_markdown)}
              </section>

              <footer class="modal-card-foot">
                % if help_url:
                    <b-button type="is-primary"
                              icon-pack="fas"
                              icon-left="external-link-alt"
                              tag="a" href="${help_url}"
                              target="_blank">
                      More Info
                    </b-button>
                % endif
                <b-button @click="displayShowDialog = false">
                  Close
                </b-button>
              </footer>
            </div>
          </${b}-modal>
      % endif

      % if can_edit_help:

          <${b}-modal has-modal-card
                      % if request.use_oruga:
                      v-model:active="configureShowDialog"
                      % else:
                      :active.sync="configureShowDialog"
                      % endif
                      >
            <div class="modal-card"
                 % if request.use_oruga:
                 style="margin: auto;"
                 % endif
                 >

              <header class="modal-card-head">
                <p class="modal-card-title">Configure Help</p>
              </header>

              <section class="modal-card-body">

                <p class="block">
                  This help info applies to all views with the current
                  route prefix.
                </p>

                <b-field grouped>

                  <b-field label="Route Prefix">
                    <span>${route_prefix}</span>
                  </b-field>

                  <b-field label="URL Prefix">
                    <span>${master.get_url_prefix()}</span>
                  </b-field>

                </b-field>

                <b-field label="Help Link (URL)">
                  <b-input v-model="helpURL"
                           ref="helpURL"
                           expanded>
                  </b-input>
                </b-field>

                <b-field label="Help Text (Markdown)">
                  <b-input v-model="markdownText"
                           type="textarea" rows="8"
                           expanded>
                  </b-input>
                </b-field>

              </section>

              <footer class="modal-card-foot">
                <b-button @click="configureShowDialog = false">
                  Cancel
                </b-button>
                <b-button type="is-primary"
                          @click="configureSave()"
                          :disabled="configureSaving"
                          icon-pack="fas"
                          icon-left="save">
                  {{ configureSaving ? "Working, please wait..." : "Save" }}
                </b-button>
              </footer>
            </div>
          </${b}-modal>

      % endif

    </div>
  </script>
</%def>

<%def name="declare_vars()">
  <script type="text/javascript">

    let PageHelp = {

        template: '#page-help-template',
        mixins: [FormPosterMixin],

        methods: {

            displayInit() {
                this.displayShowDialog = true
            },

            % if can_edit_help:
            configureInit() {
                this.configureShowDialog = true
                this.$nextTick(() => {
                    this.$refs.helpURL.focus()
                })
            },

            configureFieldsInit() {
                this.$emit('configure-fields-help')
                this.$buefy.toast.open({
                    message: "Please see the gear icon next to configurable fields",
                    type: 'is-info',
                    duration: 4000, // 4 seconds
                })
            },

            configureSave() {
                this.configureSaving = true
                let url = '${url('{}.edit_help'.format(route_prefix))}'
                let params = {
                    help_url: this.helpURL,
                    markdown_text: this.markdownText,
                }
                this.submitForm(url, params, response => {
                    this.configureShowDialog = false
                    this.$buefy.toast.open({
                        message: "Info was saved; please refresh page to see changes.",
                        type: 'is-info',
                        duration: 4000, // 4 seconds
                    })
                    this.configureSaving = false
                }, response => {
                    this.configureSaving = false
                })
            },
            % endif
        },
    }

    let PageHelpData = {
        displayShowDialog: false,

        % if can_edit_help:
        configureShowDialog: false,
        configureSaving: false,
        helpURL: ${json.dumps(help_url or None)|n},
        markdownText: ${json.dumps(help_markdown or None)|n},
        % endif
    }

  </script>
</%def>

<%def name="make_component()">
  <script type="text/javascript">

    PageHelp.data = function() { return PageHelpData }

    Vue.component('page-help', PageHelp)
    <% request.register_component('page-help', 'PageHelp') %>

  </script>
</%def>
