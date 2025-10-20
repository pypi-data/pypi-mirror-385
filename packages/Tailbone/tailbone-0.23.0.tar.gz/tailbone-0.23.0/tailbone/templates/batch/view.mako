## -*- coding: utf-8; -*-
<%inherit file="/master/view.mako" />

<%def name="extra_styles()">
  ${parent.extra_styles()}
  <style type="text/css">

    .modal-card-body label {
        white-space: nowrap;
    }

    .markdown p {
        margin-bottom: 1.5rem;
    }

  </style>
</%def>

<%def name="buttons()">
    <div class="buttons">
      ${self.leading_buttons()}
      ${refresh_button()}
      ${self.trailing_buttons()}
    </div>
</%def>

<%def name="leading_buttons()">
  % if master.has_worksheet and master.allow_worksheet(batch) and master.has_perm('worksheet'):
      <once-button type="is-primary"
                   tag="a" href="${url('{}.worksheet'.format(route_prefix), uuid=batch.uuid)}"
                   icon-left="edit"
                   text="Edit as Worksheet">
      </once-button>
  % endif
</%def>

<%def name="refresh_button()">
  % if master.batch_refreshable(batch) and master.has_perm('refresh'):
      ## TODO: this should surely use a POST request?
      <once-button type="is-primary"
                   tag="a" href="${url('{}.refresh'.format(route_prefix), uuid=batch.uuid)}"
                   text="Refresh Data"
                   icon-left="redo">
      </once-button>
  % endif
</%def>

<%def name="trailing_buttons()">
  % if master.has_worksheet_file and master.allow_worksheet(batch) and master.has_perm('worksheet'):
      <b-button tag="a"
                href="${master.get_action_url('download_worksheet', batch)}"
                icon-pack="fas"
                icon-left="download">
        Download Worksheet
      </b-button>
      <b-button type="is-primary"
                icon-pack="fas"
                icon-left="upload"
                @click="$emit('show-upload')">
        Upload Worksheet
      </b-button>
  % endif
</%def>

<%def name="object_helpers()">
  ${self.render_status_breakdown()}
  ${self.render_execute_helper()}
</%def>

<%def name="render_status_breakdown()">
  <nav class="panel">
    <p class="panel-heading">Row Status</p>
    <div class="panel-block">
      <div style="width: 100%;">
        ${status_breakdown_grid}
      </div>
    </div>
  </nav>
</%def>

<%def name="render_execute_helper()">
  <nav class="panel">
    <p class="panel-heading">Execution</p>
    <div class="panel-block">
      <div style="display: flex; flex-direction: column; gap: 0.5rem;">
      % if batch.executed:
          <p>
            ${h.pretty_datetime(request.rattail_config, batch.executed)}
            by ${batch.executed_by}
          </p>
      % elif master.handler.executable(batch):
          % if master.has_perm('execute'):
              <b-button type="is-primary"
                        % if not execute_enabled:
                        disabled
                        % if why_not_execute:
                        title="${why_not_execute}"
                        % endif
                        % endif
                        @click="showExecutionDialog = true"
                        icon-pack="fas"
                        icon-left="arrow-circle-right">
                ${execute_title}
              </b-button>

              % if execute_enabled:
                  <b-modal has-modal-card
                           :active.sync="showExecutionDialog">
                    <div class="modal-card">

                      <header class="modal-card-head">
                        <p class="modal-card-title">Execute ${model_title}</p>
                      </header>

                      <section class="modal-card-body">
                        <p class="block has-text-weight-bold">
                          What will happen when this batch is executed?
                        </p>
                        <div class="markdown">
                          ${execution_described|n}
                        </div>
                        ${execute_form.render_vue_tag(ref='executeBatchForm')}
                      </section>

                      <footer class="modal-card-foot">
                        <b-button @click="showExecutionDialog = false">
                          Cancel
                        </b-button>
                        <once-button type="is-primary"
                                     @click="submitExecuteBatch()"
                                     icon-left="arrow-circle-right"
                                     text="Execute Batch">
                        </once-button>
                      </footer>

                    </div>
                  </b-modal>
              % endif

          % else:
              <p>TODO: batch *may* be executed, but not by *you*</p>
          % endif
      % else:
          <p>TODO: batch cannot be executed..?</p>
      % endif
      </div>
    </div>
  </nav>
</%def>

<%def name="render_this_page()">
  ${parent.render_this_page()}

  % if master.has_worksheet_file and master.allow_worksheet(batch) and master.has_perm('worksheet'):
      <b-modal has-modal-card
               :active.sync="showUploadDialog">
        <div class="modal-card">

          <header class="modal-card-head">
            <p class="modal-card-title">Upload Worksheet</p>
          </header>

          <section class="modal-card-body">
            <p>
              This will <span class="has-text-weight-bold">update</span>
              the batch data with the worksheet file you provide.&nbsp;
              Please be certain to use the right one!
            </p>
            <br />
            ${upload_worksheet_form.render_vue_tag(ref='uploadForm')}
          </section>

          <footer class="modal-card-foot">
            <b-button @click="showUploadDialog = false">
              Cancel
            </b-button>
            <b-button type="is-primary"
                      @click="submitUpload()"
                      icon-pack="fas"
                      icon-left="upload"
                      :disabled="uploadButtonDisabled">
              {{ uploadButtonText }}
            </b-button>
          </footer>

        </div>
      </b-modal>
  % endif

</%def>

<%def name="render_form()">
  <div class="form">
    <${form.component} @show-upload="showUploadDialog = true">
    </${form.component}>
  </div>
</%def>

<%def name="render_row_grid_tools()">
  ${parent.render_row_grid_tools()}
  % if master.rows_bulk_deletable and not batch.executed and master.has_perm('delete_rows'):
      <b-button type="is-danger"
                @click="deleteResultsInit()"
                :disabled="!total"
                icon-pack="fas"
                icon-left="trash">
        Delete Results
      </b-button>
      <b-modal has-modal-card
               :active.sync="deleteResultsShowDialog">
        <div class="modal-card">

          <header class="modal-card-head">
            <p class="modal-card-title">Delete Results</p>
          </header>

          <section class="modal-card-body">
            <p class="block">
              This batch has
              <span class="has-text-weight-bold">${batch.rowcount}</span>
              total rows.
            </p>
            <p class="block">
              Your current filters have returned
              <span class="has-text-weight-bold">{{ total }}</span>
              results.
            </p>
            <p class="block">
              Would you like to
              <span class="has-text-danger has-text-weight-bold">
                delete all {{ total }}
              </span>
              results?
            </p>
          </section>

          <footer class="modal-card-foot">
            <b-button @click="deleteResultsShowDialog = false">
              Cancel
            </b-button>
            <once-button type="is-danger"
                         tag="a" href="${url('{}.delete_rows'.format(route_prefix), uuid=batch.uuid)}"
                         icon-left="trash"
                         text="Delete Results">
            </once-button>
          </footer>
        </div>
      </b-modal>
  % endif
</%def>

<%def name="render_vue_templates()">
  ${parent.render_vue_templates()}
  % if master.has_worksheet_file and master.allow_worksheet(batch) and master.has_perm('worksheet'):
      ${upload_worksheet_form.render_vue_template(buttons=False, form_kwargs={'ref': 'actualUploadForm'})}
  % endif
  % if master.handler.executable(batch) and master.has_perm('execute'):
      ${execute_form.render_vue_template(form_kwargs={'ref': 'actualExecuteForm'}, buttons=False)}
  % endif
</%def>

## DEPRECATED; remains for back-compat
## nb. this is called by parent template, /form.mako
<%def name="render_form_template()">
  ## TODO: should use self.render_form_buttons()
  ## ${form.render_deform(form_id='batch-form', buttons=capture(self.render_form_buttons))|n}
  ${form.render_deform(form_id='batch-form', buttons=capture(buttons))|n}
</%def>

<%def name="modify_vue_vars()">
  ${parent.modify_vue_vars()}
  <script>

    ThisPageData.statusBreakdownData = ${json.dumps(status_breakdown_data)|n}

    ThisPage.methods.autoFilterStatus = function(row) {
        this.$refs.rowGrid.setFilters([
            {key: 'status_code',
             verb: 'equal',
             value: row.code},
        ])
        document.getElementById('rowGrid').scrollIntoView({
            behavior: 'smooth',
        })
    }

    % if not batch.executed and master.has_perm('edit'):
        ${form.vue_component}Data.togglingBatchComplete = false
    % endif

    % if master.has_worksheet_file and master.allow_worksheet(batch) and master.has_perm('worksheet'):

        ThisPageData.showUploadDialog = false
        ThisPageData.uploadButtonText = "Upload & Update Batch"
        ThisPageData.uploadButtonDisabled = false

        ThisPage.methods.submitUpload = function() {
            let form = this.$refs.uploadForm
            let value = form.field_model_worksheet_file
            if (!value) {
                alert("Please choose a file to upload.")
                return
            }
            this.uploadButtonDisabled = true
            this.uploadButtonText = "Working, please wait..."
            form.submit()
        }

        ${upload_worksheet_form.vue_component}.methods.submit = function() {
            this.$refs.actualUploadForm.submit()
        }

    ## end 'external_worksheet'
    % endif

    % if execute_enabled and master.has_perm('execute'):

        ThisPageData.showExecutionDialog = false

        ThisPage.methods.submitExecuteBatch = function() {
            this.$refs.executeBatchForm.submit()
        }

        ${execute_form.vue_component}.methods.submit = function() {
            this.$refs.actualExecuteForm.submit()
        }

    % endif

    % if master.rows_bulk_deletable and not batch.executed and master.has_perm('delete_rows'):

        ${rows_grid.vue_component}Data.deleteResultsShowDialog = false

        ${rows_grid.vue_component}.methods.deleteResultsInit = function() {
            this.deleteResultsShowDialog = true
        }

    % endif

  </script>
</%def>

<%def name="make_vue_components()">
  ${parent.make_vue_components()}
  % if master.has_worksheet_file and master.allow_worksheet(batch) and master.has_perm('worksheet'):
      ${upload_worksheet_form.render_vue_finalize()}
  % endif
  % if execute_enabled and master.has_perm('execute'):
      ${execute_form.render_vue_finalize()}
  % endif
</%def>
