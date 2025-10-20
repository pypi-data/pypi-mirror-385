## -*- coding: utf-8; -*-
<%inherit file="/page.mako" />

<%def name="title()">${index_title}</%def>

<%def name="content_title()"></%def>

<%def name="page_content()">
  % if expose_websockets and not supervisor_error:
      <b-notification type="is-warning"
                      :active="websocketBroken"
                      :closable="false">
        Server connection was broken - please refresh page to see accurate status!
      </b-notification>
  % endif
  <b-field label="Supervisor Status">
    <div style="display: flex;">

      % if supervisor_error:
          <pre class="has-background-warning">${supervisor_error}</pre>
      % else:
          <pre :class="(processInfo && processInfo.statename == 'RUNNING') ? 'has-background-success' : 'has-background-warning'">{{ processDescription }}</pre>
      % endif

      <div style="margin-left: 1rem;">
        % if request.has_perm('datasync.restart'):
            ${h.form(url('datasync.restart'), **{'@submit': 'restartProcess'})}
            ${h.csrf_token(request)}
            <b-button type="is-primary"
                      native-type="submit"
                      icon-pack="fas"
                      icon-left="redo"
                      :disabled="restartingProcess">
              {{ restartingProcess ? "Working, please wait..." : "Restart Process" }}
            </b-button>
            ${h.end_form()}
        % endif
      </div>

    </div>
  </b-field>

  <h3 class="is-size-3">Watcher Status</h3>

    <${b}-table :data="watchers">
      <${b}-table-column field="key"
                      label="Watcher"
                      v-slot="props">
         {{ props.row.key }}
      </${b}-table-column>
      <${b}-table-column field="spec"
                      label="Spec"
                      v-slot="props">
         {{ props.row.spec }}
      </${b}-table-column>
      <${b}-table-column field="dbkey"
                      label="DB Key"
                      v-slot="props">
         {{ props.row.dbkey }}
      </${b}-table-column>
      <${b}-table-column field="delay"
                      label="Delay"
                      v-slot="props">
         {{ props.row.delay }} second(s)
      </${b}-table-column>
      <${b}-table-column field="lastrun"
                      label="Last Watched"
                      v-slot="props">
         <span v-html="props.row.lastrun"></span>
      </${b}-table-column>
      <${b}-table-column field="status"
                      label="Status"
                      v-slot="props">
        <span :class="props.row.status == 'okay' ? 'has-background-success' : 'has-background-warning'">
          {{ props.row.status }}
        </span>
      </${b}-table-column>
    </${b}-table>

  <h3 class="is-size-3">Consumer Status</h3>

    <${b}-table :data="consumers">
      <${b}-table-column field="key"
                      label="Consumer"
                      v-slot="props">
         {{ props.row.key }}
      </${b}-table-column>
      <${b}-table-column field="spec"
                      label="Spec"
                      v-slot="props">
         {{ props.row.spec }}
      </${b}-table-column>
      <${b}-table-column field="dbkey"
                      label="DB Key"
                      v-slot="props">
         {{ props.row.dbkey }}
      </${b}-table-column>
      <${b}-table-column field="delay"
                      label="Delay"
                      v-slot="props">
         {{ props.row.delay }} second(s)
      </${b}-table-column>
      <${b}-table-column field="changes"
                      label="Pending Changes"
                      v-slot="props">
         {{ props.row.changes }}
      </${b}-table-column>
      <${b}-table-column field="status"
                      label="Status"
                      v-slot="props">
        <span :class="props.row.status == 'okay' ? 'has-background-success' : 'has-background-warning'">
          {{ props.row.status }}
        </span>
      </${b}-table-column>
    </${b}-table>
</%def>

<%def name="modify_vue_vars()">
  ${parent.modify_vue_vars()}
  <script>

    ThisPageData.processInfo = ${json.dumps(process_info)|n}

    ThisPage.computed.processDescription = function() {
        let info = this.processInfo
        if (info) {
            return `${'$'}{info.group}:${'$'}{info.name}    ${'$'}{info.statename}    ${'$'}{info.description}`
        } else {
            return "NO PROCESS INFO AVAILABLE"
        }
    }

    ThisPageData.restartingProcess = false
    ThisPageData.watchers = ${json.dumps(watcher_data)|n}
    ThisPageData.consumers = ${json.dumps(consumer_data)|n}

    ThisPage.methods.restartProcess = function() {
        this.restartingProcess = true
    }

    % if expose_websockets and not supervisor_error:

        ThisPageData.ws = null
        ThisPageData.websocketBroken = false

        ThisPage.mounted = function() {

            ## TODO: should be a cleaner way to get this url?
            let url = '${url('ws.datasync.status')}'
            url = url.replace(/^http(s?):/, 'ws$1:')

            this.ws = new WebSocket(url)
            let that = this

            this.ws.onclose = (event) => {
                // websocket closing means 1 of 2 things:
                // - user navigated away from page intentionally
                // - server connection was broken somehow
                // only one of those is "bad" and we only want to
                // display warning in 2nd case.  so we simply use a
                // brief delay to "rule out" the 1st scenario
                setTimeout(() => { that.websocketBroken = true },
                           3000)
            }

            this.ws.onmessage = (event) => {
                that.processInfo = JSON.parse(event.data)
            }
        }

    % endif

  </script>
</%def>
