## -*- coding: utf-8; -*-
<%inherit file="/configure.mako" />

<%def name="form_content()">
  ${h.hidden('overnight_tasks', **{':value': 'JSON.stringify(overnightTasks)'})}
  ${h.hidden('backfill_tasks', **{':value': 'JSON.stringify(backfillTasks)'})}

  <div class="level">
    <div class="level-left">
      <div class="level-item">
        <h3 class="is-size-3">Overnight Tasks</h3>
      </div>
      <div class="level-item">
        <b-button type="is-primary"
                  icon-pack="fas"
                  icon-left="plus"
                  @click="overnightTaskCreate()">
          New Task
        </b-button>
      </div>
    </div>
  </div>
  <div class="block" style="padding-left: 2rem; display: flex;">

    <${b}-table :data="overnightTasks">
      <!-- <${b}-table-column field="key" -->
      <!--                 label="Key" -->
      <!--                 sortable> -->
      <!--   {{ props.row.key }} -->
      <!-- </${b}-table-column> -->
      <${b}-table-column field="key"
                      label="Key"
                      v-slot="props">
        {{ props.row.key }}
      </${b}-table-column>
      <${b}-table-column field="description"
                      label="Description"
                      v-slot="props">
        {{ props.row.description }}
      </${b}-table-column>
      <${b}-table-column field="class_name"
                      label="Class Name"
                      v-slot="props">
        {{ props.row.class_name }}
      </${b}-table-column>
      <${b}-table-column field="script"
                      label="Script"
                      v-slot="props">
        {{ props.row.script }}
      </${b}-table-column>
      <${b}-table-column label="Actions"
                      v-slot="props">
        <a href="#"
           @click.prevent="overnightTaskEdit(props.row)">
          % if request.use_oruga:
              <o-icon icon="edit" />
          % else:
              <i class="fas fa-edit"></i>
          % endif
          Edit
        </a>
        &nbsp;
        <a href="#"
           class="has-text-danger"
           @click.prevent="overnightTaskDelete(props.row)">
          % if request.use_oruga:
              <o-icon icon="trash" />
          % else:
              <i class="fas fa-trash"></i>
          % endif
          Delete
        </a>
      </${b}-table-column>
    </${b}-table>

    <b-modal has-modal-card
             :active.sync="overnightTaskShowDialog">
      <div class="modal-card">

        <header class="modal-card-head">
          <p class="modal-card-title">Overnight Task</p>
        </header>

        <section class="modal-card-body">
          <b-field label="Key"
                   :type="overnightTaskKey ? null : 'is-danger'">
            <b-input v-model.trim="overnightTaskKey"
                     ref="overnightTaskKey"
                     expanded />
          </b-field>
          <b-field label="Description"
                   :type="overnightTaskDescription ? null : 'is-danger'">
            <b-input v-model.trim="overnightTaskDescription"
                     ref="overnightTaskDescription"
                     expanded />
          </b-field>
          <b-field label="Module">
            <b-input v-model.trim="overnightTaskModule"
                     expanded />
          </b-field>
          <b-field label="Class Name">
            <b-input v-model.trim="overnightTaskClass"
                     expanded />
          </b-field>
          <b-field label="Script">
            <b-input v-model.trim="overnightTaskScript"
                     expanded />
          </b-field>
          <b-field label="Notes">
            <b-input v-model.trim="overnightTaskNotes"
                     type="textarea"
                     expanded />
          </b-field>
        </section>

        <footer class="modal-card-foot">
          <b-button type="is-primary"
                    icon-pack="fas"
                    icon-left="save"
                    @click="overnightTaskSave()"
                    :disabled="!overnightTaskKey || !overnightTaskDescription">
            Save
          </b-button>
          <b-button @click="overnightTaskShowDialog = false">
            Cancel
          </b-button>
        </footer>
      </div>
    </b-modal>

  </div>

  <div class="level">
    <div class="level-left">
      <div class="level-item">
        <h3 class="is-size-3">Backfill Tasks</h3>
      </div>
      <div class="level-item">
        <b-button type="is-primary"
                  icon-pack="fas"
                  icon-left="plus"
                  @click="backfillTaskCreate()">
          New Task
        </b-button>
      </div>
    </div>
  </div>
  <div class="block" style="padding-left: 2rem; display: flex;">

    <${b}-table :data="backfillTasks">
      <${b}-table-column field="key"
                      label="Key"
                      v-slot="props">
        {{ props.row.key }}
      </${b}-table-column>
      <${b}-table-column field="description"
                      label="Description"
                      v-slot="props">
        {{ props.row.description }}
      </${b}-table-column>
      <${b}-table-column field="script"
                      label="Script"
                      v-slot="props">
        {{ props.row.script }}
      </${b}-table-column>
      <${b}-table-column field="forward"
                      label="Orientation"
                      v-slot="props">
        {{ props.row.forward ? "Forward" : "Backward" }}
      </${b}-table-column>
      <${b}-table-column field="target_date"
                      label="Target Date"
                      v-slot="props">
        {{ props.row.target_date }}
      </${b}-table-column>
      <${b}-table-column label="Actions"
                      v-slot="props">
        <a href="#"
           @click.prevent="backfillTaskEdit(props.row)">
          % if request.use_oruga:
              <o-icon icon="edit" />
          % else:
              <i class="fas fa-edit"></i>
          % endif
          Edit
        </a>
        &nbsp;
        <a href="#"
           class="has-text-danger"
           @click.prevent="backfillTaskDelete(props.row)">
          % if request.use_oruga:
              <o-icon icon="trash" />
          % else:
              <i class="fas fa-trash"></i>
          % endif
          Delete
        </a>
      </${b}-table-column>
    </${b}-table>

    <b-modal has-modal-card
             :active.sync="backfillTaskShowDialog">
      <div class="modal-card">

        <header class="modal-card-head">
          <p class="modal-card-title">Backfill Task</p>
        </header>

        <section class="modal-card-body">
          <b-field label="Key"
                   :type="backfillTaskKey ? null : 'is-danger'">
            <b-input v-model.trim="backfillTaskKey"
                     ref="backfillTaskKey"
                     expanded />
          </b-field>
          <b-field label="Description"
                   :type="backfillTaskDescription ? null : 'is-danger'">
            <b-input v-model.trim="backfillTaskDescription"
                     ref="backfillTaskDescription"
                     expanded />
          </b-field>
          <b-field label="Script"
                   :type="backfillTaskScript ? null : 'is-danger'">
            <b-input v-model.trim="backfillTaskScript"
                     expanded />
          </b-field>
          <b-field grouped>
            <b-field label="Orientation">
              <b-select v-model="backfillTaskForward">
                <option :value="false">Backward</option>
                <option :value="true">Forward</option>
              </b-select>
            </b-field>
            <b-field label="Target Date">
              <tailbone-datepicker v-model="backfillTaskTargetDate">
              </tailbone-datepicker>
            </b-field>
          </b-field>
          <b-field label="Notes">
            <b-input v-model.trim="backfillTaskNotes"
                     type="textarea"
                     expanded />
          </b-field>
        </section>

        <footer class="modal-card-foot">
          <b-button type="is-primary"
                    icon-pack="fas"
                    icon-left="save"
                    @click="backfillTaskSave()"
                    :disabled="!backfillTaskKey || !backfillTaskDescription || !backfillTaskScript">
            Save
          </b-button>
          <b-button @click="backfillTaskShowDialog = false">
            Cancel
          </b-button>
        </footer>
      </div>
    </b-modal>

  </div>

  <h3 class="is-size-3">Luigi Proper</h3>
  <div class="block" style="padding-left: 2rem;">

    <b-field label="Luigi URL"
             message="This should be the URL to Luigi Task Visualiser web user interface."
             expanded>
      <b-input name="rattail.luigi.url"
               v-model="simpleSettings['rattail.luigi.url']"
               @input="settingsNeedSaved = true"
               expanded>
      </b-input>
    </b-field>

    <b-field label="Supervisor Process Name"
             message="This should be the complete name, including group - e.g. luigi:luigid"
             expanded>
      <b-input name="rattail.luigi.scheduler.supervisor_process_name"
               v-model="simpleSettings['rattail.luigi.scheduler.supervisor_process_name']"
               @input="settingsNeedSaved = true"
               expanded>
      </b-input>
    </b-field>

    <b-field label="Restart Command"
             message="This will run as '${system_user}' system user - please configure sudoers as needed.  Typical command is like:  sudo supervisorctl restart luigi:luigid"
             expanded>
      <b-input name="rattail.luigi.scheduler.restart_command"
               v-model="simpleSettings['rattail.luigi.scheduler.restart_command']"
               @input="settingsNeedSaved = true"
               expanded>
      </b-input>
    </b-field>

  </div>

</%def>

<%def name="modify_vue_vars()">
  ${parent.modify_vue_vars()}
  <script>

    ThisPageData.overnightTasks = ${json.dumps(overnight_tasks)|n}
    ThisPageData.overnightTaskShowDialog = false
    ThisPageData.overnightTask = null
    ThisPageData.overnightTaskCounter = 0
    ThisPageData.overnightTaskKey = null
    ThisPageData.overnightTaskDescription = null
    ThisPageData.overnightTaskModule = null
    ThisPageData.overnightTaskClass = null
    ThisPageData.overnightTaskScript = null
    ThisPageData.overnightTaskNotes = null

    ThisPage.methods.overnightTaskCreate = function() {
        this.overnightTask = {key: null, isNew: true}
        this.overnightTaskKey = null
        this.overnightTaskDescription = null
        this.overnightTaskModule = null
        this.overnightTaskClass = null
        this.overnightTaskScript = null
        this.overnightTaskNotes = null
        this.overnightTaskShowDialog = true
        this.$nextTick(() => {
            this.$refs.overnightTaskKey.focus()
        })
    }

    ThisPage.methods.overnightTaskEdit = function(task) {
        this.overnightTask = task
        this.overnightTaskKey = task.key
        this.overnightTaskDescription = task.description
        this.overnightTaskModule = task.module
        this.overnightTaskClass = task.class_name
        this.overnightTaskScript = task.script
        this.overnightTaskNotes = task.notes
        this.overnightTaskShowDialog = true
    }

    ThisPage.methods.overnightTaskSave = function() {
        this.overnightTask.key = this.overnightTaskKey
        this.overnightTask.description = this.overnightTaskDescription
        this.overnightTask.module = this.overnightTaskModule
        this.overnightTask.class_name = this.overnightTaskClass
        this.overnightTask.script = this.overnightTaskScript
        this.overnightTask.notes = this.overnightTaskNotes

        if (this.overnightTask.isNew) {
            this.overnightTasks.push(this.overnightTask)
            this.overnightTask.isNew = false
        }

        this.overnightTaskShowDialog = false
        this.settingsNeedSaved = true
    }

    ThisPage.methods.overnightTaskDelete = function(task) {
        if (confirm("Really delete this task?")) {
            let i = this.overnightTasks.indexOf(task)
            this.overnightTasks.splice(i, 1)
            this.settingsNeedSaved = true
        }
    }

    ThisPageData.backfillTasks = ${json.dumps(backfill_tasks)|n}
    ThisPageData.backfillTaskShowDialog = false
    ThisPageData.backfillTask = null
    ThisPageData.backfillTaskCounter = 0
    ThisPageData.backfillTaskKey = null
    ThisPageData.backfillTaskDescription = null
    ThisPageData.backfillTaskScript = null
    ThisPageData.backfillTaskForward = false
    ThisPageData.backfillTaskTargetDate = null
    ThisPageData.backfillTaskNotes = null

    ThisPage.methods.backfillTaskCreate = function() {
        this.backfillTask = {key: null, isNew: true}
        this.backfillTaskKey = null
        this.backfillTaskDescription = null
        this.backfillTaskScript = null
        this.backfillTaskForward = false
        this.backfillTaskTargetDate = null
        this.backfillTaskNotes = null
        this.backfillTaskShowDialog = true
        this.$nextTick(() => {
            this.$refs.backfillTaskKey.focus()
        })
    }

    ThisPage.methods.backfillTaskEdit = function(task) {
        this.backfillTask = task
        this.backfillTaskKey = task.key
        this.backfillTaskDescription = task.description
        this.backfillTaskScript = task.script
        this.backfillTaskForward = task.forward
        this.backfillTaskTargetDate = task.target_date
        this.backfillTaskNotes = task.notes
        this.backfillTaskShowDialog = true
    }

    ThisPage.methods.backfillTaskDelete = function(task) {
        if (confirm("Really delete this task?")) {
            let i = this.backfillTasks.indexOf(task)
            this.backfillTasks.splice(i, 1)
            this.settingsNeedSaved = true
        }
    }

    ThisPage.methods.backfillTaskSave = function() {
        this.backfillTask.key = this.backfillTaskKey
        this.backfillTask.description = this.backfillTaskDescription
        this.backfillTask.script = this.backfillTaskScript
        this.backfillTask.forward = this.backfillTaskForward
        this.backfillTask.target_date = this.backfillTaskTargetDate
        this.backfillTask.notes = this.backfillTaskNotes

        if (this.backfillTask.isNew) {
            this.backfillTasks.push(this.backfillTask)
            this.backfillTask.isNew = false
        }

        this.backfillTaskShowDialog = false
        this.settingsNeedSaved = true
    }

  </script>
</%def>
