## -*- coding: utf-8 -*-
<%inherit file="/page.mako" />

<%def name="title()">Ordering Worksheet</%def>

<%def name="page_content()">

  <p class="block">
    Please provide the following criteria to generate your report:
  </p>

  <div style="max-width: 50%;">
    ${h.form(request.current_route_url(), **{'@submit': 'validateForm'})}
    ${h.csrf_token(request)}
    ${h.hidden('departments', **{':value': 'departmentUUIDs'})}

    <b-field label="Vendor">
      <tailbone-autocomplete v-model="vendorUUID"
                             service-url="${url('vendors.autocomplete')}"
                             name="vendor"
                             expanded
                             % if request.use_oruga:
                                 @update:model-value="vendorChanged"
                             % else:
                                 @input="vendorChanged"
                             % endif
                             >
      </tailbone-autocomplete>
    </b-field>

    <b-field label="Departments">
      <${b}-table v-if="fetchedDepartments"
                  :data="departments"
                  narrowed
                  checkable
                  % if request.use_oruga:
                      v-model:checked-rows="checkedDepartments"
                  % else:
                      :checked-rows.sync="checkedDepartments"
                  % endif
                  :loading="fetchingDepartments">

        <${b}-table-column field="number"
                        label="Number"
                        v-slot="props">
          {{ props.row.number }}
        </${b}-table-column>

        <${b}-table-column field="name"
                        label="Name"
                        v-slot="props">
          {{ props.row.name }}
        </${b}-table-column>

      </${b}-table>
    </b-field>

    <b-field>
      <b-checkbox name="preferred_only"
                  v-model="preferredVendorOnly"
                  native-value="1">
        Only include products for which this vendor is preferred.
      </b-checkbox>
    </b-field>

    ${self.extra_fields()}

    <div class="buttons">
      <b-button type="is-primary"
                native-type="submit"
                icon-pack="fas"
                icon-left="arrow-circle-right">
        Generate Report
      </b-button>
    </div>

    ${h.end_form()}
  </div>

</%def>

<%def name="extra_fields()"></%def>

<%def name="modify_vue_vars()">
  ${parent.modify_vue_vars()}
  <script>

    ThisPageData.vendorUUID = null
    ThisPageData.departments = []
    ThisPageData.checkedDepartments = []
    ThisPageData.preferredVendorOnly = true
    ThisPageData.fetchingDepartments = false
    ThisPageData.fetchedDepartments = false

    ThisPage.computed.departmentUUIDs = function() {
        let uuids = []
        for (let dept of this.checkedDepartments) {
            uuids.push(dept.uuid)
        }
        return uuids.join(',')
    }

    ThisPage.methods.vendorChanged = function(uuid) {
        if (uuid) {
            this.fetchingDepartments = true

            let url = '${url('departments.by_vendor')}'
            let params = {uuid: uuid}
            this.$http.get(url, {params: params}).then(response => {
                this.departments = response.data
                this.fetchingDepartments = false
                this.fetchedDepartments = true
            })

        } else {
            this.departments = []
            this.fetchedDepartments = false
        }
    }

    ThisPage.methods.validateForm = function(event) {
        if (!this.departmentUUIDs.length) {
            alert("You must select at least one Department.")
            event.preventDefault()
        }
    }

  </script>
</%def>
