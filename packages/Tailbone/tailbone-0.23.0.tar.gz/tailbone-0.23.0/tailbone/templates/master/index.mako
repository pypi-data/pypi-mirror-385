## -*- coding: utf-8; -*-
## ##############################################################################
## 
## Default master 'index' template.  Features a prominent data table and
## exposes a way to filter and sort the data, etc.  Some index pages also
## include a "tools" section, just above the grid on the right.
## 
## ##############################################################################
<%inherit file="/page.mako" />

<%def name="title()">${index_title}</%def>

<%def name="content_title()"></%def>

<%def name="grid_tools()">

  ## grid totals
  % if getattr(master, 'supports_grid_totals', False):
      <div style="display: flex; align-items: center;">
        <b-button v-if="gridTotalsDisplay == null"
                  :disabled="gridTotalsFetching"
                  @click="gridTotalsFetch()">
          {{ gridTotalsFetching ? "Working, please wait..." : "Show Totals" }}
        </b-button>
        <div v-if="gridTotalsDisplay != null"
             class="control">
          Totals: {{ gridTotalsDisplay }}
        </div>
      </div>
  % endif

  ## download search results
  % if getattr(master, 'results_downloadable', False) and master.has_perm('download_results'):
      <div>
        <b-button type="is-primary"
                  icon-pack="fas"
                  icon-left="download"
                  @click="showDownloadResultsDialog = true"
                  :disabled="!total">
          Download Results
        </b-button>

        ${h.form(url('{}.download_results'.format(route_prefix)), ref='download_results_form')}
        ${h.csrf_token(request)}
        <input type="hidden" name="fmt" :value="downloadResultsFormat" />
        <input type="hidden" name="fields" :value="downloadResultsFieldsIncluded" />
        ${h.end_form()}

        <b-modal :active.sync="showDownloadResultsDialog">
          <div class="card">

            <div class="card-content">
              <p>
                There are
                <span class="is-size-4 has-text-weight-bold">
                  {{ total.toLocaleString('en') }} ${model_title_plural}
                </span>
                matching your current filters.
              </p>
              <p>
                You may download this set as a single data file if you like.
              </p>
              <br />

              <b-notification type="is-warning" :closable="false"
                              v-if="downloadResultsFormat == 'xlsx' && total >= 1000">
                Excel downloads for large data sets can take a long time to
                generate, and bog down the server in the meantime.  You are
                encouraged to choose CSV for a large data set, even though
                the end result (file size) may be larger with CSV.
              </b-notification>

              <div style="display: flex; justify-content: space-between">

                <div>
                  <b-field label="Format">
                    <b-select v-model="downloadResultsFormat">
                      % for key, label in master.download_results_supported_formats().items():
                      <option value="${key}">${label}</option>
                      % endfor
                    </b-select>
                  </b-field>
                </div>

                <div>

                  <div v-show="downloadResultsFieldsMode != 'choose'"
                       class="has-text-right">
                    <p v-if="downloadResultsFieldsMode == 'default'">
                      Will use DEFAULT fields.
                    </p>
                    <p v-if="downloadResultsFieldsMode == 'all'">
                      Will use ALL fields.
                    </p>
                    <br />
                  </div>

                  <div class="buttons is-right">
                    <b-button type="is-primary"
                              v-show="downloadResultsFieldsMode != 'default'"
                              @click="downloadResultsUseDefaultFields()">
                      Use Default Fields
                    </b-button>
                    <b-button type="is-primary"
                              v-show="downloadResultsFieldsMode != 'all'"
                              @click="downloadResultsUseAllFields()">
                      Use All Fields
                    </b-button>
                    <b-button type="is-primary"
                              v-show="downloadResultsFieldsMode != 'choose'"
                              @click="downloadResultsFieldsMode = 'choose'">
                      Choose Fields
                    </b-button>
                  </div>

                  <div v-show="downloadResultsFieldsMode == 'choose'">
                    <div style="display: flex;">
                      <div>
                        <b-field label="Excluded Fields">
                          <b-select multiple native-size="8"
                                    expanded
                                    v-model="downloadResultsExcludedFieldsSelected"
                                    ref="downloadResultsExcludedFields">
                            <option v-for="field in downloadResultsFieldsExcluded"
                                    :key="field"
                                    :value="field">
                              {{ field }}
                            </option>
                          </b-select>
                        </b-field>
                      </div>
                      <div>
                        <br /><br />
                        <b-button style="margin: 0.5rem;"
                                  @click="downloadResultsExcludeFields()">
                          &lt;
                        </b-button>
                        <br />
                        <b-button style="margin: 0.5rem;"
                                  @click="downloadResultsIncludeFields()">
                          &gt;
                        </b-button>
                      </div>
                      <div>
                        <b-field label="Included Fields">
                          <b-select multiple native-size="8"
                                    expanded
                                    v-model="downloadResultsIncludedFieldsSelected"
                                    ref="downloadResultsIncludedFields">
                            <option v-for="field in downloadResultsFieldsIncluded"
                                    :key="field"
                                    :value="field">
                              {{ field }}
                            </option>
                          </b-select>
                        </b-field>
                      </div>
                    </div>
                  </div>

                </div>
              </div>
            </div> <!-- card-content -->

            <footer class="modal-card-foot">
              <b-button @click="showDownloadResultsDialog = false">
                Cancel
              </b-button>
              <once-button type="is-primary"
                           @click="downloadResultsSubmit()"
                           icon-pack="fas"
                           icon-left="download"
                           :disabled="!downloadResultsFieldsIncluded.length"
                           text="Download Results">
              </once-button>
            </footer>
          </div>
        </b-modal>
      </div>
  % endif

  ## download rows for search results
  % if getattr(master, 'has_rows', False) and master.results_rows_downloadable and master.has_perm('download_results_rows'):
      <b-button type="is-primary"
                icon-pack="fas"
                icon-left="download"
                @click="downloadResultsRows()"
                :disabled="downloadResultsRowsButtonDisabled">
        {{ downloadResultsRowsButtonText }}
      </b-button>
      ${h.form(url('{}.download_results_rows'.format(route_prefix)), ref='downloadResultsRowsForm')}
      ${h.csrf_token(request)}
      ${h.end_form()}
  % endif

  ## merge 2 objects
  % if getattr(master, 'mergeable', False) and request.has_perm('{}.merge'.format(permission_prefix)):

      ${h.form(url('{}.merge'.format(route_prefix)), class_='control', **{'@submit': 'submitMergeForm'})}
      ${h.csrf_token(request)}
      <input type="hidden"
             name="uuids"
             :value="checkedRowUUIDs()" />
      <b-button type="is-primary"
                native-type="submit"
                icon-pack="fas"
                icon-left="object-ungroup"
                :disabled="mergeFormSubmitting || checkedRows.length != 2">
        {{ mergeFormButtonText }}
      </b-button>
      ${h.end_form()}
  % endif

  ## enable / disable selected objects
  % if getattr(master, 'supports_set_enabled_toggle', False) and master.has_perm('enable_disable_set'):

      ${h.form(url('{}.enable_set'.format(route_prefix)), class_='control', ref='enable_selected_form')}
      ${h.csrf_token(request)}
      ${h.hidden('uuids', v_model='selected_uuids')}
      <b-button :disabled="enableSelectedDisabled"
                @click="enableSelectedSubmit()">
        {{ enableSelectedText }}
      </b-button>
      ${h.end_form()}

      ${h.form(url('{}.disable_set'.format(route_prefix)), ref='disable_selected_form', class_='control')}
      ${h.csrf_token(request)}
      ${h.hidden('uuids', v_model='selected_uuids')}
      <b-button :disabled="disableSelectedDisabled"
                @click="disableSelectedSubmit()">
        {{ disableSelectedText }}
      </b-button>
      ${h.end_form()}
  % endif

  ## delete selected objects
  % if getattr(master, 'set_deletable', False) and master.has_perm('delete_set'):
      ${h.form(url('{}.delete_set'.format(route_prefix)), ref='delete_selected_form', class_='control')}
      ${h.csrf_token(request)}
      ${h.hidden('uuids', v_model='selected_uuids')}
      <b-button type="is-danger"
                :disabled="deleteSelectedDisabled"
                @click="deleteSelectedSubmit()"
                icon-pack="fas"
                icon-left="trash">
        {{ deleteSelectedText }}
      </b-button>
      ${h.end_form()}
  % endif

  ## delete search results
  % if getattr(master, 'bulk_deletable', False) and request.has_perm('{}.bulk_delete'.format(permission_prefix)):
      ${h.form(url('{}.bulk_delete'.format(route_prefix)), ref='delete_results_form', class_='control')}
      ${h.csrf_token(request)}
      <b-button type="is-danger"
                :disabled="deleteResultsDisabled"
                :title="total ? null : 'There are no results to delete'"
                @click="deleteResultsSubmit()"
                icon-pack="fas"
                icon-left="trash">
        {{ deleteResultsText }}
      </b-button>
      ${h.end_form()}
  % endif

</%def>

## DEPRECATED; remains for back-compat
<%def name="render_this_page()">
  ${self.page_content()}
</%def>

<%def name="page_content()">

  % if download_results_path:
      <b-notification type="is-info">
        Your download should start automatically, or you can
        ${h.link_to("click here", '{}?filename={}'.format(url('{}.download_results'.format(route_prefix)), h.os.path.basename(download_results_path)))}
      </b-notification>
  % endif

  % if download_results_rows_path:
      <b-notification type="is-info">
        Your download should start automatically, or you can
        ${h.link_to("click here", '{}?filename={}'.format(url('{}.download_results_rows'.format(route_prefix)), h.os.path.basename(download_results_rows_path)))}
      </b-notification>
  % endif

  ${self.render_grid_component()}

  % if master.deletable and master.has_perm('delete') and getattr(master, 'delete_confirm', 'full') == 'simple':
      ${h.form('#', ref='deleteObjectForm')}
      ${h.csrf_token(request)}
      ${h.end_form()}
  % endif
</%def>

<%def name="render_grid_component()">
  ${grid.render_vue_tag()}
</%def>

##############################
## vue components
##############################

<%def name="render_vue_templates()">
  ${parent.render_vue_templates()}

  ## DEPRECATED; called for back-compat
  ${self.make_grid_component()}
</%def>

## DEPRECATED; remains for back-compat
<%def name="make_grid_component()">
  ${grid.render_vue_template(tools=capture(self.grid_tools).strip(), context_menu=capture(self.context_menu_items).strip())}
</%def>

<%def name="modify_vue_vars()">
  ${parent.modify_vue_vars()}
  <script type="text/javascript">

    % if getattr(master, 'supports_grid_totals', False):
        ${grid.vue_component}Data.gridTotalsDisplay = null
        ${grid.vue_component}Data.gridTotalsFetching = false

        ${grid.vue_component}.methods.gridTotalsFetch = function() {
            this.gridTotalsFetching = true

            let url = '${url(f'{route_prefix}.fetch_grid_totals')}'
            this.simpleGET(url, {}, response => {
                this.gridTotalsDisplay = response.data.totals_display
                this.gridTotalsFetching = false
            }, response => {
                this.gridTotalsFetching = false
            })
        }

        ${grid.vue_component}.methods.appliedFiltersHook = function() {
            this.gridTotalsDisplay = null
            this.gridTotalsFetching = false
        }
    % endif

    ## maybe auto-redirect to download latest results file
    % if download_results_path:
        ThisPage.methods.downloadResultsRedirect = function() {
            location.href = '${url('{}.download_results'.format(route_prefix))}?filename=${h.os.path.basename(download_results_path)}';
        }
        ThisPage.mounted = function() {
            // we give this 1 second before attempting the redirect; otherwise
            // the FontAwesome icons do not seem to load properly.  so this way
            // the page should fully render before redirecting
            window.setTimeout(this.downloadResultsRedirect, 1000)
        }
    % endif

    ## maybe auto-redirect to download latest "rows for results" file
    % if download_results_rows_path:
        ThisPage.methods.downloadResultsRowsRedirect = function() {
            location.href = '${url('{}.download_results_rows'.format(route_prefix))}?filename=${h.os.path.basename(download_results_rows_path)}';
        }
        ThisPage.mounted = function() {
            // we give this 1 second before attempting the redirect; otherwise
            // the FontAwesome icons do not seem to load properly.  so this way
            // the page should fully render before redirecting
            window.setTimeout(this.downloadResultsRowsRedirect, 1000)
        }
    % endif

    % if request.session.pop('{}.results_csv.generated'.format(route_prefix), False):
        ThisPage.mounted = function() {
            location.href = '${url('{}.results_csv_download'.format(route_prefix))}';
        }
    % endif
    % if request.session.pop('{}.results_xlsx.generated'.format(route_prefix), False):
        ThisPage.mounted = function() {
            location.href = '${url('{}.results_xlsx_download'.format(route_prefix))}';
        }
    % endif

    ## delete single object
    % if master.deletable and master.has_perm('delete') and getattr(master, 'delete_confirm', 'full') == 'simple':
        ThisPage.methods.deleteObject = function(url) {
            if (confirm("Are you sure you wish to delete this ${model_title}?")) {
                let form = this.$refs.deleteObjectForm
                form.action = url
                form.submit()
            }
        }
    % endif

    ## download results
    % if getattr(master, 'results_downloadable', False) and master.has_perm('download_results'):

        ${grid.vue_component}Data.downloadResultsFormat = '${master.download_results_default_format()}'
        ${grid.vue_component}Data.showDownloadResultsDialog = false
        ${grid.vue_component}Data.downloadResultsFieldsMode = 'default'
        ${grid.vue_component}Data.downloadResultsFieldsAvailable = ${json.dumps(download_results_fields_available)|n}
        ${grid.vue_component}Data.downloadResultsFieldsDefault = ${json.dumps(download_results_fields_default)|n}
        ${grid.vue_component}Data.downloadResultsFieldsIncluded = ${json.dumps(download_results_fields_default)|n}

        ${grid.vue_component}Data.downloadResultsExcludedFieldsSelected = []
        ${grid.vue_component}Data.downloadResultsIncludedFieldsSelected = []

        ${grid.vue_component}.computed.downloadResultsFieldsExcluded = function() {
            let excluded = []
            this.downloadResultsFieldsAvailable.forEach(field => {
                if (!this.downloadResultsFieldsIncluded.includes(field)) {
                    excluded.push(field)
                }
            }, this)
            return excluded
        }

        ${grid.vue_component}.methods.downloadResultsExcludeFields = function() {
            const selected = Array.from(this.downloadResultsIncludedFieldsSelected)
            if (!selected) {
                return
            }

            selected.forEach(field => {
                let index

                // remove field from selected
                index = this.downloadResultsIncludedFieldsSelected.indexOf(field)
                if (index >= 0) {
                    this.downloadResultsIncludedFieldsSelected.splice(index, 1)
                }

                // remove field from included
                // nb. excluded list will reflect this change too
                index = this.downloadResultsFieldsIncluded.indexOf(field)
                if (index >= 0) {
                    this.downloadResultsFieldsIncluded.splice(index, 1)
                }
            })
        }

        ${grid.vue_component}.methods.downloadResultsIncludeFields = function() {
            const selected = Array.from(this.downloadResultsExcludedFieldsSelected)
            if (!selected) {
                return
            }

            selected.forEach(field => {
                let index

                // remove field from selected
                index = this.downloadResultsExcludedFieldsSelected.indexOf(field)
                if (index >= 0) {
                    this.downloadResultsExcludedFieldsSelected.splice(index, 1)
                }

                // add field to included
                // nb. excluded list will reflect this change too
                this.downloadResultsFieldsIncluded.push(field)
            })
        }

        ${grid.vue_component}.methods.downloadResultsUseDefaultFields = function() {
            this.downloadResultsFieldsIncluded = Array.from(this.downloadResultsFieldsDefault)
            this.downloadResultsFieldsMode = 'default'
        }

        ${grid.vue_component}.methods.downloadResultsUseAllFields = function() {
            this.downloadResultsFieldsIncluded = Array.from(this.downloadResultsFieldsAvailable)
            this.downloadResultsFieldsMode = 'all'
        }

        ${grid.vue_component}.methods.downloadResultsSubmit = function() {
            this.$refs.download_results_form.submit()
        }
    % endif

    ## download rows for results
    % if getattr(master, 'has_rows', False) and master.results_rows_downloadable and master.has_perm('download_results_rows'):

        ${grid.vue_component}Data.downloadResultsRowsButtonDisabled = false
        ${grid.vue_component}Data.downloadResultsRowsButtonText = "Download Rows for Results"

        ${grid.vue_component}.methods.downloadResultsRows = function() {
            if (confirm("This will generate an Excel file which contains "
                        + "not the results themselves, but the *rows* for "
                        + "each.\n\nAre you sure you want this?")) {
                this.downloadResultsRowsButtonDisabled = true
                this.downloadResultsRowsButtonText = "Working, please wait..."
                this.$refs.downloadResultsRowsForm.submit()
            }
        }
    % endif

    ## enable / disable selected objects
    % if getattr(master, 'supports_set_enabled_toggle', False) and master.has_perm('enable_disable_set'):

        ${grid.vue_component}Data.enableSelectedSubmitting = false
        ${grid.vue_component}Data.enableSelectedText = "Enable Selected"

        ${grid.vue_component}.computed.enableSelectedDisabled = function() {
            if (this.enableSelectedSubmitting) {
                return true
            }
            if (!this.checkedRowUUIDs().length) {
                return true
            }
            return false
        }

        ${grid.vue_component}.methods.enableSelectedSubmit = function() {
            let uuids = this.checkedRowUUIDs()
            if (!uuids.length) {
                alert("You must first select one or more objects to disable.")
                return
            }
            if (! confirm("Are you sure you wish to ENABLE the " + uuids.length + " selected objects?")) {
                return
            }

            this.enableSelectedSubmitting = true
            this.enableSelectedText = "Working, please wait..."
            this.$refs.enable_selected_form.submit()
        }

        ${grid.vue_component}Data.disableSelectedSubmitting = false
        ${grid.vue_component}Data.disableSelectedText = "Disable Selected"

        ${grid.vue_component}.computed.disableSelectedDisabled = function() {
            if (this.disableSelectedSubmitting) {
                return true
            }
            if (!this.checkedRowUUIDs().length) {
                return true
            }
            return false
        }

        ${grid.vue_component}.methods.disableSelectedSubmit = function() {
            let uuids = this.checkedRowUUIDs()
            if (!uuids.length) {
                alert("You must first select one or more objects to disable.")
                return
            }
            if (! confirm("Are you sure you wish to DISABLE the " + uuids.length + " selected objects?")) {
                return
            }

            this.disableSelectedSubmitting = true
            this.disableSelectedText = "Working, please wait..."
            this.$refs.disable_selected_form.submit()
        }

    % endif

    ## delete selected objects
    % if getattr(master, 'set_deletable', False) and master.has_perm('delete_set'):

        ${grid.vue_component}Data.deleteSelectedSubmitting = false
        ${grid.vue_component}Data.deleteSelectedText = "Delete Selected"

        ${grid.vue_component}.computed.deleteSelectedDisabled = function() {
            if (this.deleteSelectedSubmitting) {
                return true
            }
            if (!this.checkedRowUUIDs().length) {
                return true
            }
            return false
        }

        ${grid.vue_component}.methods.deleteSelectedSubmit = function() {
            let uuids = this.checkedRowUUIDs()
            if (!uuids.length) {
                alert("You must first select one or more objects to disable.")
                return
            }
            if (! confirm("Are you sure you wish to DELETE the " + uuids.length + " selected objects?")) {
                return
            }

            this.deleteSelectedSubmitting = true
            this.deleteSelectedText = "Working, please wait..."
            this.$refs.delete_selected_form.submit()
        }
    % endif

    % if getattr(master, 'bulk_deletable', False) and master.has_perm('bulk_delete'):

        ${grid.vue_component}Data.deleteResultsSubmitting = false
        ${grid.vue_component}Data.deleteResultsText = "Delete Results"

        ${grid.vue_component}.computed.deleteResultsDisabled = function() {
            if (this.deleteResultsSubmitting) {
                return true
            }
            if (!this.total) {
                return true
            }
            return false
        }

        ${grid.vue_component}.methods.deleteResultsSubmit = function() {
            // TODO: show "plural model title" here?
            if (!confirm("You are about to delete " + this.total.toLocaleString('en') + " objects.\n\nAre you sure?")) {
                return
            }

            this.deleteResultsSubmitting = true
            this.deleteResultsText = "Working, please wait..."
            this.$refs.delete_results_form.submit()
        }

    % endif

    % if getattr(master, 'mergeable', False) and master.has_perm('merge'):

        ${grid.vue_component}Data.mergeFormButtonText = "Merge 2 ${model_title_plural}"
        ${grid.vue_component}Data.mergeFormSubmitting = false

        ${grid.vue_component}.methods.submitMergeForm = function() {
            this.mergeFormSubmitting = true
            this.mergeFormButtonText = "Working, please wait..."
        }
    % endif
  </script>
</%def>

<%def name="make_vue_components()">
  ${parent.make_vue_components()}
  <script>
    ${grid.vue_component}.data = function() { return ${grid.vue_component}Data }
    Vue.component('${grid.vue_tagname}', ${grid.vue_component})
  </script>
</%def>
