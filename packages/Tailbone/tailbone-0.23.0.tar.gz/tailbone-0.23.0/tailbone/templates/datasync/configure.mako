## -*- coding: utf-8; -*-
<%inherit file="/configure.mako" />

<%def name="extra_styles()">
  ${parent.extra_styles()}
  <style>
    .invisible-watcher {
        display: none;
    }
  </style>
</%def>

<%def name="buttons_row()">
  <div class="level">
    <div class="level-left">

      <div class="level-item">
        <p class="block">
          This tool lets you modify the DataSync configuration.&nbsp;
          Before using it,
          <a href="#" class="has-background-warning"
             @click.prevent="showConfigFilesNote = !showConfigFilesNote">
            please see these notes.
          </a>
        </p>
      </div>

      <div class="level-item">
        ${self.save_undo_buttons()}
      </div>
    </div>

    <div class="level-right">

      <div class="level-item">
        ${h.form(url('datasync.restart'), **{'@submit': 'submitRestartDatasyncForm'})}
        ${h.csrf_token(request)}
        <b-button type="is-primary"
                  native-type="submit"
                  @click="restartDatasync"
                  :disabled="restartingDatasync"
                  icon-pack="fas"
                  icon-left="redo">
          {{ restartDatasyncFormButtonText }}
        </b-button>
        ${h.end_form()}
      </div>

      <div class="level-item">
        ${self.purge_button()}
      </div>
    </div>
  </div>
</%def>

<%def name="form_content()">
  ${h.hidden('profiles', **{':value': 'JSON.stringify(profilesData)'})}

  <b-notification type="is-warning"
                  % if request.use_oruga:
                  v-model:active="showConfigFilesNote"
                  % else:
                  :active.sync="showConfigFilesNote"
                  % endif
                  >
    ## TODO: should link to some ratman page here, yes?
    <p class="block">
      This tool works by modifying settings in the DB.&nbsp; It
      does <span class="is-italic">not</span> modify any config
      files.&nbsp; If you intend to manage datasync watcher/consumer
      config via files only then you should be sure to UNCHECK the
      "Use these Settings.." checkbox near the top of page.
    </p>
    <p class="block">
      If you have managed config via files thus far, and want to
      start using this tool to manage via DB settings instead,
      that&apos;s fine - but after saving the settings via this tool
      you should probably remove all
      <span class="is-family-code">[rattail.datasync]</span> entries
      from your config file (and restart apps) so as to avoid
      confusion.
    </p>
  </b-notification>

  <b-field>
    <b-checkbox name="rattail.datasync.use_profile_settings"
                v-model="simpleSettings['rattail.datasync.use_profile_settings']"
                native-value="true"
                @input="settingsNeedSaved = true">
      Use these Settings to configure watchers and consumers
    </b-checkbox>
  </b-field>

  <div class="level">
    <div class="level-left">
      <div class="level-item">
        <h3 class="is-size-3">Watcher Profiles</h3>
      </div>
    </div>
    <div class="level-right">
      <div class="level-item"
           v-show="simpleSettings['rattail.datasync.use_profile_settings']">
        <b-button type="is-primary"
                  @click="newProfile()"
                  icon-pack="fas"
                  icon-left="plus">
          New Profile
        </b-button>
      </div>
      <div class="level-item">
        <b-button @click="toggleDisabledProfiles()">
          {{ showDisabledProfiles ? "Hide" : "Show" }} Disabled
        </b-button>
      </div>
    </div>
  </div>

  <${b}-table :data="profilesData"
              :row-class="getWatcherRowClass">
      <${b}-table-column field="key"
                      label="Watcher Key"
                      v-slot="props">
        {{ props.row.key }}
      </${b}-table-column>
      <${b}-table-column field="watcher_spec"
                      label="Watcher Spec"
                      v-slot="props">
        {{ props.row.watcher_spec }}
      </${b}-table-column>
      <${b}-table-column field="watcher_dbkey"
                      label="DB Key"
                      v-slot="props">
        {{ props.row.watcher_dbkey }}
      </${b}-table-column>
      <${b}-table-column field="watcher_delay"
                      label="Loop Delay"
                      v-slot="props">
        {{ props.row.watcher_delay }} sec
      </${b}-table-column>
      <${b}-table-column field="watcher_retry_attempts"
                      label="Attempts / Delay"
                      v-slot="props">
        {{ props.row.watcher_retry_attempts }} / {{ props.row.watcher_retry_delay }} sec
      </${b}-table-column>
      <${b}-table-column field="watcher_default_runas"
                      label="Default Runas"
                      v-slot="props">
        {{ props.row.watcher_default_runas }}
      </${b}-table-column>
      <${b}-table-column label="Consumers"
                      v-slot="props">
        {{ consumerShortList(props.row) }}
      </${b}-table-column>
##         <${b}-table-column field="notes" label="Notes">
##           TODO
##           ## {{ props.row.notes }}
##         </${b}-table-column>
      <${b}-table-column field="enabled"
                      label="Enabled"
                      v-slot="props">
        {{ props.row.enabled ? "Yes" : "No" }}
      </${b}-table-column>
      <${b}-table-column label="Actions"
                      v-slot="props"
                      v-if="simpleSettings['rattail.datasync.use_profile_settings']">
        <a href="#"
           class="grid-action"
           @click.prevent="editProfile(props.row)">
          % if request.use_oruga:
              <span class="icon-text">
                <o-icon icon="edit" />
                <span>Edit</span>
              </span>
          % else:
              <i class="fas fa-edit"></i>
              Edit
          % endif
        </a>
        &nbsp;
        <a href="#"
           class="grid-action has-text-danger"
           @click.prevent="deleteProfile(props.row)">
          % if request.use_oruga:
              <span class="icon-text">
                <o-icon icon="trash" />
                <span>Delete</span>
              </span>
          % else:
              <i class="fas fa-trash"></i>
              Delete
          % endif
        </a>
      </${b}-table-column>
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
  </${b}-table>

  <b-modal :active.sync="editProfileShowDialog">
    <div class="card">
      <div class="card-content">

        <b-field grouped>
          
          <b-field label="Watcher Key"
                   :type="editingProfileKey ? null : 'is-danger'">
            <b-input v-model="editingProfileKey"
                     ref="watcherKeyInput">
            </b-input>
          </b-field>

          <b-field label="Default Runas User">
            <b-input v-model="editingProfileWatcherDefaultRunas">
            </b-input>
          </b-field>

        </b-field>

        <b-field grouped expanded>

          <b-field label="Watcher Spec" 
                   :type="editingProfileWatcherSpec ? null : 'is-danger'"
                   expanded>
            <b-input v-model="editingProfileWatcherSpec" expanded>
            </b-input>
          </b-field>

          <b-field label="DB Key">
            <b-input v-model="editingProfileWatcherDBKey">
            </b-input>
          </b-field>

        </b-field>

        <b-field grouped>

          <b-field label="Loop Delay (seconds)">
            <b-input v-model="editingProfileWatcherDelay">
            </b-input>
          </b-field>

          <b-field label="Attempts">
            <b-input v-model="editingProfileWatcherRetryAttempts">
            </b-input>
          </b-field>

          <b-field label="Retry Delay (seconds)">
            <b-input v-model="editingProfileWatcherRetryDelay">
            </b-input>
          </b-field>

          <b-field :label="`Kwargs (${'$'}{editingProfilePendingWatcherKwargs.length})`">
            <b-button type="is-primary"
                      icon-pack="fas"
                      icon-left="edit"
                      :disabled="editingWatcherKwarg"
                      @click="editingWatcherKwargs = !editingWatcherKwargs">
              {{ editingWatcherKwargs ? "Stop Editing" : "Edit Kwargs" }}
            </b-button>
          </b-field>

        </b-field>

        <div v-show="editingWatcherKwargs"
             style="display: flex; justify-content: end;">

          <b-button type="is-primary"
                    v-show="!editingWatcherKwarg"
                    icon-pack="fas"
                    icon-left="plus"
                    @click="newWatcherKwarg()">
            New Watcher Kwarg
          </b-button>

          <div v-show="editingWatcherKwarg">

            <b-field grouped>

              <b-field label="Key"
                       :type="editingWatcherKwargKey ? null : 'is-danger'">
                <b-input v-model="editingWatcherKwargKey"
                         ref="watcherKwargKey">
                </b-input>
              </b-field>

              <b-field label="Value"
                       :type="editingWatcherKwargValue ? null : 'is-danger'">
                <b-input v-model="editingWatcherKwargValue">
                </b-input>
              </b-field>

            </b-field>

            <b-field grouped>

              <b-button @click="editingWatcherKwarg = null"
                        class="control"
                        >
                Cancel
              </b-button>

              <b-button type="is-primary"
                        @click="updateWatcherKwarg()"
                        class="control">
                Update Kwarg
              </b-button>

            </b-field>

          </div>


          <${b}-table :data="editingProfilePendingWatcherKwargs"
                   style="margin-left: 1rem;">
            <${b}-table-column field="key"
                            label="Key"
                            v-slot="props">
              {{ props.row.key }}
            </${b}-table-column>
            <${b}-table-column field="value"
                            label="Value"
                            v-slot="props">
              {{ props.row.value }}
            </${b}-table-column>
            <${b}-table-column label="Actions"
                            v-slot="props">
              <a href="#"
                 @click.prevent="editProfileWatcherKwarg(props.row)">
                % if request.use_oruga:
                    <span class="icon-text">
                      <o-icon icon="edit" />
                      <span>Edit</span>
                    </span>
                % else:
                    <i class="fas fa-edit"></i>
                    Edit
                % endif
              </a>
              &nbsp;
              <a href="#"
                 class="has-text-danger"
                 @click.prevent="deleteProfileWatcherKwarg(props.row)">
                % if request.use_oruga:
                    <span class="icon-text">
                      <o-icon icon="trash" />
                      <span>Delete</span>
                    </span>
                % else:
                    <i class="fas fa-trash"></i>
                    Delete
                % endif
              </a>
            </${b}-table-column>
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
          </${b}-table>

        </div>

        <div v-show="!editingWatcherKwargs"
             style="display: flex;">

          <div style="width: 40%;">

            <b-field label="Watcher consumes its own changes"
                     v-if="!editingProfilePendingConsumers.length">
              <b-checkbox v-model="editingProfileWatcherConsumesSelf">
                {{ editingProfileWatcherConsumesSelf ? "Yes" : "No" }}
              </b-checkbox>
            </b-field>

            <${b}-table :data="editingProfilePendingConsumers"
                     v-if="!editingProfileWatcherConsumesSelf"
                     :row-class="(row, i) => row.enabled ? null : 'has-background-warning'">
              <${b}-table-column field="key"
                              label="Consumer"
                              v-slot="props">
                {{ props.row.key }}
              </${b}-table-column>
              <${b}-table-column style="white-space: nowrap;"
                              v-slot="props">
                {{ props.row.consumer_delay }} / {{ props.row.consumer_retry_attempts }} / {{ props.row.consumer_retry_delay }}
              </${b}-table-column>
              <${b}-table-column label="Actions"
                              v-slot="props">
                <a href="#"
                   class="grid-action"
                   @click.prevent="editProfileConsumer(props.row)">
                  % if request.use_oruga:
                      <span class="icon-text">
                        <o-icon icon="edit" />
                        <span>Edit</span>
                      </span>
                  % else:
                      <i class="fas fa-edit"></i>
                      Edit
                  % endif
                </a>
                &nbsp;
                <a href="#"
                   class="grid-action has-text-danger"
                   @click.prevent="deleteProfileConsumer(props.row)">
                  % if request.use_oruga:
                      <span class="icon-text">
                        <o-icon icon="trash" />
                        <span>Delete</span>
                      </span>
                  % else:
                      <i class="fas fa-trash"></i>
                      Delete
                  % endif
                </a>
              </${b}-table-column>
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
            </${b}-table>

          </div>

          <div v-show="!editingConsumer && !editingProfileWatcherConsumesSelf"
               style="padding-left: 1rem;">
            <b-button type="is-primary"
                      @click="newConsumer()"
                      icon-pack="fas"
                      icon-left="plus">
              New Consumer
            </b-button>
          </div>

          <div v-show="editingConsumer"
               style="flex-grow: 1; padding-left: 1rem; padding-right: 1rem;">
            
            <b-field grouped>

              <b-field label="Consumer Key"
                       :type="editingConsumerKey ? null : 'is-danger'">
                <b-input v-model="editingConsumerKey"
                         ref="consumerKeyInput">
                </b-input>
              </b-field>

              <b-field label="Runas User">
                <b-input v-model="editingConsumerRunas">
                </b-input>
              </b-field>

            </b-field>

            <b-field grouped>

              <b-field label="Consumer Spec" 
                       expanded
                       :type="editingConsumerSpec ? null : 'is-danger'"
                       >
                <b-input v-model="editingConsumerSpec">
                </b-input>
              </b-field>

              <b-field label="DB Key">
                <b-input v-model="editingConsumerDBKey">
                </b-input>
              </b-field>

            </b-field>

            <b-field grouped>

              <b-field label="Loop Delay">
                <b-input v-model="editingConsumerDelay"
                         style="width: 8rem;">
                </b-input>
              </b-field>

              <b-field label="Attempts">
                <b-input v-model="editingConsumerRetryAttempts"
                         style="width: 8rem;">
                </b-input>
              </b-field>

              <b-field label="Retry Delay">
                <b-input v-model="editingConsumerRetryDelay"
                         style="width: 8rem;">
                </b-input>
              </b-field>

            </b-field>

            <b-field grouped>

              <b-button @click="editingConsumer = null"
                        class="control">
                Cancel
              </b-button>

              <b-button type="is-primary"
                        @click="updateConsumer()"
                        :disabled="updateConsumerDisabled"
                        class="control">
                Update Consumer
              </b-button>

              <b-field label="Enabled" horizontal
                       style="margin-left: 2rem;">
                <b-checkbox v-model="editingConsumerEnabled">
                  {{ editingConsumerEnabled ? "Yes" : "No" }}
                </b-checkbox>
              </b-field>

            </b-field>
          </div>
        </div>

        <br />
        <b-field grouped>

          <b-button @click="editProfileShowDialog = false"
                    class="control">
            Cancel
          </b-button>

          <b-button type="is-primary"
                    class="control"
                    @click="updateProfile()"
                    :disabled="updateProfileDisabled">
            Update Profile
          </b-button>

          <b-field label="Enabled" horizontal
                   style="margin-left: 2rem;">
            <b-checkbox v-model="editingProfileEnabled">
              {{ editingProfileEnabled ? "Yes" : "No" }}
            </b-checkbox>
          </b-field>

        </b-field>

      </div>
    </div>
  </b-modal>

  <br />

  <h3 class="is-size-3">Misc.</h3>

  <b-field label="Supervisor Process Name"
           message="This should be the complete name, including group - e.g. poser:poser_datasync"
           expanded>
    <b-input name="rattail.datasync.supervisor_process_name"
             v-model="simpleSettings['rattail.datasync.supervisor_process_name']"
             @input="settingsNeedSaved = true"
             expanded>
    </b-input>
  </b-field>

  <b-field label="Consumer Batch Size"
           message="Max number of changes to be consumed at once."
           expanded>
    <numeric-input name="rattail.datasync.batch_size_limit"
                   v-model="simpleSettings['rattail.datasync.batch_size_limit']"
                   @input="settingsNeedSaved = true" />
  </b-field>

  <h3 class="is-size-3">Legacy</h3>
  <b-field label="Restart Command"
           message="This will run as '${system_user}' system user - please configure sudoers as needed.  Typical command is like:  sudo supervisorctl restart poser:poser_datasync"
           expanded>
    <b-input name="tailbone.datasync.restart"
             v-model="simpleSettings['tailbone.datasync.restart']"
             @input="settingsNeedSaved = true"
             expanded>
    </b-input>
  </b-field>

</%def>

<%def name="modify_vue_vars()">
  ${parent.modify_vue_vars()}
  <script>

    ThisPageData.showConfigFilesNote = false
    ThisPageData.profilesData = ${json.dumps(profiles_data)|n}
    ThisPageData.showDisabledProfiles = false

    ThisPageData.editProfileShowDialog = false
    ThisPageData.editingProfile = null
    ThisPageData.editingProfileKey = null
    ThisPageData.editingProfileWatcherSpec = null
    ThisPageData.editingProfileWatcherDBKey = null
    ThisPageData.editingProfileWatcherDelay = 1
    ThisPageData.editingProfileWatcherRetryAttempts = 1
    ThisPageData.editingProfileWatcherRetryDelay = 1
    ThisPageData.editingProfileWatcherDefaultRunas = null
    ThisPageData.editingProfileWatcherConsumesSelf = false
    ThisPageData.editingProfilePendingConsumers = []
    ThisPageData.editingProfileEnabled = true

    ThisPageData.editingConsumer = null
    ThisPageData.editingConsumerKey = null
    ThisPageData.editingConsumerSpec = null
    ThisPageData.editingConsumerDBKey = null
    ThisPageData.editingConsumerDelay = 1
    ThisPageData.editingConsumerRetryAttempts = 1
    ThisPageData.editingConsumerRetryDelay = 1
    ThisPageData.editingConsumerRunas = null
    ThisPageData.editingConsumerEnabled = true

    ThisPage.computed.updateConsumerDisabled = function() {
        if (!this.editingConsumerKey) {
            return true
        }
        if (!this.editingConsumerSpec) {
            return true
        }
        return false
    }

    ThisPage.computed.updateProfileDisabled = function() {
        if (this.editingConsumer) {
            return true
        }
        if (!this.editingProfileKey) {
            return true
        }
        if (!this.editingProfileWatcherSpec) {
            return true
        }
        return false
    }

    ThisPage.methods.toggleDisabledProfiles = function() {
        this.showDisabledProfiles = !this.showDisabledProfiles
    }

    ThisPage.methods.getWatcherRowClass = function(row, i) {
        if (!row.enabled) {
            if (!this.showDisabledProfiles) {
                return 'invisible-watcher'
            }
            return 'has-background-warning'
        }
    }

    ThisPage.methods.consumerShortList = function(row) {
        let keys = []
        if (row.watcher_consumes_self) {
            keys.push('self (watcher)')
        } else {
            for (let consumer of row.consumers_data) {
                if (consumer.enabled) {
                    keys.push(consumer.key)
                }
            }
        }
        return keys.join(', ')
    }

    ThisPage.methods.newProfile = function() {
        this.editingProfile = {watcher_kwargs_data: []}
        this.editingConsumer = null
        this.editingWatcherKwargs = false

        this.editingProfileKey = null
        this.editingProfileWatcherSpec = null
        this.editingProfileWatcherDBKey = null
        this.editingProfileWatcherDelay = 1
        this.editingProfileWatcherRetryAttempts = 1
        this.editingProfileWatcherRetryDelay = 1
        this.editingProfileWatcherDefaultRunas = null
        this.editingProfileWatcherConsumesSelf = false
        this.editingProfileEnabled = true
        this.editingProfilePendingConsumers = []
        this.editingProfilePendingWatcherKwargs = []

        this.editProfileShowDialog = true
        this.$nextTick(() => {
            this.$refs.watcherKeyInput.focus()
        })
    }

    ThisPage.methods.editProfile = function(row) {
        this.editingProfile = row
        this.editingConsumer = null
        this.editingWatcherKwargs = false

        this.editingProfileKey = row.key
        this.editingProfileWatcherSpec = row.watcher_spec
        this.editingProfileWatcherDBKey = row.watcher_dbkey
        this.editingProfileWatcherDelay = row.watcher_delay
        this.editingProfileWatcherRetryAttempts = row.watcher_retry_attempts
        this.editingProfileWatcherRetryDelay = row.watcher_retry_delay
        this.editingProfileWatcherDefaultRunas = row.watcher_default_runas
        this.editingProfileWatcherConsumesSelf = row.watcher_consumes_self
        this.editingProfileEnabled = row.enabled

        this.editingProfilePendingWatcherKwargs = []
        for (let kwarg of row.watcher_kwargs_data) {
            let pending = {
                original_key: kwarg.key,
                key: kwarg.key,
                value: kwarg.value,
            }
            this.editingProfilePendingWatcherKwargs.push(pending)
        }

        this.editingProfilePendingConsumers = []
        for (let consumer of row.consumers_data) {
            const pending = {
                ...consumer,
                original_key: consumer.key,
            }
            this.editingProfilePendingConsumers.push(pending)
        }

        this.editProfileShowDialog = true
    }

    ThisPageData.editingWatcherKwargs = false
    ThisPageData.editingProfilePendingWatcherKwargs = []
    ThisPageData.editingWatcherKwarg = null
    ThisPageData.editingWatcherKwargKey = null
    ThisPageData.editingWatcherKwargValue = null

    ThisPage.methods.newWatcherKwarg = function() {
        this.editingWatcherKwargKey = null
        this.editingWatcherKwargValue = null
        this.editingWatcherKwarg = {key: null, value: null}
        this.$nextTick(() => {
            this.$refs.watcherKwargKey.focus()
        })
    }

    ThisPage.methods.editProfileWatcherKwarg = function(row) {
        this.editingWatcherKwargKey = row.key
        this.editingWatcherKwargValue = row.value
        this.editingWatcherKwarg = row
    }

    ThisPage.methods.updateWatcherKwarg = function() {
        let pending = this.editingWatcherKwarg
        let isNew = !pending.key

        pending.key = this.editingWatcherKwargKey
        pending.value = this.editingWatcherKwargValue

        if (isNew) {
            this.editingProfilePendingWatcherKwargs.push(pending)
        }

        this.editingWatcherKwarg = null
    }

    ThisPage.methods.deleteProfileWatcherKwarg = function(row) {
        let i = this.editingProfilePendingWatcherKwargs.indexOf(row)
        this.editingProfilePendingWatcherKwargs.splice(i, 1)
    }

    ThisPage.methods.findConsumer = function(profileConsumers, key) {
        for (const consumer of profileConsumers) {
            if (consumer.key == key) {
                return consumer
            }
        }
    }

    ThisPage.methods.updateProfile = function() {
        const row = this.editingProfile

        const newRow = !row.key
        let originalProfile = null
        if (newRow) {
            row.consumers_data = []
            this.profilesData.push(row)
        } else {
            originalProfile = this.findProfile(row)
        }

        row.key = this.editingProfileKey
        row.watcher_spec = this.editingProfileWatcherSpec
        row.watcher_dbkey = this.editingProfileWatcherDBKey
        row.watcher_delay = this.editingProfileWatcherDelay
        row.watcher_retry_attempts = this.editingProfileWatcherRetryAttempts
        row.watcher_retry_delay = this.editingProfileWatcherRetryDelay
        row.watcher_default_runas = this.editingProfileWatcherDefaultRunas
        row.watcher_consumes_self = this.editingProfileWatcherConsumesSelf
        row.enabled = this.editingProfileEnabled

        // track which keys still belong (persistent)
        let persistentWatcherKwargs = []

        // transfer pending data to profile watcher kwargs
        for (let pending of this.editingProfilePendingWatcherKwargs) {
            persistentWatcherKwargs.push(pending.key)
            if (pending.original_key) {
                let kwarg = this.findOriginalWatcherKwarg(pending.original_key)
                kwarg.key = pending.key
                kwarg.value = pending.value
            } else {
                row.watcher_kwargs_data.push(pending)
            }
        }

        // remove any kwargs not being persisted
        let removeWatcherKwargs = []
        for (let kwarg of row.watcher_kwargs_data) {
            let i = persistentWatcherKwargs.indexOf(kwarg.key)
            if (i < 0) {
                removeWatcherKwargs.push(kwarg)
            }
        }
        for (let kwarg of removeWatcherKwargs) {
            let i = row.watcher_kwargs_data.indexOf(kwarg)
            row.watcher_kwargs_data.splice(i, 1)
        }

        // track which keys still belong (persistent)
        let persistentConsumers = []

        // transfer pending data to profile consumers
        for (let pending of this.editingProfilePendingConsumers) {
            persistentConsumers.push(pending.key)
            if (pending.original_key) {
                const consumer = this.findConsumer(originalProfile.consumers_data,
                                                   pending.original_key)
                consumer.key = pending.key
                consumer.consumer_spec = pending.consumer_spec
                consumer.consumer_dbkey = pending.consumer_dbkey
                consumer.consumer_delay = pending.consumer_delay
                consumer.consumer_retry_attempts = pending.consumer_retry_attempts
                consumer.consumer_retry_delay = pending.consumer_retry_delay
                consumer.consumer_runas = pending.consumer_runas
                consumer.enabled = pending.enabled
            } else {
                row.consumers_data.push(pending)
            }
        }

        // remove any consumers not being persisted
        let removeConsumers = []
        for (let consumer of row.consumers_data) {
            let i = persistentConsumers.indexOf(consumer.key)
            if (i < 0) {
                removeConsumers.push(consumer)
            }
        }
        for (let consumer of removeConsumers) {
            let i = row.consumers_data.indexOf(consumer)
            row.consumers_data.splice(i, 1)
        }

        if (!newRow) {

            // nb. must explicitly update the original data row;
            // otherwise (with vue3) it will remain stale and
            // submitting the form will keep same settings!
            // TODO: this probably means i am doing something
            // sloppy, but at least this hack fixes for now.
            const profile = this.findProfile(row)
            for (const key of Object.keys(row)) {
                profile[key] = row[key]
            }
        }

        this.settingsNeedSaved = true
        this.editProfileShowDialog = false
    }

    ThisPage.methods.findProfile = function(row) {
        for (const profile of this.profilesData) {
            if (profile.key == row.key) {
                return profile
            }
        }
    }

    ThisPage.methods.deleteProfile = function(row) {
        if (confirm("Are you sure you want to delete the '" + row.key + "' profile?")) {
            let i = this.profilesData.indexOf(row)
            this.profilesData.splice(i, 1)
            this.settingsNeedSaved = true
        }
    }

    ThisPage.methods.newConsumer = function() {
        this.editingConsumerKey = null
        this.editingConsumerSpec = null
        this.editingConsumerDBKey = null
        this.editingConsumerDelay = 1
        this.editingConsumerRetryAttempts = 1
        this.editingConsumerRetryDelay = 1
        this.editingConsumerRunas = null
        this.editingConsumerEnabled = true
        this.editingConsumer = {}
        this.$nextTick(() => {
            this.$refs.consumerKeyInput.focus()
        })
    }

    ThisPage.methods.editProfileConsumer = function(row) {
        this.editingConsumerKey = row.key
        this.editingConsumerSpec = row.consumer_spec
        this.editingConsumerDBKey = row.consumer_dbkey
        this.editingConsumerDelay = row.consumer_delay
        this.editingConsumerRetryAttempts = row.consumer_retry_attempts
        this.editingConsumerRetryDelay = row.consumer_retry_delay
        this.editingConsumerRunas = row.consumer_runas
        this.editingConsumerEnabled = row.enabled
        this.editingConsumer = row
    }

    ThisPage.methods.updateConsumer = function() {
        const pending = this.findConsumer(
            this.editingProfilePendingConsumers,
            this.editingConsumer.key)
        const isNew = !pending.key

        pending.key = this.editingConsumerKey
        pending.consumer_spec = this.editingConsumerSpec
        pending.consumer_dbkey = this.editingConsumerDBKey
        pending.consumer_delay = this.editingConsumerDelay
        pending.consumer_retry_attempts = this.editingConsumerRetryAttempts
        pending.consumer_retry_delay = this.editingConsumerRetryDelay
        pending.consumer_runas = this.editingConsumerRunas
        pending.enabled = this.editingConsumerEnabled

        if (isNew) {
            this.editingProfilePendingConsumers.push(pending)
        }
        this.editingConsumer = null
    }

    ThisPage.methods.deleteProfileConsumer = function(row) {
        if (confirm("Are you sure you want to delete the '" + row.key + "' consumer?")) {
            let i = this.editingProfilePendingConsumers.indexOf(row)
            this.editingProfilePendingConsumers.splice(i, 1)
        }
    }

    % if request.has_perm('datasync.restart'):
        ThisPageData.restartingDatasync = false
        ThisPageData.restartDatasyncFormButtonText = "Restart Datasync"
        ThisPage.methods.restartDatasync = function(e) {
            if (this.settingsNeedSaved) {
                alert("You have unsaved changes.  Please save or undo them first.")
                e.preventDefault()
            }
        }
        ThisPage.methods.submitRestartDatasyncForm = function() {
            this.restartingDatasync = true
            this.restartDatasyncFormButtonText = "Restarting Datasync..."
        }
    % endif

  </script>
</%def>
