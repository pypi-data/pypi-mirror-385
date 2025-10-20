## -*- coding: utf-8; -*-
<%inherit file="wuttaweb:templates/master/index.mako" />

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

<%def name="render_vue_template_grid()">
  ${grid.render_vue_template(tools=capture(self.grid_tools).strip(), context_menu=capture(self.context_menu_items).strip())}
</%def>

<%def name="modify_vue_vars()">
  ${parent.modify_vue_vars()}
  <script>

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

  </script>
</%def>
