## -*- coding: utf-8; -*-
<%inherit file="/master/index.mako" />

<%def name="grid_tools()">
  ${parent.grid_tools()}

  ## Refresh Results
  % if master.results_refreshable and master.has_perm('refresh'):
      <b-button type="is-primary"
                :disabled="refreshResultsButtonDisabled"
                icon-pack="fas"
                icon-left="redo"
                @click="refreshResults()">
        {{ refreshResultsButtonText }}
      </b-button>
      ${h.form(url('{}.refresh_results'.format(route_prefix)), ref='refreshResultsForm')}
      ${h.csrf_token(request)}
      ${h.end_form()}
  % endif

  ## Execute Results
  % if master.results_executable and master.has_perm('execute_multiple'):
      <b-button type="is-primary"
                @click="executeResults()"
                icon-pack="fas"
                icon-left="arrow-circle-right"
                :disabled="!total">
        Execute Results
      </b-button>

      <b-modal has-modal-card
               :active.sync="showExecutionOptions">
        <div class="modal-card">

          <header class="modal-card-head">
            <p class="modal-card-title">Execution Options</p>
          </header>

          <section class="modal-card-body">
            <p>
              Please be advised, you are about to execute {{ total }} batches!
            </p>
            <br />
            <div class="form-wrapper">
              <div class="form">
                ${execute_form.render_vue_tag(ref='executeResultsForm')}
              </div>
            </div>
          </section>

          <footer class="modal-card-foot">
            <b-button @click="showExecutionOptions = false">
              Cancel
            </b-button>
            <once-button type="is-primary"
                         @click="submitExecuteResults()"
                         icon-left="arrow-circle-right"
                         :text="'Execute ' + total + ' Batches'">
            </once-button>
          </footer>

        </div>
      </b-modal>
  % endif
</%def>

<%def name="render_vue_templates()">
  ${parent.render_vue_templates()}
  % if master.results_executable and master.has_perm('execute_multiple'):
      ${execute_form.render_vue_template(form_kwargs={'ref': 'actualExecuteForm'}, buttons=False)}
  % endif
</%def>

<%def name="modify_vue_vars()">
  ${parent.modify_vue_vars()}
  % if master.results_refreshable and master.has_perm('refresh'):
      <script>

        TailboneGridData.refreshResultsButtonText = "Refresh Results"
        TailboneGridData.refreshResultsButtonDisabled = false

        TailboneGrid.methods.refreshResults = function() {
            this.refreshResultsButtonDisabled = true
            this.refreshResultsButtonText = "Working, please wait..."
            this.$refs.refreshResultsForm.submit()
        }

      </script>
  % endif
  % if master.results_executable and master.has_perm('execute_multiple'):
      <script>

        ${execute_form.vue_component}.methods.submit = function() {
            this.$refs.actualExecuteForm.submit()
        }

        TailboneGridData.hasExecutionOptions = ${json.dumps(master.has_execution_options(batch))|n}
        TailboneGridData.showExecutionOptions = false

        TailboneGrid.methods.executeResults = function() {

            // this should never happen since we disable the button when there are no results
            if (!this.total) {
                alert("There are no batch results to execute.")
                return
            }

            if (this.hasExecutionOptions) {
                // show execution options modal, user can submit form from there
                this.showExecutionOptions = true

            } else {
                // no execution options, but this still warrants a basic confirmation
                if (confirm("Are you sure you wish to execute all " + this.total.toLocaleString('en') + " batches?")) {
                    alert('TODO: ok then you asked for it')
                }
            }
        }

        TailboneGrid.methods.submitExecuteResults = function() {
            this.$refs.executeResultsForm.submit()
        }

      </script>
  % endif
</%def>

<%def name="make_vue_components()">
  ${parent.make_vue_components()}
  % if master.results_executable and master.has_perm('execute_multiple'):
      ${execute_form.render_vue_finalize()}
  % endif
</%def>
