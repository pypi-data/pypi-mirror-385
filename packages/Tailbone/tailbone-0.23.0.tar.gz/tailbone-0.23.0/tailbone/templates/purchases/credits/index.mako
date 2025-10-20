## -*- coding: utf-8; -*-
<%inherit file="/master/index.mako" />

<%def name="grid_tools()">
  ${parent.grid_tools()}

  <b-button type="is-primary"
            @click="changeStatusInit()"
            :disabled="!selected_uuids.length">
    Change Status
  </b-button>

  <b-modal has-modal-card
           :active.sync="changeStatusShowDialog">
    <div class="modal-card">

      <header class="modal-card-head">
        <p class="modal-card-title">Change Status</p>
      </header>

      <section class="modal-card-body">

        <p class="block">
          Please choose the appropriate status for the selected credits.
        </p>

        <b-field label="Status">
          <b-select v-model="changeStatusValue">
            <option v-for="status in changeStatusOptions"
                    :key="status.value"
                    :value="status.value">
              {{ status.label }}
            </option>
          </b-select>
        </b-field>

      </section>

      <footer class="modal-card-foot">
        <b-button @click="changeStatusShowDialog = false">
          Cancel
        </b-button>
        <b-button type="is-primary"
                  @click="changeStatusSubmit()"
                  :disabled="changeStatusSubmitting || !changeStatusValue"
                  icon-pack="fas"
                  icon-left="save">
          {{ changeStatusSubmitting ? "Working, please wait..." : "Save" }}
        </b-button>
      </footer>
    </div>
  </b-modal>

  ${h.form(url('purchases.credits.change_status'), ref='changeStatusForm')}
  ${h.csrf_token(request)}
  ${h.hidden('uuids', **{':value': 'selected_uuids'})}
  ${h.hidden('status', **{':value': 'changeStatusValue'})}
  ${h.end_form()}

</%def>

<%def name="modify_vue_vars()">
  ${parent.modify_vue_vars()}
  <script>

    ${grid.vue_component}Data.changeStatusShowDialog = false
    ${grid.vue_component}Data.changeStatusOptions = ${json.dumps(status_options)|n}
    ${grid.vue_component}Data.changeStatusValue = null
    ${grid.vue_component}Data.changeStatusSubmitting = false

    ${grid.vue_component}.methods.changeStatusInit = function() {
        this.changeStatusValue = null
        this.changeStatusShowDialog = true
    }

    ${grid.vue_component}.methods.changeStatusSubmit = function() {
        this.changeStatusSubmitting = true
        this.$refs.changeStatusForm.submit()
    }

  </script>
</%def>
