## -*- coding: utf-8; -*-
<%inherit file="/page.mako" />

<%def name="title()">View / Launch Tasks</%def>

<%def name="page_content()">
  <br />
  <div class="form">

    <div class="buttons">

      <b-button tag="a"
                % if luigi_url:
                href="${luigi_url}"
                % else:
                href="#" disabled
                title="Luigi URL is not configured"
                % endif
                icon-pack="fas"
                icon-left="external-link-alt"
                target="_blank">
        Luigi Task Visualiser
      </b-button>

      <b-button tag="a"
                % if luigi_history_url:
                href="${luigi_history_url}"
                % else:
                href="#" disabled
                title="Luigi URL is not configured"
                % endif
                icon-pack="fas"
                icon-left="external-link-alt"
                target="_blank">
        Luigi Task History
      </b-button>

      % if master.has_perm('restart_scheduler'):
          ${h.form(url('{}.restart_scheduler'.format(route_prefix)), **{'@submit': 'submitRestartSchedulerForm'})}
          ${h.csrf_token(request)}
          <b-button type="is-primary"
                    native-type="submit"
                    icon-pack="fas"
                    icon-left="redo"
                    :disabled="restartSchedulerFormSubmitting">
            {{ restartSchedulerFormSubmitting ? "Working, please wait..." : "Restart Luigi Scheduler" }}
          </b-button>
          ${h.end_form()}
      % endif
    </div>

    % if master.has_perm('launch_overnight'):

        <h3 class="block is-size-3">Overnight Tasks</h3>

        <${b}-table :data="overnightTasks" hoverable>
          <${b}-table-column field="description"
                          label="Description"
                          v-slot="props">
            {{ props.row.description }}
          </${b}-table-column>
          <${b}-table-column field="script"
                          label="Command"
                          v-slot="props">
            {{ props.row.script || props.row.class_name }}
          </${b}-table-column>
          <${b}-table-column field="last_date"
                          label="Last Date"
                          v-slot="props">
            <span :class="overnightTextClass(props.row)">
              {{ props.row.last_date || "never!" }}
            </span>
          </${b}-table-column>
          <${b}-table-column label="Actions"
                          v-slot="props">
            <b-button type="is-primary"
                      icon-pack="fas"
                      icon-left="arrow-circle-right"
                      @click="overnightTaskLaunchInit(props.row)">
              Launch
            </b-button>
            <${b}-modal has-modal-card
                        % if request.use_oruga:
                            v-model:active="overnightTaskShowLaunchDialog"
                        % else:
                            :active.sync="overnightTaskShowLaunchDialog"
                        % endif
                        >
              <div class="modal-card">

                <header class="modal-card-head">
                  <p class="modal-card-title">Launch Overnight Task</p>
                </header>

                <section class="modal-card-body"
                         v-if="overnightTask">

                  <b-field label="Task" horizontal>
                    <span>{{ overnightTask.description }}</span>
                  </b-field>

                  <b-field label="Last Date" horizontal>
                    <span :class="overnightTextClass(overnightTask)">
                      {{ overnightTask.last_date || "n/a" }}
                    </span>
                  </b-field>

                  <b-field label="Next Date" horizontal>
                    <span>
                      ${rattail_app.render_date(rattail_app.yesterday())} (yesterday)
                    </span>
                  </b-field>

                  <p class="block">
                    Launching this task will schedule it to begin
                    within one minute.&nbsp; See the Luigi Task
                    Visualizer after that, for current status.
                  </p>

                </section>

                <footer class="modal-card-foot">
                  <b-button @click="overnightTaskShowLaunchDialog = false">
                    Cancel
                  </b-button>
                  <b-button type="is-primary"
                            icon-pack="fas"
                            icon-left="arrow-circle-right"
                            @click="overnightTaskLaunchSubmit()"
                            :disabled="overnightTaskLaunching">
                    {{ overnightTaskLaunching ? "Working, please wait..." : "Launch" }}
                  </b-button>
                </footer>
              </div>
            </${b}-modal>
          </${b}-table-column>
          <template #empty>
            <p class="block">No tasks defined.</p>
          </template>
        </${b}-table>

    % endif

    % if master.has_perm('launch_backfill'):

        <h3 class="block is-size-3">Backfill Tasks</h3>

        <${b}-table :data="backfillTasks" hoverable>
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
          <${b}-table-column field="last_date"
                          label="Last Date"
                          v-slot="props">
            <span :class="backfillTextClass(props.row)">
              {{ props.row.last_date }}
            </span>
          </${b}-table-column>
          <${b}-table-column field="target_date"
                          label="Target Date"
                          v-slot="props">
            {{ props.row.target_date }}
          </${b}-table-column>
          <${b}-table-column label="Actions"
                          v-slot="props">
            <b-button type="is-primary"
                      icon-pack="fas"
                      icon-left="arrow-circle-right"
                      @click="backfillTaskLaunch(props.row)">
              Launch
            </b-button>
          </${b}-table-column>
          <template #empty>
            <p class="block">No tasks defined.</p>
          </template>
        </${b}-table>

        <${b}-modal has-modal-card
                    % if request.use_oruga:
                        v-model:active="backfillTaskShowLaunchDialog"
                    % else:
                        :active.sync="backfillTaskShowLaunchDialog"
                    % endif
                    >
          <div class="modal-card">

            <header class="modal-card-head">
              <p class="modal-card-title">Launch Backfill Task</p>
            </header>

            <section class="modal-card-body"
                     v-if="backfillTask">

              <p class="block has-text-weight-bold">
                {{ backfillTask.description }}
                (goes {{ backfillTask.forward ? "FORWARD" : "BACKWARD" }})
              </p>

              <b-field grouped>
                <b-field label="Last Date">
                  {{ backfillTask.last_date || "n/a" }}
                </b-field>
                <b-field label="Target Date">
                  {{ backfillTask.target_date || "n/a" }}
                </b-field>
              </b-field>

              <b-field grouped>

                <b-field label="Start Date"
                         :type="backfillTaskStartDate ? null : 'is-danger'">
                  <tailbone-datepicker v-model="backfillTaskStartDate">
                  </tailbone-datepicker>
                </b-field>

                <b-field label="End Date"
                         :type="backfillTaskEndDate ? null : 'is-danger'">
                  <tailbone-datepicker v-model="backfillTaskEndDate">
                  </tailbone-datepicker>
                </b-field>

              </b-field>

            </section>

            <footer class="modal-card-foot">
              <b-button @click="backfillTaskShowLaunchDialog = false">
                Cancel
              </b-button>
              <b-button type="is-primary"
                        icon-pack="fas"
                        icon-left="arrow-circle-right"
                        @click="backfillTaskLaunchSubmit()"
                        :disabled="backfillTaskLaunching || !backfillTaskStartDate || !backfillTaskEndDate">
                {{ backfillTaskLaunching ? "Working, please wait..." : "Launch" }}
              </b-button>
            </footer>
          </div>
        </${b}-modal>

    % endif

  </div>
</%def>

<%def name="modify_vue_vars()">
  ${parent.modify_vue_vars()}
  <script>

    % if master.has_perm('restart_scheduler'):

        ThisPageData.restartSchedulerFormSubmitting = false

        ThisPage.methods.submitRestartSchedulerForm = function() {
            this.restartSchedulerFormSubmitting = true
        }

    % endif

    % if master.has_perm('launch_overnight'):

        ThisPageData.overnightTasks = ${json.dumps(overnight_tasks)|n}
        ThisPageData.overnightTask = null
        ThisPageData.overnightTaskShowLaunchDialog = false
        ThisPageData.overnightTaskLaunching = false

        ThisPage.methods.overnightTextClass = function(task) {
            let yesterday = '${rattail_app.today() - datetime.timedelta(days=1)}'
            if (task.last_date) {
                if (task.last_date == yesterday) {
                    return 'has-text-success'
                } else {
                    return 'has-text-warning'
                }
            } else {
                return 'has-text-warning'
            }
        }

        ThisPage.methods.overnightTaskLaunchInit = function(task) {
            this.overnightTask = task
            this.overnightTaskShowLaunchDialog = true
        }

        ThisPage.methods.overnightTaskLaunchSubmit = function() {
            this.overnightTaskLaunching = true

            let url = '${url('{}.launch_overnight'.format(route_prefix))}'
            let params = {key: this.overnightTask.key}

            this.submitForm(url, params, response => {
                this.$buefy.toast.open({
                    message: "Task has been scheduled for immediate launch!",
                    type: 'is-success',
                    duration: 5000, // 5 seconds
                })
                this.overnightTaskLaunching = false
                this.overnightTaskShowLaunchDialog = false
            })
        }

    % endif

    % if master.has_perm('launch_backfill'):

        ThisPageData.backfillTasks = ${json.dumps(backfill_tasks)|n}
        ThisPageData.backfillTask = null
        ThisPageData.backfillTaskStartDate = null
        ThisPageData.backfillTaskEndDate = null
        ThisPageData.backfillTaskShowLaunchDialog = false
        ThisPageData.backfillTaskLaunching = false

        ThisPage.methods.backfillTextClass = function(task) {
            if (task.target_date) {
                if (task.last_date) {
                    if (task.forward) {
                        if (task.last_date >= task.target_date) {
                            return 'has-text-success'
                        } else {
                            return 'has-text-warning'
                        }
                    } else {
                        if (task.last_date <= task.target_date) {
                            return 'has-text-success'
                        } else {
                            return 'has-text-warning'
                        }
                    }
                }
            }
        }

        ThisPage.methods.backfillTaskLaunch = function(task) {
            this.backfillTask = task
            this.backfillTaskStartDate = null
            this.backfillTaskEndDate = null
            this.backfillTaskShowLaunchDialog = true
        }

        ThisPage.methods.backfillTaskLaunchSubmit = function() {
            this.backfillTaskLaunching = true

            let url = '${url('{}.launch_backfill'.format(route_prefix))}'
            let params = {
                key: this.backfillTask.key,
                start_date: this.backfillTaskStartDate,
                end_date: this.backfillTaskEndDate,
            }

            this.submitForm(url, params, response => {
                this.$buefy.toast.open({
                    message: "Task has been scheduled for immediate launch!",
                    type: 'is-success',
                    duration: 5000, // 5 seconds
                })
                this.backfillTaskLaunching = false
                this.backfillTaskShowLaunchDialog = false
            })
        }

    % endif

  </script>
</%def>
