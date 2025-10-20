## -*- coding: utf-8; -*-
<%inherit file="/master/view.mako" />
<%namespace file="/util.mako" import="view_profiles_helper" />

<%def name="extra_styles()">
  ${parent.extra_styles()}
  ${h.stylesheet_link(request.static_url('tailbone:static/css/perms.css'))}
</%def>

<%def name="object_helpers()">
  ${parent.object_helpers()}
  % if instance.person:
      ${view_profiles_helper([instance.person])}
  % endif
</%def>

<%def name="render_this_page()">
  ${parent.render_this_page()}

  % if master.has_perm('manage_api_tokens'):

      <b-modal :active.sync="apiNewTokenShowDialog"
               has-modal-card>
        <div class="modal-card">
          <header class="modal-card-head">
            <p class="modal-card-title">
              New API Token
            </p>
          </header>
          <section class="modal-card-body">

            <div v-if="!apiNewTokenSaved">
              <b-field label="Description"
                       :type="{'is-danger': !apiNewTokenDescription}">
                <b-input v-model.trim="apiNewTokenDescription"
                         expanded
                         ref="apiNewTokenDescription">
                </b-input>
              </b-field>
            </div>

            <div v-if="apiNewTokenSaved">
              <p class="block">
                Your new API token is shown below.
              </p>
              <p class="block">
                IMPORTANT:&nbsp; You must record this token elsewhere
                for later reference.&nbsp; You will NOT be able to
                recover the value if you lose it.
              </p>
              <b-field horizontal label="API Token">
                {{ apiNewTokenRaw }}
              </b-field>
              <b-field horizontal label="Description">
                {{ apiNewTokenDescription }}
              </b-field>
            </div>

          </section>
          <footer class="modal-card-foot">
            <b-button @click="apiNewTokenShowDialog = false">
              {{ apiNewTokenSaved ? "Close" : "Cancel" }}
            </b-button>
            <b-button v-if="!apiNewTokenSaved"
                      type="is-primary"
                      icon-pack="fas"
                      icon-left="save"
                      @click="apiNewTokenSave()"
                      :disabled="!apiNewTokenDescription || apiNewTokenSaving">
              Save
            </b-button>
          </footer>
        </div>
      </b-modal>

  % endif
</%def>

<%def name="modify_vue_vars()">
  ${parent.modify_vue_vars()}
  % if master.has_perm('manage_api_tokens'):
    <script>

      ${form.vue_component}.props.apiTokens = null

      ThisPageData.apiTokens = ${json.dumps(api_tokens_data)|n}

      ThisPageData.apiNewTokenShowDialog = false
      ThisPageData.apiNewTokenDescription = null

      ThisPage.methods.apiNewToken = function() {
          this.apiNewTokenDescription = null
          this.apiNewTokenSaved = false
          this.apiNewTokenShowDialog = true
          this.$nextTick(() => {
              this.$refs.apiNewTokenDescription.focus()
          })
      }

      ThisPageData.apiNewTokenSaving = false
      ThisPageData.apiNewTokenSaved = false
      ThisPageData.apiNewTokenRaw = null

      ThisPage.methods.apiNewTokenSave = function() {
          this.apiNewTokenSaving = true

          let url = '${master.get_action_url('add_api_token', instance)}'
          let params = {
              description: this.apiNewTokenDescription,
          }

          this.simplePOST(url, params, response => {
              this.apiTokens = response.data.tokens
              this.apiNewTokenSaving = false
              this.apiNewTokenRaw = response.data.raw_token
              this.apiNewTokenSaved = true
          }, response => {
              this.apiNewTokenSaving = false
          })
      }

      ThisPage.methods.apiTokenDelete = function(token) {
          if (!confirm("Really delete this API token?")) {
              return
          }

          let url = '${master.get_action_url('delete_api_token', instance)}'
          let params = {uuid: token.uuid}
          this.simplePOST(url, params, response => {
              this.apiTokens = response.data.tokens
          })
      }

    </script>
  % endif
</%def>
