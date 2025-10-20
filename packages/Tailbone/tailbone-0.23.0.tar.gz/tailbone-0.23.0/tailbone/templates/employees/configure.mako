## -*- coding: utf-8; -*-
<%inherit file="/configure.mako" />

<%def name="form_content()">

  <h3 class="block is-size-3">General</h3>
  <div class="block" style="padding-left: 2rem;">

    <b-field message="If set, grid links are to Employee tab of Profile view.">
      <b-checkbox name="rattail.employees.straight_to_profile"
                  v-model="simpleSettings['rattail.employees.straight_to_profile']"
                  native-value="true"
                  @input="settingsNeedSaved = true">
        Link directly to Profile when applicable
      </b-checkbox>
    </b-field>

  </div>
</%def>


${parent.body()}
