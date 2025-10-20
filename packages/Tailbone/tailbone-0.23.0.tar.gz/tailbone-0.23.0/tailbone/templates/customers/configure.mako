## -*- coding: utf-8; -*-
<%inherit file="/configure.mako" />

<%def name="form_content()">

  <h3 class="block is-size-3">General</h3>
  <div class="block" style="padding-left: 2rem;">

    <b-field grouped>

      <b-field label="Key Field">
        <b-select name="rattail.customers.key_field"
                  v-model="simpleSettings['rattail.customers.key_field']"
                  @input="updateKeyLabel()">
          <option value="id">id</option>
          <option value="number">number</option>
        </b-select>
      </b-field>

      <b-field label="Key Field Label">
        <b-input name="rattail.customers.key_label"
                 v-model="simpleSettings['rattail.customers.key_label']"
                 @input="settingsNeedSaved = true">
        </b-input>
      </b-field>

    </b-field>

    <b-field message="If set, grid links are to Customer tab of Profile view.">
      <b-checkbox name="rattail.customers.straight_to_profile"
                  v-model="simpleSettings['rattail.customers.straight_to_profile']"
                  native-value="true"
                  @input="settingsNeedSaved = true">
        Link directly to Profile when applicable
      </b-checkbox>
    </b-field>

    <b-field message="Set this to show the Shoppers field when viewing a Customer record.">
      <b-checkbox name="rattail.customers.expose_shoppers"
                  v-model="simpleSettings['rattail.customers.expose_shoppers']"
                  native-value="true"
                  @input="settingsNeedSaved = true">
        Show the Shoppers field
      </b-checkbox>
    </b-field>

    <b-field message="Set this to show the People field when viewing a Customer record.">
      <b-checkbox name="rattail.customers.expose_people"
                  v-model="simpleSettings['rattail.customers.expose_people']"
                  native-value="true"
                  @input="settingsNeedSaved = true">
        Show the People field
      </b-checkbox>
    </b-field>

    <b-field message="If not set, Customer chooser is an autocomplete field.">
      <b-checkbox name="rattail.customers.choice_uses_dropdown"
                  v-model="simpleSettings['rattail.customers.choice_uses_dropdown']"
                  native-value="true"
                  @input="settingsNeedSaved = true">
        Use dropdown (select element) for Customer chooser
      </b-checkbox>
    </b-field>

    <b-field label="Clientele Handler"
             message="Leave blank for default handler.">
      <b-input name="rattail.clientele.handler"
               v-model="simpleSettings['rattail.clientele.handler']"
               @input="settingsNeedSaved = true">
      </b-input>
    </b-field>

  </div>

  <h3 class="block is-size-3">POS</h3>
  <div class="block" style="padding-left: 2rem;">

    <b-field>
      <b-checkbox name="rattail.customers.active_in_pos"
                  v-model="simpleSettings['rattail.customers.active_in_pos']"
                  native-value="true"
                  @input="settingsNeedSaved = true">
        Expose/track the "Active in POS" flag for customers.
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
        this.simpleSettings['rattail.customers.key_label'] = this.getLabelForKey(
            this.simpleSettings['rattail.customers.key_field'])
        this.settingsNeedSaved = true
    }

  </script>
</%def>
