## -*- coding: utf-8; -*-
<%inherit file="/page.mako" />

<%def name="title()">Inventory Worksheet</%def>

<%def name="page_content()">

  <p class="block">
    Please provide the following criteria to generate your report:
  </p>

  ${h.form(request.current_route_url())}
  ${h.csrf_token(request)}

  <b-field label="Department">
    <b-select name="department">
      <option v-for="dept in departments"
              :key="dept.uuid"
              :value="dept.uuid">
        {{ dept.name }}
      </option>
    </b-select>
  </b-field>

  <b-field>
    <b-checkbox name="weighted-only" native-value="1">
      Only include items which are sold by weight.
    </b-checkbox>
  </b-field>

  <b-field>
    <b-checkbox name="exclude-not-for-sale"
                v-model="excludeNotForSale"
                native-value="1">
      Exclude items marked "not for sale".
    </b-checkbox>
  </b-field>

  <div class="buttons">
    <b-button type="is-primary"
              native-type="submit"
              icon-pack="fas"
              icon-left="arrow-circle-right">
      Generate Report
    </b-button>
  </div>

  ${h.end_form()}
</%def>

<%def name="modify_vue_vars()">
  ${parent.modify_vue_vars()}
  <script>
    ThisPageData.departments = ${json.dumps([{'uuid': d.uuid, 'name': d.name} for d in departments])|n}
    ThisPageData.excludeNotForSale = true
  </script>
</%def>
