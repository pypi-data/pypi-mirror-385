## -*- coding: utf-8; -*-
<%inherit file="/configure.mako" />

<%def name="form_content()">

  <h3 class="block is-size-3">General</h3>
  <div class="block" style="padding-left: 2rem; width: 50%;">

    <b-field message="If set, grid links are to Personal tab of Profile view.">
      <b-checkbox name="rattail.people.straight_to_profile"
                  v-model="simpleSettings['rattail.people.straight_to_profile']"
                  native-value="true"
                  @input="settingsNeedSaved = true">
        Link directly to Profile when applicable
      </b-checkbox>
    </b-field>

    <b-field message="Allows quick profile lookup using e.g. customer number.">
      <b-checkbox name="rattail.people.expose_quickie_search"
                  v-model="simpleSettings['rattail.people.expose_quickie_search']"
                  native-value="true"
                  @input="settingsNeedSaved = true">
        Show "quickie search" lookup
      </b-checkbox>
    </b-field>

    <b-field label="People Handler"
             message="Leave blank for default handler.">
      <b-input name="rattail.people.handler"
               v-model="simpleSettings['rattail.people.handler']"
               @input="settingsNeedSaved = true"
               expanded />
    </b-field>

  </div>

  <h3 class="block is-size-3">Profile View</h3>
  <div class="block" style="padding-left: 2rem; width: 50%;">

    <b-field>
      <b-checkbox name="tailbone.people.profile.expose_members"
                  v-model="simpleSettings['tailbone.people.profile.expose_members']"
                  native-value="true"
                  @input="settingsNeedSaved = true">
        Show tab for Member Accounts
      </b-checkbox>
    </b-field>
    <b-field>
      <b-checkbox name="tailbone.people.profile.expose_transactions"
                  v-model="simpleSettings['tailbone.people.profile.expose_transactions']"
                  native-value="true"
                  @input="settingsNeedSaved = true">
        Show tab for Customer POS Transactions
      </b-checkbox>
    </b-field>

  </div>
</%def>


${parent.body()}
