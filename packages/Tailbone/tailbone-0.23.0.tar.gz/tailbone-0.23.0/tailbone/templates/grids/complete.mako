## -*- coding: utf-8; -*-

<% request.register_component(grid.vue_tagname, grid.vue_component) %>

<script type="text/x-template" id="${grid.vue_tagname}-template">
  <div>

    <div style="display: flex; justify-content: space-between; margin-bottom: 0.5em;">

      <div style="display: flex; flex-direction: column; justify-content: end;">
        <div class="filters">
          % if getattr(grid, 'filterable', False):
              <form method="GET" @submit.prevent="applyFilters()">

                <div style="display: flex; flex-direction: column; gap: 0.5rem;">
                  <grid-filter v-for="key in filtersSequence"
                               :key="key"
                               :filter="filters[key]"
                               ref="gridFilters">
                  </grid-filter>
                </div>

                <div style="display: flex; gap: 0.5rem; margin-top: 0.5rem;">

                  <b-button type="is-primary"
                            native-type="submit"
                            icon-pack="fas"
                            icon-left="check">
                    Apply Filters
                  </b-button>

                  <b-button v-if="!addFilterShow"
                            icon-pack="fas"
                            icon-left="plus"
                            @click="addFilterInit()">
                    Add Filter
                  </b-button>

                  <b-autocomplete v-if="addFilterShow"
                                  ref="addFilterAutocomplete"
                                  :data="addFilterChoices"
                                  v-model="addFilterTerm"
                                  placeholder="Add Filter"
                                  field="key"
                                  :custom-formatter="formatAddFilterItem"
                                  open-on-focus
                                  keep-first
                                  icon-pack="fas"
                                  clearable
                                  clear-on-select
                                  @select="addFilterSelect">
                  </b-autocomplete>

                  <b-button @click="resetView()"
                            icon-pack="fas"
                            icon-left="home">
                    Default View
                  </b-button>

                  <b-button @click="clearFilters()"
                            icon-pack="fas"
                            icon-left="trash">
                    No Filters
                  </b-button>

                  % if allow_save_defaults and request.user:
                      <b-button @click="saveDefaults()"
                                icon-pack="fas"
                                icon-left="save"
                                :disabled="savingDefaults">
                        {{ savingDefaults ? "Working, please wait..." : "Save Defaults" }}
                      </b-button>
                  % endif

                </div>
              </form>
          % endif
        </div>
      </div>

      <div style="display: flex; flex-direction: column; justify-content: space-between;">

        <div class="context-menu">
          % if context_menu:
              <ul id="context-menu">
                ## TODO: stop using |n filter
                ${context_menu|n}
              </ul>
          % endif
        </div>

        <div class="grid-tools-wrapper">
          % if tools:
              <div class="grid-tools">
                ## TODO: stop using |n filter
                ${tools|n}
              </div>
          % endif
        </div>

      </div>

    </div>

    <${b}-table
       :data="visibleData"
       :loading="loading"
       :row-class="getRowClass"
       % if request.use_oruga:
           tr-checked-class="is-checked"
       % endif

       % if request.rattail_config.getbool('tailbone', 'sticky_headers'):
       sticky-header
       height="600px"
       % endif

       :checkable="checkable"

       % if getattr(grid, 'checkboxes', False):
           % if request.use_oruga:
               v-model:checked-rows="checkedRows"
           % else:
               :checked-rows.sync="checkedRows"
           % endif
           % if grid.clicking_row_checks_box:
               @click="rowClick"
           % endif
       % endif

       % if getattr(grid, 'check_handler', None):
       @check="${grid.check_handler}"
       % endif
       % if getattr(grid, 'check_all_handler', None):
       @check-all="${grid.check_all_handler}"
       % endif

       % if hasattr(grid, 'checkable'):
       % if isinstance(grid.checkable, str):
       :is-row-checkable="${grid.row_checkable}"
       % elif grid.checkable:
       :is-row-checkable="row => row._checkable"
       % endif
       % endif

       ## sorting
       % if grid.sortable:
           ## nb. buefy/oruga only support *one* default sorter
           :default-sort="sorters.length ? [sorters[0].field, sorters[0].order] : null"
           % if grid.sort_on_backend:
               backend-sorting
               @sort="onSort"
           % endif
           % if grid.sort_multiple:
               % if grid.sort_on_backend:
                   ## TODO: there is a bug (?) which prevents the arrow
                   ## from displaying for simple default single-column sort,
                   ## when multi-column sort is allowed for the table.  for
                   ## now we work around that by waiting until mount to
                   ## enable the multi-column support.  see also
                   ## https://github.com/buefy/buefy/issues/2584
                   :sort-multiple="allowMultiSort"
                   :sort-multiple-data="sortingPriority"
                   @sorting-priority-removed="sortingPriorityRemoved"
               % else:
                   sort-multiple
               % endif
               ## nb. user must ctrl-click column header for multi-sort
               sort-multiple-key="ctrlKey"
           % endif
       % endif

       % if getattr(grid, 'click_handlers', None):
       @cellclick="cellClick"
       % endif

       ## paging
       % if grid.paginated:
           paginated
           pagination-size="${'small' if request.use_oruga else 'is-small'}"
           :per-page="perPage"
           :current-page="currentPage"
           @page-change="onPageChange"
           % if grid.paginate_on_backend:
               backend-pagination
               :total="pagerStats.item_count"
           % endif
       % endif

       ## TODO: should let grid (or master view) decide how to set these?
       icon-pack="fas"
       ## note that :striped="true" was interfering with row status (e.g. warning) styles
       :striped="false"
       :hoverable="true"
       :narrowed="true">

      % for column in grid.get_vue_columns():
          <${b}-table-column field="${column['field']}"
                          label="${column['label']}"
                          v-slot="props"
                          :sortable="${json.dumps(column.get('sortable', False))|n}"
                          :searchable="${json.dumps(column.get('searchable', False))|n}"
                          cell-class="c_${column['field']}"
                          :visible="${json.dumps(column.get('visible', True))}">
            % if hasattr(grid, 'raw_renderers') and column['field'] in grid.raw_renderers:
                ${grid.raw_renderers[column['field']]()}
            % elif grid.is_linked(column['field']):
                <a :href="props.row._action_url_view"
                   % if view_click_handler:
                   @click.prevent="${view_click_handler}"
                   % endif
                   v-html="props.row.${column['field']}">
                </a>
            % else:
                <span v-html="props.row.${column['field']}"></span>
            % endif
          </${b}-table-column>
      % endfor

      % if grid.actions:
          <${b}-table-column field="actions"
                          label="Actions"
                          v-slot="props">
            ## TODO: we do not currently differentiate for "main vs. more"
            ## here, but ideally we would tuck "more" away in a drawer etc.
            % for action in grid.actions:
                <a v-if="props.row._action_url_${action.key}"
                   :href="props.row._action_url_${action.key}"
                   class="grid-action${' has-text-danger' if action.key == 'delete' else ''} ${action.link_class or ''}"
                   % if getattr(action, 'click_handler', None):
                   @click.prevent="${action.click_handler}"
                   % endif
                   % if getattr(action, 'target', None):
                   target="${action.target}"
                   % endif
                   >
                  ${action.render_icon_and_label()}
                </a>
                &nbsp;
            % endfor
          </${b}-table-column>
      % endif

      <template #empty>
        <section class="section">
          <div class="content has-text-grey has-text-centered">
            <p>
              <b-icon
                 pack="fas"
                 icon="sad-tear"
                 size="is-large">
              </b-icon>
            </p>
            <p>Nothing here.</p>
          </div>
        </section>
      </template>

      <template #footer>
        <div style="display: flex; justify-content: space-between;">

          % if getattr(grid, 'expose_direct_link', False):
              <b-button type="is-primary"
                        size="is-small"
                        @click="copyDirectLink()"
                        title="Copy link to clipboard">
                % if request.use_oruga:
                    <o-icon icon="share-alt" />
                % else:
                    <span><i class="fa fa-share-alt"></i></span>
                % endif
              </b-button>
          % else:
              <div></div>
          % endif

          % if grid.paginated:
              <div v-if="pagerStats.first_item"
                   style="display: flex; gap: 0.5rem; align-items: center;">
                <span>
                  showing
                  {{ renderNumber(pagerStats.first_item) }}
                  - {{ renderNumber(pagerStats.last_item) }}
                  of {{ renderNumber(pagerStats.item_count) }} results;
                </span>
                <b-select v-model="perPage"
                          size="is-small"
                          @input="perPageUpdated">
                  % for value in grid.get_pagesize_options():
                      <option value="${value}">${value}</option>
                  % endfor
                </b-select>
                <span>
                  per page
                </span>
              </div>
          % endif

        </div>
      </template>

    </${b}-table>

    ## dummy input field needed for sharing links on *insecure* sites
    % if getattr(request, 'scheme', None) == 'http':
        <b-input v-model="shareLink" ref="shareLink" v-show="shareLink"></b-input>
    % endif

  </div>
</script>

<script type="text/javascript">

  const ${grid.vue_component}Context = ${json.dumps(grid.get_vue_context())|n}
  let ${grid.vue_component}CurrentData = ${grid.vue_component}Context.data

  let ${grid.vue_component}Data = {
      loading: false,
      ajaxDataUrl: ${json.dumps(getattr(grid, 'ajax_data_url', request.path_url))|n},

      ## nb. this tracks whether grid.fetchFirstData() happened
      fetchedFirstData: false,

      savingDefaults: false,

      data: ${grid.vue_component}CurrentData,
      rowStatusMap: ${json.dumps(grid_data['row_status_map'] if grid_data is not Undefined else {})|n},

      checkable: ${json.dumps(getattr(grid, 'checkboxes', False))|n},
      % if getattr(grid, 'checkboxes', False):
      checkedRows: ${grid_data['checked_rows_code']|n},
      % endif

      ## paging
      % if grid.paginated:
          pageSizeOptions: ${json.dumps(grid.pagesize_options)|n},
          perPage: ${json.dumps(grid.pagesize)|n},
          currentPage: ${json.dumps(grid.page)|n},
          % if grid.paginate_on_backend:
              pagerStats: ${json.dumps(grid.get_vue_pager_stats())|n},
          % endif
      % endif

      ## sorting
      % if grid.sortable:
          sorters: ${json.dumps(grid.get_vue_active_sorters())|n},
          % if grid.sort_multiple:
              % if grid.sort_on_backend:
                  ## TODO: there is a bug (?) which prevents the arrow
                  ## from displaying for simple default single-column sort,
                  ## when multi-column sort is allowed for the table.  for
                  ## now we work around that by waiting until mount to
                  ## enable the multi-column support.  see also
                  ## https://github.com/buefy/buefy/issues/2584
                  allowMultiSort: false,
                  ## nb. this should be empty when current sort is single-column
                  % if len(grid.active_sorters) > 1:
                      sortingPriority: ${json.dumps(grid.get_vue_active_sorters())|n},
                  % else:
                      sortingPriority: [],
                  % endif
              % endif
          % endif
      % endif

      ## filterable: ${json.dumps(grid.filterable)|n},
      filters: ${json.dumps(filters_data if getattr(grid, 'filterable', False) else None)|n},
      filtersSequence: ${json.dumps(filters_sequence if getattr(grid, 'filterable', False) else None)|n},
      addFilterTerm: '',
      addFilterShow: false,

      ## dummy input value needed for sharing links on *insecure* sites
      % if getattr(request, 'scheme', None) == 'http':
      shareLink: null,
      % endif
  }

  let ${grid.vue_component} = {
      template: '#${grid.vue_tagname}-template',

      mixins: [FormPosterMixin],

      props: {
          csrftoken: String,
      },

      computed: {

          ## TODO: this should be temporary? but anyway 'total' is
          ## still referenced in other places, e.g. "delete results"
          % if grid.paginated:
              total() { return this.pagerStats.item_count },
          % endif

          % if not grid.paginate_on_backend:

              pagerStats() {
                  const data = this.visibleData
                  let last = this.currentPage * this.perPage
                  let first = last - this.perPage + 1
                  if (last > data.length) {
                      last = data.length
                  }
                  return {
                      'item_count': data.length,
                      'items_per_page': this.perPage,
                      'page': this.currentPage,
                      'first_item': first,
                      'last_item': last,
                  }
              },

          % endif

          addFilterChoices() {
              // nb. this returns all choices available for "Add Filter" operation

              // collect all filters, which are *not* already shown
              let choices = []
              for (let field of this.filtersSequence) {
                  let filtr = this.filters[field]
                  if (!filtr.visible) {
                      choices.push(filtr)
                  }
              }

              // parse list of search terms
              let terms = []
              for (let term of this.addFilterTerm.toLowerCase().split(' ')) {
                  term = term.trim()
                  if (term) {
                      terms.push(term)
                  }
              }

              // only filters matching all search terms are presented
              // as choices to the user
              return choices.filter(option => {
                  let label = option.label.toLowerCase()
                  for (let term of terms) {
                      if (label.indexOf(term) < 0) {
                          return false
                      }
                  }
                  return true
              })
          },

          // note, can use this with v-model for hidden 'uuids' fields
          selected_uuids: function() {
              return this.checkedRowUUIDs().join(',')
          },

          // nb. this can be overridden if needed, e.g. to dynamically
          // show/hide certain records in a static data set
          visibleData() {
              return this.data
          },

          directLink() {
              let params = new URLSearchParams(this.getAllParams())
              return `${request.path_url}?${'$'}{params}`
          },
      },

      % if grid.sortable and grid.sort_multiple and grid.sort_on_backend:

            ## TODO: there is a bug (?) which prevents the arrow
            ## from displaying for simple default single-column sort,
            ## when multi-column sort is allowed for the table.  for
            ## now we work around that by waiting until mount to
            ## enable the multi-column support.  see also
            ## https://github.com/buefy/buefy/issues/2584
            mounted() {
                this.allowMultiSort = true
            },

      % endif

      methods: {

          renderNumber(value) {
              if (value != undefined) {
                  return value.toLocaleString('en')
              }
          },

          formatAddFilterItem(filtr) {
              if (!filtr.key) {
                  filtr = this.filters[filtr]
              }
              return filtr.label || filtr.key
          },

          % if getattr(grid, 'click_handlers', None):
              cellClick(row, column, rowIndex, columnIndex) {
                  % for key in grid.click_handlers:
                      if (column._props.field == '${key}') {
                          ${grid.click_handlers[key]}(row)
                      }
                  % endfor
              },
          % endif

          copyDirectLink() {

              if (navigator.clipboard) {
                  // this is the way forward, but requires HTTPS
                  navigator.clipboard.writeText(this.directLink)

              } else {
                  // use deprecated 'copy' command, but this just
                  // tells the browser to copy currently-selected
                  // text..which means we first must "add" some text
                  // to screen, and auto-select that, before copying
                  // to clipboard
                  this.shareLink = this.directLink
                  this.$nextTick(() => {
                      let input = this.$refs.shareLink.$el.firstChild
                      input.select()
                      document.execCommand('copy')
                      // re-hide the dummy input
                      this.shareLink = null
                  })
              }

              this.$buefy.toast.open({
                  message: "Link was copied to clipboard",
                  type: 'is-info',
                  duration: 2000, // 2 seconds
              })
          },

          addRowClass(index, className) {

              // TODO: this may add duplicated name to class string
              // (not a serious problem i think, but could be improved)
              this.rowStatusMap[index] = (this.rowStatusMap[index] || '')
                  + ' ' + className

              // nb. for some reason b-table does not always "notice"
              // when we update status; so we force it to refresh
              this.$forceUpdate()
          },

          getRowClass(row, index) {
              return this.rowStatusMap[index]
          },

          getBasicParams() {
              const params = {
                  % if grid.paginated and grid.paginate_on_backend:
                      pagesize: this.perPage,
                      page: this.currentPage,
                  % endif
              }
              % if grid.sortable and grid.sort_on_backend:
                  for (let i = 1; i <= this.sorters.length; i++) {
                      params['sort'+i+'key'] = this.sorters[i-1].field
                      params['sort'+i+'dir'] = this.sorters[i-1].order
                  }
              % endif
              return params
          },

          getFilterParams() {
              let params = {}
              for (var key in this.filters) {
                  var filter = this.filters[key]
                  if (filter.active) {
                      params[key] = filter.value
                      params[key+'.verb'] = filter.verb
                  }
              }
              if (Object.keys(params).length) {
                  params.filter = true
              }
              return params
          },

          getAllParams() {
              return {...this.getBasicParams(),
                      ...this.getFilterParams()}
          },

          ## nb. this is meant to call for a grid which is hidden at
          ## first, when it is first being shown to the user.  and if
          ## it was initialized with empty data set.
          async fetchFirstData() {
              if (this.fetchedFirstData) {
                  return
              }
              await this.loadAsyncData()
              this.fetchedFirstData = true
          },

          ## TODO: i noticed buefy docs show using `async` keyword here,
          ## so now i am too.  knowing nothing at all of if/how this is
          ## supposed to improve anything.  we shall see i guess
          async loadAsyncData(params, success, failure) {

              if (params === undefined || params === null) {
                  params = new URLSearchParams(this.getBasicParams())
              } else {
                  params = new URLSearchParams(params)
              }
              if (!params.has('partial')) {
                  params.append('partial', true)
              }
              params = params.toString()

              this.loading = true
              this.$http.get(`${'$'}{this.ajaxDataUrl}?${'$'}{params}`).then(response => {
                  if (!response.data.error) {
                      ${grid.vue_component}CurrentData = response.data.data
                      this.data = ${grid.vue_component}CurrentData
                      % if grid.paginated and grid.paginate_on_backend:
                          this.pagerStats = response.data.pager_stats
                      % endif
                      this.rowStatusMap = response.data.row_status_map || {}
                      this.loading = false
                      this.savingDefaults = false
                      this.checkedRows = this.locateCheckedRows(response.data.checked_rows || [])
                      if (success) {
                          success()
                      }
                  } else {
                      this.$buefy.toast.open({
                          message: response.data.error,
                          type: 'is-danger',
                          duration: 2000, // 4 seconds
                      })
                      this.loading = false
                      this.savingDefaults = false
                      if (failure) {
                          failure()
                      }
                  }
              })
              .catch((error) => {
                  ${grid.vue_component}CurrentData = []
                  this.data = []
                  % if grid.paginated and grid.paginate_on_backend:
                      this.pagerStats = {}
                  % endif
                  this.loading = false
                  this.savingDefaults = false
                  if (failure) {
                      failure()
                  }
                  throw error
              })
          },

          locateCheckedRows(checked) {
              let rows = []
              if (checked) {
                  for (let i = 0; i < this.data.length; i++) {
                      if (checked.includes(i)) {
                          rows.push(this.data[i])
                      }
                  }
              }
              return rows
          },

          onPageChange(page) {
              this.currentPage = page
              this.loadAsyncData()
          },

          perPageUpdated(value) {

              // nb. buefy passes value, oruga passes event
              if (value.target) {
                  value = event.target.value
              }

              this.loadAsyncData({
                  pagesize: value,
              })
          },

          % if grid.sortable and grid.sort_on_backend:

              onSort(field, order, event) {

                  ## nb. buefy passes field name; oruga passes field object
                  % if request.use_oruga:
                      field = field.field
                  % endif

                  % if grid.sort_multiple:

                      // did user ctrl-click the column header?
                      if (event.ctrlKey) {

                          // toggle direction for existing, or add new sorter
                          const sorter = this.sorters.filter(s => s.field === field)[0]
                          if (sorter) {
                              sorter.order = sorter.order === 'desc' ? 'asc' : 'desc'
                          } else {
                              this.sorters.push({field, order})
                          }

                          // apply multi-column sorting
                          this.sortingPriority = this.sorters

                      } else {

                  % endif

                  // sort by single column only
                  this.sorters = [{field, order}]

                  % if grid.sort_multiple:
                          // multi-column sort not engaged
                          this.sortingPriority = []
                      }
                  % endif

                  // nb. always reset to first page when sorting changes
                  this.currentPage = 1
                  this.loadAsyncData()
              },

              % if grid.sort_multiple:

                  sortingPriorityRemoved(field) {

                      // prune from active sorters
                      this.sorters = this.sorters.filter(s => s.field !== field)

                      // nb. even though we might have just one sorter
                      // now, we are still technically in multi-sort mode
                      this.sortingPriority = this.sorters

                      this.loadAsyncData()
                  },

              % endif

          % endif

          resetView() {
              this.loading = true

              // use current url proper, plus reset param
              let url = '?reset-view=true'

              // add current hash, to preserve that in redirect
              if (location.hash) {
                  url += '&hash=' + location.hash.slice(1)
              }

              location.href = url
          },

          addFilterInit() {
              this.addFilterShow = true

              this.$nextTick(() => {
                  const input = this.$refs.addFilterAutocomplete.$el.querySelector('input')
                  input.addEventListener('keydown', this.addFilterKeydown)
                  this.$refs.addFilterAutocomplete.focus()
              })
          },

          addFilterHide() {
              const input = this.$refs.addFilterAutocomplete.$el.querySelector('input')
              input.removeEventListener('keydown', this.addFilterKeydown)
              this.addFilterTerm = ''
              this.addFilterShow = false
          },

          addFilterKeydown(event) {

              // ESC will clear searchbox
              if (event.which == 27) {
                  this.addFilterHide()
              }
          },

          addFilterSelect(filtr) {
              this.addFilter(filtr.key)
              this.addFilterHide()
          },

          addFilter(filter_key) {

              // show corresponding grid filter
              this.filters[filter_key].visible = true
              this.filters[filter_key].active = true

              // track down the component
              var gridFilter = null
              for (var gf of this.$refs.gridFilters) {
                  if (gf.filter.key == filter_key) {
                      gridFilter = gf
                      break
                  }
              }

              // tell component to focus the value field, ASAP
              this.$nextTick(function() {
                  gridFilter.focusValue()
              })

          },

          applyFilters(params) {
              if (params === undefined) {
                  params = {}
              }

              // merge in actual filter params
              // cf. https://stackoverflow.com/a/171256
              params = {...params, ...this.getFilterParams()}

              // hide inactive filters
              for (var key in this.filters) {
                  var filter = this.filters[key]
                  if (!filter.active) {
                      filter.visible = false
                  }
              }

              // set some explicit params
              params.partial = true
              params.filter = true

              params = new URLSearchParams(params)
              this.loadAsyncData(params)
              this.appliedFiltersHook()
          },

          appliedFiltersHook() {},

          clearFilters() {

              // explicitly deactivate all filters
              for (var key in this.filters) {
                  this.filters[key].active = false
              }

              // then just "apply" as normal
              this.applyFilters()
          },

          // explicitly set filters for the grid, to the given set.
          // this totally overrides whatever might be current.  the
          // new filter set should look like:
          //
          //     [
          //         {key: 'status_code',
          //          verb: 'equal',
          //          value: 1},
          //         {key: 'description',
          //          verb: 'contains',
          //          value: 'whatever'},
          //     ]
          //
          setFilters(newFilters) {
              for (let key in this.filters) {
                  let filter = this.filters[key]
                  let active = false
                  for (let newFilter of newFilters) {
                      if (newFilter.key == key) {
                          active = true
                          filter.active = true
                          filter.visible = true
                          filter.verb = newFilter.verb
                          filter.value = newFilter.value
                          break
                      }
                  }
                  if (!active) {
                      filter.active = false
                      filter.visible = false
                  }
              }
              this.applyFilters()
          },

          saveDefaults() {
              this.savingDefaults = true

              // apply current filters as normal, but add special directive
              this.applyFilters({'save-current-filters-as-defaults': true})
          },

          deleteObject(event) {
              // we let parent component/app deal with this, in whatever way makes sense...
              // TODO: should we ever provide anything besides the URL for this?
              this.$emit('deleteActionClicked', event.target.href)
          },

          checkedRowUUIDs() {
              let uuids = []
              for (let row of this.$data.checkedRows) {
                  uuids.push(row.uuid)
              }
              return uuids
          },

          allRowUUIDs() {
              let uuids = []
              for (let row of this.data) {
                  uuids.push(row.uuid)
              }
              return uuids
          },

          // when a user clicks a row, handle as if they clicked checkbox.
          // note that this method is only used if table is "checkable"
          rowClick(row) {
              let i = this.checkedRows.indexOf(row)
              if (i >= 0) {
                  this.checkedRows.splice(i, 1)
              } else {
                  this.checkedRows.push(row)
              }
              % if getattr(grid, 'check_handler', None):
              this.${grid.check_handler}(this.checkedRows, row)
              % endif
          },
      }
  }

</script>
