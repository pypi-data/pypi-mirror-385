## -*- coding: utf-8; -*-
<%namespace name="base_meta" file="/base_meta.mako" />
<%namespace file="/base.mako" import="core_javascript" />
<%namespace file="/base.mako" import="core_styles" />
<%namespace file="/http-plugin.mako" import="make_http_plugin" />
<!DOCTYPE html>
<html lang="en">
  <head>
    <meta http-equiv="content-type" content="text/html; charset=UTF-8" />
    ${base_meta.favicon()}
    <title>${initial_msg or "Working"}...</title>
    ${core_javascript()}
    ${core_styles()}
    ${self.extra_styles()}
  </head>

  <body>
    <div id="app" style="height: 100%; display: flex; flex-direction: column; justify-content: space-between;">
      <whole-page></whole-page>
    </div>

    ${make_http_plugin()}
    ${self.make_whole_page_component()}
    ${self.modify_whole_page_vars()}
    ${self.make_whole_page_app()}
  </body>
</html>

<%def name="extra_styles()"></%def>

<%def name="make_whole_page_component()">
  <script type="text/x-template" id="whole-page-template">
    <section class="hero is-fullheight">
      <div class="hero-body">
        <div class="container">

          <div style="display: flex; flex-direction: column; justify-content: center;">
            <div style="margin: auto; display: flex; gap: 1rem; align-items: end;">

              <div style="display: flex; flex-direction: column; gap: 1rem;">

                <div style="display: flex; gap: 3rem;">
                  <span>{{ progressMessage }} ... {{ totalDisplay }}</span>
                  <span>{{ percentageDisplay }}</span>
                </div>

                <div style="display: flex; gap: 1rem; align-items: center;">

                  <div>
                    <progress class="progress is-large"
                              style="width: 400px;"
                              :max="progressMax"
                              :value="progressValue" />
                  </div>

                  % if can_cancel:
                      <o-button v-show="canCancel"
                                @click="cancelProgress()"
                                :disabled="cancelingProgress"
                                icon-left="ban">
                        {{ cancelingProgress ? "Canceling, please wait..." : "Cancel" }}
                      </o-button>
                  % endif

                </div>
              </div>

            </div>
          </div>

          ${self.after_progress()}

        </div>
      </div>
    </section>
  </script>
  <script>

    const WholePage = {
        template: '#whole-page-template',

        computed: {

            percentageDisplay() {
                if (!this.progressMax) {
                    return
                }

                const percent = this.progressValue / this.progressMax
                return percent.toLocaleString(undefined, {
                    style: 'percent',
                    minimumFractionDigits: 0})
            },

            totalDisplay() {

                % if can_cancel:
                    if (!this.stillInProgress && !this.cancelingProgress) {
                        return "done!"
                    }
                % else:
                    if (!this.stillInProgress) {
                        return "done!"
                    }
                % endif

                if (this.progressMaxDisplay) {
                    return `(${'$'}{this.progressMaxDisplay} total)`
                }
            },
        },

        mounted() {

            // fetch first progress data, one second from now
            setTimeout(() => {
                this.updateProgress()
            }, 1000)

            // custom logic if applicable
            this.mountedCustom()
        },

        methods: {

            mountedCustom() {},

            updateProgress() {

                this.$http.get(this.progressURL).then(response => {

                    if (response.data.error) {
                        // errors stop the show, we redirect to "cancel" page
                        location.href = '${cancel_url}'

                    } else {

                        if (response.data.complete || response.data.maximum) {
                            this.progressMessage = response.data.message
                            this.progressMaxDisplay = response.data.maximum_display

                            if (response.data.complete) {
                                this.progressValue = this.progressMax
                                this.stillInProgress = false
                                % if can_cancel:
                                this.canCancel = false
                                % endif

                                location.href = response.data.success_url

                            } else {
                                this.progressValue = response.data.value
                                this.progressMax = response.data.maximum
                            }
                        }

                        // custom logic if applicable
                        this.updateProgressCustom(response)

                        if (this.stillInProgress) {

                            // fetch progress data again, in one second from now
                            setTimeout(() => {
                                this.updateProgress()
                            }, 1000)
                        }
                    }
                })
            },

            updateProgressCustom(response) {},

            % if can_cancel:

                cancelProgress() {

                    if (confirm("Do you really wish to cancel this operation?")) {

                        this.cancelingProgress = true
                        this.stillInProgress = false

                        let params = {cancel_msg: ${json.dumps(cancel_msg)|n}}
                        this.$http.get(this.cancelURL, {params: params}).then(response => {
                            location.href = ${json.dumps(cancel_url)|n}
                        })
                    }

                },

            % endif
        }
    }

    const WholePageData = {

        progressURL: '${url('progress', key=progress.key, _query={'sessiontype': progress.session.type})}',
        progressMessage: "${(initial_msg or "Working").replace('"', '\\"')} (please wait)",
        progressMax: null,
        progressMaxDisplay: null,
        progressValue: null,
        stillInProgress: true,

        % if can_cancel:
        canCancel: true,
        cancelURL: '${url('progress.cancel', key=progress.key, _query={'sessiontype': progress.session.type})}',
        cancelingProgress: false,
        % endif
    }

  </script>
</%def>

<%def name="after_progress()"></%def>

<%def name="modify_whole_page_vars()"></%def>

<%def name="make_whole_page_app()">
  <script type="module">
    import {createApp} from 'vue'
    import {Oruga} from '@oruga-ui/oruga-next'
    import {bulmaConfig} from '@oruga-ui/theme-bulma'
    import { library } from "@fortawesome/fontawesome-svg-core"
    import { fas } from "@fortawesome/free-solid-svg-icons"
    import { FontAwesomeIcon } from "@fortawesome/vue-fontawesome"
    library.add(fas)

    const app = createApp()

    app.component('vue-fontawesome', FontAwesomeIcon)

    WholePage.data = () => { return WholePageData }
    app.component('whole-page', WholePage)

    app.use(Oruga, {
        ...bulmaConfig,
        iconComponent: 'vue-fontawesome',
        iconPack: 'fas',
    })

    app.use(HttpPlugin)

    app.mount('#app')
  </script>
</%def>
