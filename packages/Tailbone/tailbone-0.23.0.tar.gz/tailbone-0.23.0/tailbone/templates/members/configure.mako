## -*- coding: utf-8; -*-
<%inherit file="/configure.mako" />

<%def name="form_content()">

  <h3 class="block is-size-3">General</h3>
  <div class="block" style="padding-left: 2rem;">

    <b-field grouped>

      <b-field label="Key Field">
        <b-select name="rattail.members.key_field"
                  v-model="simpleSettings['rattail.members.key_field']"
                  @input="updateKeyLabel()">
          <option value="id">id</option>
          <option value="number">number</option>
        </b-select>
      </b-field>

      <b-field label="Key Field Label">
        <b-input name="rattail.members.key_label"
                 v-model="simpleSettings['rattail.members.key_label']"
                 @input="settingsNeedSaved = true">
        </b-input>
      </b-field>

    </b-field>

    <b-field message="If set, grid links are to Member tab of Profile view.">
      <b-checkbox name="rattail.members.straight_to_profile"
                  v-model="simpleSettings['rattail.members.straight_to_profile']"
                  native-value="true"
                  @input="settingsNeedSaved = true">
        Link directly to Profile when applicable
      </b-checkbox>
    </b-field>

  </div>

  <h3 class="block is-size-3">Relationships</h3>
  <div class="block" style="padding-left: 2rem;">

    <b-field message="By default a Person may have multiple Member accounts.">
      <b-checkbox name="rattail.members.max_one_per_person"
                  v-model="simpleSettings['rattail.members.max_one_per_person']"
                  native-value="true"
                  @input="settingsNeedSaved = true">
        Limit one (1) Member account per Person
      </b-checkbox>
    </b-field>

  </div>
</%def>

<%def name="modify_vue_vars()">
  ${parent.modify_vue_vars()}
  <script>

    ThisPage.methods.getLabelForKey = function(key) {
        switch (key) {
        case 'id':
            return "ID"
        case 'number':
            return "Number"
        default:
            return "Key"
        }
    }

    ThisPage.methods.updateKeyLabel = function() {
        this.simpleSettings['rattail.members.key_label'] = this.getLabelForKey(
            this.simpleSettings['rattail.members.key_field'])
        this.settingsNeedSaved = true
    }

  </script>
</%def>
