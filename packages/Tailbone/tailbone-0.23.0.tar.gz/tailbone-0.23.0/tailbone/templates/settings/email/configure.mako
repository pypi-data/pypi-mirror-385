## -*- coding: utf-8; -*-
<%inherit file="/configure.mako" />

<%def name="form_content()">

  <h3 class="block is-size-3">General</h3>
  <div class="block" style="padding-left: 2rem;">
    <b-field label="Mail Handler"
             message="Leave blank for default handler.">
      <b-input name="rattail.mail.handler"
               v-model="simpleSettings['rattail.mail.handler']"
               @input="settingsNeedSaved = true">
      </b-input>
    </b-field>
    <b-field label="Template Paths"
             message="Leave blank for default paths.">
      <b-input name="rattail.mail.templates"
               v-model="simpleSettings['rattail.mail.templates']"
               @input="settingsNeedSaved = true">
      </b-input>
    </b-field>
  </div>

  <h3 class="block is-size-3">Sending</h3>
  <div class="block" style="padding-left: 2rem;">

    <b-field>
      <b-checkbox name="rattail.mail.record_attempts"
                  v-model="simpleSettings['rattail.mail.record_attempts']"
                  native-value="true"
                  @input="settingsNeedSaved = true">
        Make record of all attempts to send email
      </b-checkbox>
    </b-field>

    <b-field>
      <b-checkbox name="rattail.mail.send_email_on_failure"
                  v-model="simpleSettings['rattail.mail.send_email_on_failure']"
                  native-value="true"
                  @input="settingsNeedSaved = true">
        When sending an email fails, send another to report the failure
      </b-checkbox>
    </b-field>

  </div>

  <h3 class="block is-size-3">Testing</h3>
  <div class="block" style="padding-left: 2rem;">

    <b-field grouped>
      <b-field horizontal label="Recipient">
        <b-input v-model="testRecipient"></b-input>
      </b-field>
      <b-button type="is-primary"
                @click="sendTest()"
                :disabled="sendingTest">
        {{ sendingTest ? "Working, please wait..." : "Send Test Email" }}
      </b-button>
    </b-field>

    <div class="level">
      <div class="level-left">
        <div class="level-item">
          <p>You can raise a "bogus" error to test if/how that generates email:</p>
        </div>
        <div class="level-item">
          <b-button type="is-primary"
                    % if request.has_perm('errors.bogus'):
                    @click="raiseBogusError()"
                    :disabled="raisingBogusError"
                    % else:
                    disabled
                    title="your permissions do not allow this"
                    % endif
                    >
            % if request.has_perm('errors.bogus'):
            {{ raisingBogusError ? "Working, please wait..." : "Raise Bogus Error" }}
            % else:
            Raise Bogus Error
            % endif
          </b-button>
        </div>
      </div>
    </div>

  </div>
</%def>

<%def name="modify_vue_vars()">
  ${parent.modify_vue_vars()}
  <script>

    ThisPageData.testRecipient = ${json.dumps(user_email_address)|n}
    ThisPageData.sendingTest = false

    ThisPage.methods.sendTest = function() {
        this.sendingTest = true
        let url = '${url('emailprofiles.send_test')}'
        let params = {recipient: this.testRecipient}
        this.simplePOST(url, params, response => {
            this.$buefy.toast.open({
                message: "Test email was sent!",
                type: 'is-success',
                duration: 4000, // 4 seconds
            })
            this.sendingTest = false
        }, response => {
            this.sendingTest = false
        })
    }

    % if request.has_perm('errors.bogus'):

        ThisPageData.raisingBogusError = false

        ThisPage.methods.raiseBogusError = function() {
            this.raisingBogusError = true

            let url = '${url('bogus_error')}'
            this.$http.get(url).then(response => {
                this.$buefy.toast.open({
                    message: "Ironically, response was 200 which means we failed to raise an error!\n\nPlease investigate!",
                    type: 'is-danger',
                    duration: 5000, // 5 seconds
                })
                this.raisingBogusError = false
            }, response => {
                this.$buefy.toast.open({
                    message: "Error was raised; please check your email and/or logs.",
                    type: 'is-success',
                    duration: 4000, // 4 seconds
                })
                this.raisingBogusError = false
            })
        }

    % endif
  </script>
</%def>
