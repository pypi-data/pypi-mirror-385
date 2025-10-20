## -*- coding: utf-8; -*-
<%inherit file="/master/index.mako" />

<%def name="grid_tools()">

  % if getattr(master, 'mergeable', False) and master.has_perm('request_merge'):
      <b-button @click="showMergeRequest()"
                icon-pack="fas"
                icon-left="object-ungroup"
                :disabled="checkedRows.length != 2">
        Request Merge
      </b-button>
      <b-modal has-modal-card
               :active.sync="mergeRequestShowDialog">
        <div class="modal-card">

          <header class="modal-card-head">
            <p class="modal-card-title">Request Merge of 2 People</p>
          </header>

          <section class="modal-card-body">
            <b-table :data="mergeRequestRows"
                     striped hoverable>
              <b-table-column field="customer_number"
                              label="Customer #"
                              v-slot="props">
                <span v-html="props.row.customer_number"></span>
              </b-table-column>
              <b-table-column field="first_name"
                              label="First Name"
                              v-slot="props">
                <span v-html="props.row.first_name"></span>
              </b-table-column>
              <b-table-column field="last_name"
                              label="Last Name"
                              v-slot="props">
                <span v-html="props.row.last_name"></span>
              </b-table-column>
            </b-table>
          </section>

          <footer class="modal-card-foot">
            <b-button @click="mergeRequestShowDialog = false">
              Cancel
            </b-button>
            ${h.form(url('{}.request_merge'.format(route_prefix)), **{'@submit': 'submitMergeRequest'})}
            ${h.csrf_token(request)}
            ${h.hidden('removing_uuid', **{':value': 'mergeRequestRemovingUUID'})}
            ${h.hidden('keeping_uuid', **{':value': 'mergeRequestKeepingUUID'})}
            <b-button type="is-primary"
                      native-type="submit"
                      :disabled="mergeRequestSubmitting">
              {{ mergeRequestSubmitText }}
            </b-button>
            ${h.end_form()}
          </footer>
        </div>
      </b-modal>
  % endif

  ${parent.grid_tools()}
</%def>

<%def name="modify_vue_vars()">
  ${parent.modify_vue_vars()}
  <script>

    % if getattr(master, 'mergeable', False) and master.has_perm('request_merge'):

        ${grid.vue_component}Data.mergeRequestShowDialog = false
        ${grid.vue_component}Data.mergeRequestRows = []
        ${grid.vue_component}Data.mergeRequestSubmitText = "Submit Merge Request"
        ${grid.vue_component}Data.mergeRequestSubmitting = false

        ${grid.vue_component}.computed.mergeRequestRemovingUUID = function() {
            if (this.mergeRequestRows.length) {
                return this.mergeRequestRows[0].uuid
            }
            return null
        }

        ${grid.vue_component}.computed.mergeRequestKeepingUUID = function() {
            if (this.mergeRequestRows.length) {
                return this.mergeRequestRows[1].uuid
            }
            return null
        }

        ${grid.vue_component}.methods.showMergeRequest = function() {
            this.mergeRequestRows = this.checkedRows
            this.mergeRequestShowDialog = true
        }

        ${grid.vue_component}.methods.submitMergeRequest = function() {
            this.mergeRequestSubmitting = true
            this.mergeRequestSubmitText = "Working, please wait..."
        }

    % endif

  </script>
</%def>
