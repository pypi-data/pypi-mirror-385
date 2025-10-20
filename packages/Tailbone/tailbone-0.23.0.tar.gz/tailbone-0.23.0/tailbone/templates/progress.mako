## -*- coding: utf-8; -*-
<%namespace file="/base.mako" import="core_javascript" />
<%namespace file="/base.mako" import="core_styles" />
<!DOCTYPE html>
<html lang="en">
  <head>
    <meta http-equiv="content-type" content="text/html; charset=UTF-8" />
    <title>${initial_msg or "Working"}...</title>
    ${core_javascript()}
    ${core_styles()}
    ${self.extra_styles()}
  </head>
  <body style="height: 100%;">

    <div id="whole-page-app">
      <whole-page></whole-page>
    </div>

    <script type="text/x-template" id="whole-page-template">

      <section class="hero is-fullheight">
        <div class="hero-body">
          <div class="container">

            <div style="display: flex;">
              <div style="flex-grow: 1;"></div>
              <div>

                <p class="block">
                  {{ progressMessage }} ... {{ totalDisplay }}
                </p>

                <div class="level">

                  <div class="level-item">
                    <b-progress size="is-large"
                                style="width: 400px;"
                                :max="progressMax"
                                :value="progressValue"
                                show-value
                                format="percent"
                                precision="0">
                    </b-progress>
                  </div>

                  % if can_cancel:
                      <div class="level-item"
                           style="margin-left: 2rem;">
                        <b-button v-show="canCancel"
                                  @click="cancelProgress()"
                                  :disabled="cancelingProgress"
                                  icon-pack="fas"
                                  icon-left="ban">
                          {{ cancelingProgress ? "Canceling, please wait..." : "Cancel" }}
                        </b-button>
                      </div>
                  % endif

                </div>

              </div>
              <div style="flex-grow: 1;"></div>
            </div>

            ${self.after_progress()}

          </div>
        </div>
      </section>

    </script>

    <script type="text/javascript">

      let WholePage = {
          template: '#whole-page-template',

          computed: {

              totalDisplay() {

                  % if can_cancel:
                  if (!this.stillInProgress && !this.cancelingProgress) {
                  % else:
                  if (!this.stillInProgress) {
                  % endif
                      return "done!"
                  }

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

      let WholePageData = {

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

    ${self.modify_whole_page_vars()}
    ${self.make_whole_page_app()}

  </body>
</html>

<%def name="extra_styles()"></%def>

<%def name="after_progress()"></%def>

<%def name="modify_whole_page_vars()"></%def>

<%def name="make_whole_page_app()">
  <script type="text/javascript">

    WholePage.data = function() { return WholePageData }

    Vue.component('whole-page', WholePage)

    new Vue({
        el: '#whole-page-app'
    })

  </script>
</%def>
