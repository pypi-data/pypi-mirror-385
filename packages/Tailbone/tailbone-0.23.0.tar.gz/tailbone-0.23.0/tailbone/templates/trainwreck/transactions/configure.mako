## -*- coding: utf-8; -*-
<%inherit file="/configure.mako" />

<%def name="form_content()">

  <h3 class="block is-size-3">Display</h3>
  <div class="block" style="padding-left: 2rem;">

    <b-field>
      <b-checkbox name="tailbone.trainwreck.view_txn.autocollapse_header"
                  v-model="simpleSettings['tailbone.trainwreck.view_txn.autocollapse_header']"
                  native-value="true"
                  @input="settingsNeedSaved = true">
        Auto-collapse header when viewing transaction
      </b-checkbox>
    </b-field>
  </div>

  <h3 class="block is-size-3">Rotation</h3>
  <div class="block" style="padding-left: 2rem;">

    <b-field message="There is only one Trainwreck DB, unless rotation is used.">
      <b-checkbox name="trainwreck.use_rotation"
                  v-model="simpleSettings['trainwreck.use_rotation']"
                  native-value="true"
                  @input="settingsNeedSaved = true">
        Rotate Databases
      </b-checkbox>
    </b-field>

    <b-field grouped>
      <b-field label="Current Years"
               message="How many years (max) to keep in &quot;current&quot; DB.  Default is 2 if not set.">
        <b-input name="trainwreck.current_years"
                 v-model="simpleSettings['trainwreck.current_years']"
                 @input="settingsNeedSaved = true">
        </b-input>
      </b-field>
    </b-field>

  </div>

  <h3 class="block is-size-3">Hidden Databases</h3>
  <div class="block" style="padding-left: 2rem;">
    <p class="block">
      The selected DBs will be hidden from the DB picker when viewing
      Trainwreck data.
    </p>
    % for key, engine in trainwreck_engines.items():
        <b-field>
          <b-checkbox name="hidedb_${key}"
                      v-model="hiddenDatabases['${key}']"
                      native-value="true"
                      % if key == 'default':
                      disabled
                      % endif
                      @input="settingsNeedSaved = true">
            ${key}
          </b-checkbox>
        </b-field>
    % endfor
  </div>
</%def>

<%def name="modify_vue_vars()">
  ${parent.modify_vue_vars()}
  <script>
    ThisPageData.hiddenDatabases = ${json.dumps(hidden_databases)|n}
  </script>
</%def>
