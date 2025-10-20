## -*- coding: utf-8; -*-
<%inherit file="/master/form.mako" />

<%def name="title()">${index_title} &raquo; ${instance_title}</%def>

<%def name="content_title()">
  ${instance_title}
</%def>

<%def name="render_instance_header_title_extras()">
  % if getattr(master, 'touchable', False) and master.has_perm('touch'):
      <b-button title="&quot;Touch&quot; this record to trigger sync"
                @click="touchRecord()"
                :disabled="touchSubmitting">
        % if request.use_oruga:
            <o-icon icon="hand-pointer" />
        % else:
            <span><i class="fa fa-hand-pointer"></i></span>
        % endif
      </b-button>
  % endif
  % if expose_versions:
      <b-button icon-pack="fas"
                icon-left="history"
                @click="viewingHistory = !viewingHistory">
        {{ viewingHistory ? "View Current" : "View History" }}
      </b-button>
  % endif
</%def>

<%def name="object_helpers()">
  ${parent.object_helpers()}
  ${self.render_xref_helper()}
</%def>

<%def name="render_xref_helper()">
  % if xref_buttons or xref_links:
      <nav class="panel">
        <p class="panel-heading">Cross-Reference</p>
        <div class="panel-block">
          <div style="display: flex; flex-direction: column; gap: 0.5rem;">
            % for button in xref_buttons:
                ${button}
            % endfor
            % for link in xref_links:
                ${link}
            % endfor
          </div>
        </div>
      </nav>
  % endif
</%def>

<%def name="render_row_grid_tools()">
  ${rows_grid_tools}
  % if master.rows_downloadable_xlsx and master.has_perm('row_results_xlsx'):
      <b-button tag="a" href="${master.get_action_url('row_results_xlsx', instance)}"
                icon-pack="fas"
                icon-left="download">
        Download Results XLSX
      </b-button>
  % endif
  % if master.rows_downloadable_csv and master.has_perm('row_results_csv'):
      <b-button tag="a" href="${master.get_action_url('row_results_csv', instance)}"
                icon-pack="fas"
                icon-left="download">
        Download Results CSV
      </b-button>
  % endif
</%def>

<%def name="render_this_page_component()">
  ## TODO: should override this in a cleaner way!  too much duplicate code w/ parent template
  <this-page @change-content-title="changeContentTitle"
             % if can_edit_help:
             :configure-fields-help="configureFieldsHelp"
             % endif
             % if expose_versions:
             :viewing-history="viewingHistory"
             % endif
             >
  </this-page>
</%def>

<%def name="render_this_page()">
  <div
    % if expose_versions:
    v-show="!viewingHistory"
    % endif
    >

    ## render main form
    ${parent.render_this_page()}

    ## render row grid
    % if getattr(master, 'has_rows', False):
        <br />
        % if rows_title:
            <h4 class="block is-size-4">${rows_title}</h4>
        % endif
        ${self.render_row_grid_component()}
    % endif
  </div>

  % if expose_versions:
      <div v-show="viewingHistory">

        <div style="display: flex; align-items: center; gap: 2rem;">
          <h3 class="is-size-3">Version History</h3>
          <p class="block">
            <a href="${master.get_action_url('versions', instance)}"
               target="_blank">
              % if request.use_oruga:
                  <o-icon icon="external-link-alt" />
              % else:
                  <i class="fas fa-external-link-alt"></i>
              % endif
              View as separate page
            </a>
          </p>
        </div>

        ${versions_grid.render_vue_tag(ref='versionsGrid', **{'@view-revision': 'viewRevision'})}

        <${b}-modal :width="1200"
                    % if request.use_oruga:
                    v-model:active="viewVersionShowDialog"
                    % else:
                    :active.sync="viewVersionShowDialog"
                    % endif
                    >
          <div class="card">
            <div class="card-content">
              <div style="display: flex; flex-direction: column; gap: 1.5rem;">

                <div style="display: flex; gap: 1rem;">

                  <div style="flex-grow: 1;">
                    <b-field horizontal label="Changed">
                      <div v-html="viewVersionData.changed"></div>
                    </b-field>
                    <b-field horizontal label="Changed by">
                      <div v-html="viewVersionData.changed_by"></div>
                    </b-field>
                    <b-field horizontal label="IP Address">
                      <div v-html="viewVersionData.remote_addr"></div>
                    </b-field>
                    <b-field horizontal label="Comment">
                      <div v-html="viewVersionData.comment"></div>
                    </b-field>
                    <b-field horizontal label="TXN ID">
                      <div v-html="viewVersionData.txnid"></div>
                    </b-field>
                  </div>

                  <div style="display: flex; flex-direction: column; justify-content: space-between;">

                    <div class="buttons">
                      <b-button @click="viewPrevRevision()"
                                type="is-primary"
                                icon-pack="fas"
                                icon-left="arrow-left"
                                :disabled="!viewVersionData.prev_txnid">
                        Older
                      </b-button>
                      <b-button @click="viewNextRevision()"
                                type="is-primary"
                                icon-pack="fas"
                                icon-right="arrow-right"
                                :disabled="!viewVersionData.next_txnid">
                        Newer
                      </b-button>
                    </div>

                    <div>
                      <a :href="viewVersionData.url"
                         target="_blank">
                        % if request.use_oruga:
                            <o-icon icon="external-link-alt" />
                        % else:
                            <i class="fas fa-external-link-alt"></i>
                        % endif
                        View as separate page
                      </a>
                    </div>

                    <b-button @click="toggleVersionFields()">
                      {{ viewVersionShowAllFields ? "Show Diffs Only" : "Show All Fields" }}
                    </b-button>
                  </div>

                </div>

                <div v-for="version in viewVersionData.versions"
                     :key="version.key">

                  <p class="block has-text-weight-bold">
                    {{ version.model_title }}
                    ({{ version.operation }})
                  </p>

                  <table class="diff monospace is-size-7"
                         :class="version.diff_class">
                    <thead>
                      <tr>
                        <th>field name</th>
                        <th>old value</th>
                        <th>new value</th>
                      </tr>
                    </thead>
                    <tbody>
                      <tr v-for="field in version.fields"
                          :key="field"
                          :class="{diff: version.values[field].after != version.values[field].before}"
                          v-show="viewVersionShowAllFields || version.values[field].after != version.values[field].before">
                        <td class="field has-text-weight-bold">{{ field }}</td>
                        <td class="old-value" v-html="version.values[field].before"></td>
                        <td class="new-value" v-html="version.values[field].after"></td>
                      </tr>
                    </tbody>
                  </table>

                </div>

              </div>
              % if request.use_oruga:
                  <o-loading v-model:active="viewVersionLoading" :is-full-page="false" />
              % else:
                  <b-loading :active.sync="viewVersionLoading" :is-full-page="false"></b-loading>
              % endif
            </div>
          </div>
        </${b}-modal>
      </div>
  % endif
</%def>

<%def name="render_row_grid_component()">
  ${rows_grid.render_vue_tag(id='rowGrid', ref='rowGrid')}
</%def>

<%def name="render_vue_templates()">
  ${parent.render_vue_templates()}
  % if getattr(master, 'has_rows', False):
      ${rows_grid.render_vue_template(allow_save_defaults=False, tools=capture(self.render_row_grid_tools))}
  % endif
  % if expose_versions:
      ${versions_grid.render_vue_template()}
  % endif
</%def>

<%def name="modify_vue_vars()">
  ${parent.modify_vue_vars()}
  <script>

    % if getattr(master, 'touchable', False) and master.has_perm('touch'):

        WholePageData.touchSubmitting = false

        WholePage.methods.touchRecord = function() {
            this.touchSubmitting = true
            location.href = '${master.get_action_url('touch', instance)}'
        }

    % endif

    % if expose_versions:

        WholePageData.viewingHistory = false
        ThisPage.props.viewingHistory = Boolean

        ThisPageData.gettingRevisions = false
        ThisPageData.gotRevisions = false

        ThisPageData.viewVersionShowDialog = false
        ThisPageData.viewVersionData = {}
        ThisPageData.viewVersionShowAllFields = false
        ThisPageData.viewVersionLoading = false

        // auto-fetch grid results when first viewing history
        ThisPage.watch.viewingHistory = function(newval, oldval) {
            if (!this.gotRevisions && !this.gettingRevisions) {
                this.gettingRevisions = true
                this.$refs.versionsGrid.loadAsyncData(null, () => {
                    this.gettingRevisions = false
                    this.gotRevisions = true
                }, () => {
                    this.gettingRevisions = false
                })
            }
        }

        VersionsGrid.methods.viewRevision = function(row) {
            this.$emit('view-revision', row)
        }

        ThisPage.methods.viewRevision = function(row) {
            this.viewVersionLoading = true

            let url = '${master.get_action_url('revisions_data', instance)}'
            let params = {txnid: row.id}
            this.simpleGET(url, params, response => {
                this.viewVersionData = response.data
                this.viewVersionLoading = false
            }, response => {
                this.viewVersionLoading = false
            })

            this.viewVersionShowDialog = true
        }

        ThisPage.methods.viewPrevRevision = function() {
            this.viewRevision({id: this.viewVersionData.prev_txnid})
        }

        ThisPage.methods.viewNextRevision = function() {
            this.viewRevision({id: this.viewVersionData.next_txnid})
        }

        ThisPage.methods.toggleVersionFields = function() {
            this.viewVersionShowAllFields = !this.viewVersionShowAllFields
        }

    % endif
  </script>
</%def>

<%def name="make_vue_components()">
  ${parent.make_vue_components()}
  % if getattr(master, 'has_rows', False):
      ${rows_grid.render_vue_finalize()}
  % endif
  % if expose_versions:
      ${versions_grid.render_vue_finalize()}
  % endif
</%def>
