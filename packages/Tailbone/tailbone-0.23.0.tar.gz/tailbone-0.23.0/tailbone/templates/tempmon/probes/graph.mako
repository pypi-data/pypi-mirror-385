## -*- coding: utf-8; -*-
<%inherit file="/form.mako" />

<%def name="title()">Temperature Graph</%def>

<%def name="extra_javascript()">
  ${parent.extra_javascript()}
  <script src="https://cdnjs.cloudflare.com/ajax/libs/Chart.js/2.5.0/Chart.bundle.min.js"></script>
</%def>

<%def name="context_menu_items()">
  ${parent.context_menu_items()}
  % if master.has_perm('view'):
      <li>${h.link_to("View this {}".format(model_title), master.get_action_url('view', probe))}</li>
  % endif
  % if request.has_perm('tempmon.appliances.dashboard'):
      <li>${h.link_to("Go to the Dashboard", url('tempmon.dashboard'))}</li>
  % endif
</%def>

<%def name="render_this_page()">
  <div style="display: flex; justify-content: space-between;">

    <div class="form-wrapper">
      <div class="form">

        <b-field horizontal label="Appliance">
          <div>
            % if probe.appliance:
                <a href="${url('tempmon.appliances.view', uuid=probe.appliance.uuid)}">${probe.appliance}</a>
            % endif
          </div>
        </b-field>

        <b-field horizontal label="Probe Location">
          <div>
            ${probe.location or ""}
          </div>
        </b-field>

        <b-field horizontal label="Showing">
          <b-select v-model="currentTimeRange"
                    @input="timeRangeChanged">
            <option value="last hour">Last Hour</option>
            <option value="last 6 hours">Last 6 Hours</option>
            <option value="last day">Last Day</option>
            <option value="last week">Last Week</option>
          </b-select>
        </b-field>

      </div>
    </div>

    <div style="display: flex; align-items: flex-start;">
      <div class="object-helpers">
        ${self.object_helpers()}
      </div>

      <ul id="context-menu">
        ${self.context_menu_items()}
      </ul>
    </div>

  </div>

  <canvas ref="tempchart" width="400" height="150"></canvas>
</%def>

<%def name="modify_vue_vars()">
  ${parent.modify_vue_vars()}
  <script>

    ThisPageData.currentTimeRange = ${json.dumps(current_time_range)|n}
    ThisPageData.chart = null

    ThisPage.methods.fetchReadings = function(timeRange) {

        if (timeRange === undefined) {
            timeRange = this.currentTimeRange
        }

        let timeUnit = null
        if (timeRange == 'last hour') {
            timeUnit = 'minute'
        } else if (['last 6 hours', 'last day'].includes(timeRange)) {
            timeUnit = 'hour'
        } else {
            timeUnit = 'day'
        }

        if (this.chart) {
            this.chart.destroy()
        }

        let url = '${url(f'{route_prefix}.graph_readings', uuid=probe.uuid)}'
        let params = {'time-range': timeRange}
        this.$http.get(url, {params: params}).then(({ data }) => {

            this.chart = new Chart(this.$refs.tempchart, {
                type: 'scatter',
                data: {
                    datasets: [{
                        label: "${probe.description}",
                        data: data
                    }]
                },
                options: {
                    scales: {
                        xAxes: [{
                            type: 'time',
                            time: {unit: timeUnit},
                            position: 'bottom'
                        }]
                    }
                }
            });

        })
    }

    ThisPage.methods.timeRangeChanged = function(value) {
        this.fetchReadings(value)
    }

    ThisPage.mounted = function() {
        this.fetchReadings()
    }

  </script>
</%def>
