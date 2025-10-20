## -*- coding: utf-8; -*-
<%inherit file="/master/view.mako" />

<%def name="extra_styles()">
  ${parent.extra_styles()}
  % if master.has_perm('execute'):
      <style type="text/css">
        .progress-with-textout {
            border: 1px solid Black;
            line-height: 1.2;
            overflow: auto;
            padding: 1rem;
        }
      </style>
  % endif
</%def>

<%def name="render_this_page()">
  ${parent.render_this_page()}

  % if expose_websockets and master.has_perm('execute'):
      <${b}-modal full-screen
                  % if request.use_oruga:
                      v-model:active="upgradeExecuting"
                      :cancelable="false"
                  % else:
                      :active.sync="upgradeExecuting"
                      :can-cancel="false"
                  % endif
                  >
        <div class="card">
          <div class="card-content">

            <div class="level">
              <div class="level-item has-text-centered"
                   style="display: flex; flex-direction: column;">
                <p class="block">
                  Upgrading ${system_title} (please wait) ...
                  {{ executeUpgradeComplete ? "DONE!" : "" }}
                </p>
                % if request.use_oruga:
                    <progress class="progress is-large"
                              style="width: 400px;" />
                % else:
                <b-progress size="is-large"
                            style="width: 400px;"
    ##                             :value="80"
    ##                             show-value
    ##                             format="percent"
                            >
                </b-progress>
                % endif
              </div>
              <div class="level-right">
                <div class="level-item">
                  <b-button type="is-warning"
                            icon-pack="fas"
                            icon-left="sad-tear"
                            @click="declareFailureClick()">
                    Declare Failure
                  </b-button>
                </div>
              </div>
            </div>

            <div class="container progress-with-textout is-family-monospace is-size-7"
                 ref="textout">
              <span v-for="line in progressOutput"
                    :key="line.key"
                    v-html="line.text">
              </span>

              ## nb. we auto-scroll down to "see" this element
              <div ref="seeme"></div>
            </div>

          </div>
        </div>
      </${b}-modal>
  % endif

  % if master.has_perm('execute'):
      ${h.form(master.get_action_url('declare_failure', instance), ref='declareFailureForm')}
      ${h.csrf_token(request)}
      ${h.end_form()}
  % endif
</%def>

<%def name="render_form()">
  <div class="form">
    <${form.component}
      % if master.has_perm('execute'):
      @declare-failure-click="declareFailureClick"
      :declare-failure-submitting="declareFailureSubmitting"
      % if expose_websockets:
      % if instance_executable:
      @execute-upgrade-click="executeUpgrade"
      % endif
      :upgrade-executing="upgradeExecuting"
      % endif
      % endif
      >
    </${form.component}>
  </div>
</%def>

<%def name="render_form_buttons()">
  % if instance_executable and master.has_perm('execute'):
      <div class="buttons">
        % if instance.enabled and not instance.executing:
            % if expose_websockets:
                <b-button type="is-primary"
                          icon-pack="fas"
                          icon-left="arrow-circle-right"
                          :disabled="upgradeExecuting"
                          @click="$emit('execute-upgrade-click')">
                  {{ upgradeExecuting ? "Working, please wait..." : "Execute this upgrade" }}
                </b-button>
            % else:
                ${h.form(url('{}.execute'.format(route_prefix), uuid=instance.uuid), **{'@submit': 'submitForm'})}
                ${h.csrf_token(request)}
                <b-button type="is-primary"
                          native-type="submit"
                          icon-pack="fas"
                          icon-left="arrow-circle-right"
                          :disabled="formSubmitting">
                  {{ formSubmitting ? "Working, please wait..." : "Execute this upgrade" }}
                </b-button>
                ${h.end_form()}
            % endif
        % elif instance.enabled:
            <button type="button" class="button is-primary" disabled="disabled" title="This upgrade is currently executing">Execute this upgrade</button>
        % else:
            <button type="button" class="button is-primary" disabled="disabled" title="This upgrade is not enabled">Execute this upgrade</button>
        % endif
      </div>
  % endif
</%def>

<%def name="modify_vue_vars()">
  ${parent.modify_vue_vars()}
  <script>

    ${form.vue_component}Data.showingPackages = 'diffs'

    % if master.has_perm('execute'):

        % if expose_websockets:

            ThisPageData.ws = null

            //////////////////////////////
            // execute upgrade
            //////////////////////////////

            ${form.vue_component}.props.upgradeExecuting = {
                type: Boolean,
                default: false,
            }

            ThisPageData.upgradeExecuting = false
            ThisPageData.progressOutput = []
            ThisPageData.progressOutputCounter = 0
            ThisPageData.executeUpgradeComplete = false

            ThisPage.methods.adjustTextoutHeight = function() {

                // grow the textout area to fill most of screen
                let textout = this.$refs.textout
                let height = window.innerHeight - textout.offsetTop - 50
                textout.style.height = height + 'px'
            }

            ThisPage.methods.showExecuteDialog = function() {
                this.upgradeExecuting = true
                document.title = "Upgrading ${system_title} ..."
                this.$nextTick(() => {
                    this.adjustTextoutHeight()
                })
            }

            ThisPage.methods.establishWebsocket = function() {

                ## TODO: should be a cleaner way to get this url?
                let url = '${url('ws.upgrades.execution_progress', _query={'uuid': instance.uuid})}'
                url = url.replace(/^http(s?):/, 'ws$1:')

                this.ws = new WebSocket(url)

                ## TODO: add support for this here?
                // this.ws.onclose = (event) => {
                //     // websocket closing means 1 of 2 things:
                //     // - user navigated away from page intentionally
                //     // - server connection was broken somehow
                //     // only one of those is "bad" and we only want to
                //     // display warning in 2nd case.  so we simply use a
                //     // brief delay to "rule out" the 1st scenario
                //     setTimeout(() => { that.websocketBroken = true },
                //                3000)
                // }

                this.ws.onmessage = (event) => {
                    let data = JSON.parse(event.data)

                    if (data.complete) {

                        // upgrade has completed; reload page to view result
                        this.executeUpgradeComplete = true
                        this.$nextTick(() => {
                            location.reload()
                        })

                    } else if (data.stdout) {

                        // add lines to textout area
                        this.progressOutput.push({
                            key: ++this.progressOutputCounter,
                            text: data.stdout})

                        //  scroll down to end of textout area
                        this.$nextTick(() => {
                            this.$refs.seeme.scrollIntoView({behavior: 'smooth'})
                        })
                    }
                }
            }

            % if instance.executing:
                ThisPage.mounted = function() {
                    this.showExecuteDialog()
                    this.establishWebsocket()
                }
            % endif

            % if instance_executable:

                ThisPage.methods.executeUpgrade = function() {
                    this.showExecuteDialog()

                    let url = '${master.get_action_url('execute', instance)}'
                    this.submitForm(url, {ws: true}, response => {

                        this.establishWebsocket()
                    })
                }

            % endif

        % else:
            ## no websockets

            //////////////////////////////
            // execute upgrade
            //////////////////////////////

            ${form.vue_component}Data.formSubmitting = false

            ${form.vue_component}.methods.submitForm = function() {
                this.formSubmitting = true
            }

        % endif

        //////////////////////////////
        // declare failure
        //////////////////////////////

        ${form.vue_component}.props.declareFailureSubmitting = {
            type: Boolean,
            default: false,
        }

        ${form.vue_component}.methods.declareFailureClick = function() {
            this.$emit('declare-failure-click')
        }

        ThisPageData.declareFailureSubmitting = false

        ThisPage.methods.declareFailureClick = function() {
            if (confirm("Really declare this upgrade a failure?")) {
                this.declareFailureSubmitting = true
                this.$refs.declareFailureForm.submit()
            }
        }

    % endif

  </script>
</%def>
