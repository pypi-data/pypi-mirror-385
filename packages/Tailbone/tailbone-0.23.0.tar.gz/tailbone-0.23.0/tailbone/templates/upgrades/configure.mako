## -*- coding: utf-8; -*-
<%inherit file="/configure.mako" />

<%def name="form_content()">
  ${h.hidden('upgrade_systems', **{':value': 'JSON.stringify(upgradeSystems)'})}

  <h3 class="is-size-3">Upgradable Systems</h3>
  <div class="block" style="padding-left: 2rem; display: flex;">

    <${b}-table :data="upgradeSystems"
             sortable>
      <${b}-table-column field="key"
                      label="Key"
                      v-slot="props"
                      sortable>
        {{ props.row.key }}
      </${b}-table-column>
      <${b}-table-column field="label"
                      label="Label"
                      v-slot="props"
                      sortable>
        {{ props.row.label }}
      </${b}-table-column>
      <${b}-table-column field="command"
                      label="Command"
                      v-slot="props"
                      sortable>
        {{ props.row.command }}
      </${b}-table-column>
      <${b}-table-column label="Actions"
                      v-slot="props">
        <a href="#"
           @click.prevent="upgradeSystemEdit(props.row)">
          % if request.use_oruga:
              <o-icon icon="edit" />
          % else:
              <i class="fas fa-edit"></i>
          % endif
          Edit
        </a>
        &nbsp;
        <a href="#"
           v-if="props.row.key != 'rattail'"
           class="has-text-danger"
           @click.prevent="updateSystemDelete(props.row)">
          % if request.use_oruga:
              <o-icon icon="trash" />
          % else:
              <i class="fas fa-trash"></i>
          % endif
          Delete
        </a>
      </${b}-table-column>
    </${b}-table>

    <div style="margin-left: 1rem;">
      <b-button type="is-primary"
                icon-pack="fas"
                icon-left="plus"
                @click="upgradeSystemCreate()">
        New System
      </b-button>

      <b-modal has-modal-card
               :active.sync="upgradeSystemShowDialog">
        <div class="modal-card">

          <header class="modal-card-head">
            <p class="modal-card-title">Upgradable System</p>
          </header>

          <section class="modal-card-body">
            <b-field label="Key"
                     :type="upgradeSystemKey ? null : 'is-danger'">
              <b-input v-model.trim="upgradeSystemKey"
                       ref="upgradeSystemKey"
                       :disabled="upgradeSystemKey == 'rattail'"
                       expanded />
            </b-field>
            <b-field label="Label"
                     :type="upgradeSystemLabel ? null : 'is-danger'">
              <b-input v-model.trim="upgradeSystemLabel"
                       ref="upgradeSystemLabel"
                       :disabled="upgradeSystemKey == 'rattail'"
                       expanded />
            </b-field>
            <b-field label="Command"
                     :type="upgradeSystemCommand ? null : 'is-danger'">
              <b-input v-model.trim="upgradeSystemCommand"
                       ref="upgradeSystemCommand"
                       expanded />
            </b-field>
          </section>

          <footer class="modal-card-foot">
            <b-button type="is-primary"
                      icon-pack="fas"
                      icon-left="save"
                      @click="upgradeSystemSave()"
                      :disabled="!upgradeSystemKey || !upgradeSystemLabel || !upgradeSystemCommand">
              Save
            </b-button>
            <b-button @click="upgradeSystemShowDialog = false">
              Cancel
            </b-button>
          </footer>
        </div>
      </b-modal>

    </div>
  </div>
</%def>

<%def name="modify_vue_vars()">
  ${parent.modify_vue_vars()}
  <script>

    ThisPageData.upgradeSystems = ${json.dumps(upgrade_systems)|n}
    ThisPageData.upgradeSystemShowDialog = false
    ThisPageData.upgradeSystem = null
    ThisPageData.upgradeSystemKey = null
    ThisPageData.upgradeSystemLabel = null
    ThisPageData.upgradeSystemCommand = null

    ThisPage.methods.upgradeSystemCreate = function() {
        this.upgradeSystem = null
        this.upgradeSystemKey = null
        this.upgradeSystemLabel = null
        this.upgradeSystemCommand = null
        this.upgradeSystemShowDialog = true
        this.$nextTick(() => {
            this.$refs.upgradeSystemKey.focus()
        })
    }

    ThisPage.methods.upgradeSystemEdit = function(system) {
        this.upgradeSystem = system
        this.upgradeSystemKey = system.key
        this.upgradeSystemLabel = system.label
        this.upgradeSystemCommand = system.command
        this.upgradeSystemShowDialog = true
        this.$nextTick(() => {
            this.$refs.upgradeSystemCommand.focus()
        })
    }

    ThisPage.methods.upgradeSystemSave = function() {
        if (this.upgradeSystem) {
            this.upgradeSystem.key = this.upgradeSystemKey
            this.upgradeSystem.label = this.upgradeSystemLabel
            this.upgradeSystem.command = this.upgradeSystemCommand
        } else {
            let system = {key: this.upgradeSystemKey,
                          label: this.upgradeSystemLabel,
                          command: this.upgradeSystemCommand}
            this.upgradeSystems.push(system)
        }
        this.upgradeSystemShowDialog = false
        this.settingsNeedSaved = true
    }

  </script>
</%def>
