## -*- coding: utf-8; -*-
<%inherit file="/page.mako" />

<%def name="title()">Find ${model_title_plural} by Permission</%def>

<%def name="page_content()">
  <br />
  <find-principals :permission-groups="permissionGroups"
                   :sorted-groups="sortedGroups">
  </find-principals>
</%def>

<%def name="principal_table()">
  <div
    style="width: 50%;"
    >
    ${grid.render_table_element(data_prop='principalsData')|n}
  </div>
</%def>

<%def name="render_vue_templates()">
  ${parent.render_vue_templates()}
  <script type="text/x-template" id="find-principals-template">
    <div>

      ${h.form(request.url, method='GET', **{'@submit': 'formSubmitting = true'})}
        <div style="margin-left: 10rem; max-width: 50%;">

          ${h.hidden('permission_group', **{':value': 'selectedGroup'})}
          <b-field label="Permission Group" horizontal>
            <b-autocomplete v-if="!selectedGroup"
                            ref="permissionGroupAutocomplete"
                            v-model="permissionGroupTerm"
                            :data="permissionGroupChoices"
                            :custom-formatter="filtr => filtr.label"
                            open-on-focus
                            keep-first
                            icon-pack="fas"
                            clearable
                            clear-on-select
                            expanded
                            @select="permissionGroupSelect">
            </b-autocomplete>
            <b-button v-if="selectedGroup"
                      @click="permissionGroupReset()">
              {{ permissionGroups[selectedGroup].label }}
            </b-button>
          </b-field>

          ${h.hidden('permission', **{':value': 'selectedPermission'})}
          <b-field label="Permission" horizontal>
            <b-autocomplete v-if="!selectedPermission"
                            ref="permissionAutocomplete"
                            v-model="permissionTerm"
                            :data="permissionChoices"
                            :custom-formatter="filtr => filtr.label"
                            open-on-focus
                            keep-first
                            icon-pack="fas"
                            clearable
                            clear-on-select
                            expanded
                            @select="permissionSelect">
            </b-autocomplete>
            <b-button v-if="selectedPermission"
                      @click="permissionReset()">
              {{ selectedPermissionLabel }}
            </b-button>
          </b-field>

          <b-field horizontal>
            <div class="buttons" style="margin-top: 1rem;">
              <once-button tag="a"
                           href="${request.path_url}"
                           text="Reset Form">
              </once-button>
              <b-button type="is-primary"
                        native-type="submit"
                        icon-pack="fas"
                        icon-left="search"
                        :disabled="formSubmitting">
                {{ formSubmitting ? "Working, please wait..." : "Find ${model_title_plural}" }}
              </b-button>
            </div>
          </b-field>

        </div>
      ${h.end_form()}

      % if principals is not None:
          <br />
          <p class="block">
            Found ${len(principals)} ${model_title_plural} with permission:
            <span class="has-text-weight-bold">${selected_permission}</span>
          </p>
          ${self.principal_table()}
      % endif

    </div>
  </script>
  <script type="text/javascript">

    const FindPrincipals = {
        template: '#find-principals-template',
        props: {
            permissionGroups: Object,
            sortedGroups: Array
        },
        data() {
            return {
                groupPermissions: ${json.dumps(perms_data.get(selected_group, {}).get('permissions', []))|n},
                permissionGroupTerm: '',
                permissionTerm: '',
                selectedGroup: ${json.dumps(selected_group)|n},
                selectedPermission: ${json.dumps(selected_permission)|n},
                selectedPermissionLabel: ${json.dumps(selected_permission_label or '')|n},
                formSubmitting: false,
                principalsData: ${json.dumps(principals_data)|n},
            }
        },

        computed: {

            permissionGroupChoices() {

                // collect all groups
                let choices = []
                for (let groupkey of this.sortedGroups) {
                    choices.push(this.permissionGroups[groupkey])
                }

                // parse list of search terms
                let terms = []
                for (let term of this.permissionGroupTerm.toLowerCase().split(' ')) {
                    term = term.trim()
                    if (term) {
                        terms.push(term)
                    }
                }

                // filter groups by search terms
                choices = choices.filter(option => {
                    let label = option.label.toLowerCase()
                    for (let term of terms) {
                        if (label.indexOf(term) < 0) {
                            return false
                        }
                    }
                    return true
                })

                return choices
            },

            permissionChoices() {

                // collect all permissions for current group
                let choices = this.groupPermissions

                // parse list of search terms
                let terms = []
                for (let term of this.permissionTerm.toLowerCase().split(' ')) {
                    term = term.trim()
                    if (term) {
                        terms.push(term)
                    }
                }

                // filter permissions by search terms
                choices = choices.filter(option => {
                    let label = option.label.toLowerCase()
                    for (let term of terms) {
                        if (label.indexOf(term) < 0) {
                            return false
                        }
                    }
                    return true
                })

                return choices
            },
        },

        methods: {

            navigateTo(url) {
                location.href = url
            },

            permissionGroupSelect(option) {
                this.selectedPermission = null
                this.selectedPermissionLabel = null
                if (option) {
                    this.selectedGroup = option.groupkey
                    this.groupPermissions = this.permissionGroups[option.groupkey].permissions
                    this.$nextTick(() => {
                        this.$refs.permissionAutocomplete.focus()
                    })
                }
            },

            permissionGroupReset() {
                this.selectedGroup = null
                this.selectedPermission = null
                this.selectedPermissionLabel = ''
                this.$nextTick(() => {
                    this.$refs.permissionGroupAutocomplete.focus()
                })
            },

            permissionSelect(option) {
                if (option) {
                    this.selectedPermission = option.permkey
                    this.selectedPermissionLabel = option.label
                }
            },

            permissionReset() {
                this.selectedPermission = null
                this.selectedPermissionLabel = null
                this.permissionTerm = ''
                this.$nextTick(() => {
                    this.$refs.permissionAutocomplete.focus()
                })
            },
        }
    }

  </script>
</%def>

<%def name="modify_vue_vars()">
  ${parent.modify_vue_vars()}
  <script>
    ThisPageData.permissionGroups = ${json.dumps(perms_data)|n}
    ThisPageData.sortedGroups = ${json.dumps(sorted_groups_data)|n}
  </script>
</%def>

<%def name="make_vue_components()">
  ${parent.make_vue_components()}
  <script>
    Vue.component('find-principals', FindPrincipals)
    <% request.register_component('find-principals', 'FindPrincipals') %>
  </script>
</%def>
