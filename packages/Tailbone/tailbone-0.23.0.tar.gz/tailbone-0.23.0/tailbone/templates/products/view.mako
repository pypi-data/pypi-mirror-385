## -*- coding: utf-8; -*-
<%inherit file="/master/view.mako" />

<%def name="extra_styles()">
  ${parent.extra_styles()}
  <style type="text/css">
    nav.item-panel {
        min-width: 600px;
    }
    #main-product-panel {
        margin-right: 2em;
        margin-top: 1em;
    }
    #pricing-panel .field-wrapper .field {
        white-space: nowrap;
    }
  </style>
</%def>

<%def name="render_main_fields(form)">
  % for field in panel_fields['main']:
      ${form.render_field_readonly(field)}
  % endfor
  ${self.extra_main_fields(form)}
</%def>

<%def name="left_column()">
  <nav class="panel item-panel" id="pricing-panel">
    <p class="panel-heading">Pricing</p>
    <div class="panel-block">
      <div style="width: 100%;">
        ${self.render_price_fields(form)}
      </div>
    </div>
  </nav>
  <nav class="panel item-panel">
    <p class="panel-heading">Flags</p>
    <div class="panel-block">
      <div style="width: 100%;">
        ${self.render_flag_fields(form)}
      </div>
    </div>
  </nav>
  ${self.extra_left_panels()}
</%def>

<%def name="right_column()">
  ${self.organization_panel()}
  ${self.movement_panel()}
  ${self.sources_panel()}
  ${self.notes_panel()}
  ${self.ingredients_panel()}
  ${self.lookup_codes_panel()}
  ${self.extra_right_panels()}
</%def>

<%def name="extra_main_fields(form)"></%def>

<%def name="organization_panel()">
  <nav class="panel item-panel">
    <p class="panel-heading">Organization</p>
    <div class="panel-block">
      <div style="width: 100%;">
        ${self.render_organization_fields(form)}
      </div>
    </div>
  </nav>
</%def>

<%def name="render_organization_fields(form)">
    ${form.render_field_readonly('department')}
    ${form.render_field_readonly('subdepartment')}
    ${form.render_field_readonly('category')}
    ${form.render_field_readonly('family')}
    ${form.render_field_readonly('report_code')}
</%def>

<%def name="render_price_fields(form)">
    ${form.render_field_readonly('price_required')}
    ${form.render_field_readonly('regular_price')}
    ${form.render_field_readonly('current_price')}
    ${form.render_field_readonly('current_price_ends')}
    ${form.render_field_readonly('sale_price')}
    ${form.render_field_readonly('sale_price_ends')}
    ${form.render_field_readonly('tpr_price')}
    ${form.render_field_readonly('tpr_price_ends')}
    ${form.render_field_readonly('suggested_price')}
    ${form.render_field_readonly('deposit_link')}
    ${form.render_field_readonly('tax')}
</%def>

<%def name="render_flag_fields(form)">
  % for field in panel_fields['flag']:
      ${form.render_field_readonly(field)}
  % endfor
</%def>

<%def name="movement_panel()">
  <nav class="panel item-panel">
    <p class="panel-heading">Movement</p>
    <div class="panel-block">
      <div style="width: 100%;">
        ${self.render_movement_fields(form)}
      </div>
    </div>
  </nav>
</%def>

<%def name="render_movement_fields(form)">
    ${form.render_field_readonly('last_sold')}
</%def>

<%def name="lookup_codes_grid()">
  ${lookup_codes['grid'].render_table_element(data_prop='lookupCodesData')|n}
</%def>

<%def name="lookup_codes_panel()">
  <nav class="panel item-panel">
    <p class="panel-heading">Additional Lookup Codes</p>
    <div class="panel-block">
      ${self.lookup_codes_grid()}
    </div>
  </nav>
</%def>

<%def name="sources_grid()">
  ${vendor_sources['grid'].render_table_element(data_prop='vendorSourcesData')|n}
</%def>

<%def name="sources_panel()">
  <nav class="panel item-panel">
    <p class="panel-heading">
      Vendor Sources
      % if request.rattail_config.versioning_enabled() and master.has_perm('versions'):
          <a href="#" @click.prevent="showCostHistory()">
            (view cost history)
          </a>
      % endif
    </p>
    <div class="panel-block">
      ${self.sources_grid()}
    </div>
  </nav>
</%def>

<%def name="notes_panel()">
  <nav class="panel item-panel">
    <p class="panel-heading">Notes</p>
    <div class="panel-block">
      <div class="field">${form.render_field_readonly('notes')}</div>
    </div>
  </nav>
</%def>

<%def name="ingredients_panel()">
  <nav class="panel item-panel">
    <p class="panel-heading">Ingredients</p>
    <div class="panel-block">
      ${form.render_field_readonly('ingredients')}
    </div>
  </nav>
</%def>

<%def name="extra_left_panels()"></%def>

<%def name="extra_right_panels()"></%def>

<%def name="render_this_page()">
  ${parent.render_this_page()}
  % if request.rattail_config.versioning_enabled() and master.has_perm('versions'):

      <b-modal :active.sync="showingPriceHistory_regular"
               has-modal-card>
        <div class="modal-card">
          <header class="modal-card-head">
            <p class="modal-card-title">
              Regular Price History
            </p>
          </header>
          <section class="modal-card-body">
            ${regular_price_history_grid.render_table_element(data_prop='regularPriceHistoryData', loading='regularPriceHistoryLoading', paginated=True, per_page=10)|n}
          </section>
          <footer class="modal-card-foot">
            <b-button @click="showingPriceHistory_regular = false">
              Close
            </b-button>
          </footer>
        </div>
      </b-modal>

      <b-modal :active.sync="showingPriceHistory_current"
               has-modal-card>
        <div class="modal-card">
          <header class="modal-card-head">
            <p class="modal-card-title">
              Current Price History
            </p>
          </header>
          <section class="modal-card-body">
            ${current_price_history_grid.render_table_element(data_prop='currentPriceHistoryData', loading='currentPriceHistoryLoading', paginated=True, per_page=10)|n}
          </section>
          <footer class="modal-card-foot">
            <b-button @click="showingPriceHistory_current = false">
              Close
            </b-button>
          </footer>
        </div>
      </b-modal>

      <b-modal :active.sync="showingPriceHistory_suggested"
               has-modal-card>
        <div class="modal-card">
          <header class="modal-card-head">
            <p class="modal-card-title">
              Suggested Price History
            </p>
          </header>
          <section class="modal-card-body">
            ${suggested_price_history_grid.render_table_element(data_prop='suggestedPriceHistoryData', loading='suggestedPriceHistoryLoading', paginated=True, per_page=10)|n}
          </section>
          <footer class="modal-card-foot">
            <b-button @click="showingPriceHistory_suggested = false">
              Close
            </b-button>
          </footer>
        </div>
      </b-modal>

      <b-modal :active.sync="showingCostHistory"
               has-modal-card>
        <div class="modal-card">
          <header class="modal-card-head">
            <p class="modal-card-title">
              Cost History
            </p>
          </header>
          <section class="modal-card-body">
            ${cost_history_grid.render_table_element(data_prop='costHistoryData', loading='costHistoryLoading', paginated=True, per_page=10)|n}
          </section>
          <footer class="modal-card-foot">
            <b-button @click="showingCostHistory = false">
              Close
            </b-button>
          </footer>
        </div>
      </b-modal>
  % endif
</%def>

<%def name="page_content()">
  <div style="display: flex; flex-direction: column;">

    <nav class="panel item-panel" id="main-product-panel">
      <p class="panel-heading">Product</p>
      <div class="panel-block">
        <div style="display: flex; gap: 2rem; width: 100%;">
          <div style="flex-grow: 1;">
            ${self.render_main_fields(form)}
          </div>
          <div>
            % if image_url:
                ${h.image(image_url, "Product Image", id='product-image', width=150, height=150)}
            % endif
          </div>
        </div>
      </div>
    </nav>

    <div style="display: flex;">
      <div class="panel-wrapper"> <!-- left column -->
        ${self.left_column()}
      </div> <!-- left column -->
      <div class="panel-wrapper" style="margin-left: 1em;"> <!-- right column -->
        ${self.right_column()}
      </div> <!-- right column -->
    </div>

  </div>

  % if buttons:
      ${buttons|n}
  % endif
</%def>

<%def name="modify_vue_vars()">
  ${parent.modify_vue_vars()}
  <script>

    ThisPageData.vendorSourcesData = ${json.dumps(vendor_sources['data'])|n}
    ThisPageData.lookupCodesData = ${json.dumps(lookup_codes['data'])|n}

    % if request.rattail_config.versioning_enabled() and master.has_perm('versions'):

        ThisPageData.showingPriceHistory_regular = false
        ThisPageData.regularPriceHistoryDataRaw = ${json.dumps(regular_price_history_grid.get_table_data()['data'])|n}
        ThisPageData.regularPriceHistoryLoading = false

        ThisPage.computed.regularPriceHistoryData = function() {
            let data = []
            this.regularPriceHistoryDataRaw.forEach(raw => {
                data.push({
                    price: raw.price_display,
                    since: raw.since,
                    changed: raw.changed_display_html,
                    changed_by: raw.changed_by_display,
                })
            })
            return data
        }

        ThisPage.methods.showPriceHistory_regular = function() {
            this.showingPriceHistory_regular = true
            this.regularPriceHistoryLoading = true

            let url = '${url("products.price_history", uuid=instance.uuid)}'
            let params = {'type': 'regular'}
            this.$http.get(url, {params: params}).then(response => {
                this.regularPriceHistoryDataRaw = response.data
                this.regularPriceHistoryLoading = false
            })
        }

        ThisPageData.showingPriceHistory_current = false
        ThisPageData.currentPriceHistoryDataRaw = ${json.dumps(current_price_history_grid.get_table_data()['data'])|n}
        ThisPageData.currentPriceHistoryLoading = false

        ThisPage.computed.currentPriceHistoryData = function() {
            let data = []
            this.currentPriceHistoryDataRaw.forEach(raw => {
                data.push({
                    price: raw.price_display,
                    price_type: raw.price_type,
                    since: raw.since,
                    changed: raw.changed_display_html,
                    changed_by: raw.changed_by_display,
                })
            })
            return data
        }

        ThisPage.methods.showPriceHistory_current = function() {
            this.showingPriceHistory_current = true
            this.currentPriceHistoryLoading = true

            let url = '${url("products.price_history", uuid=instance.uuid)}'
            let params = {'type': 'current'}
            this.$http.get(url, {params: params}).then(response => {
                this.currentPriceHistoryDataRaw = response.data
                this.currentPriceHistoryLoading = false
            })
        }

        ThisPageData.showingPriceHistory_suggested = false
        ThisPageData.suggestedPriceHistoryDataRaw = ${json.dumps(suggested_price_history_grid.get_table_data()['data'])|n}
        ThisPageData.suggestedPriceHistoryLoading = false

        ThisPage.computed.suggestedPriceHistoryData = function() {
            let data = []
            this.suggestedPriceHistoryDataRaw.forEach(raw => {
                data.push({
                    price: raw.price_display,
                    since: raw.since,
                    changed: raw.changed_display_html,
                    changed_by: raw.changed_by_display,
                })
            })
            return data
        }

        ThisPage.methods.showPriceHistory_suggested = function() {
            this.showingPriceHistory_suggested = true
            this.suggestedPriceHistoryLoading = true

            let url = '${url("products.price_history", uuid=instance.uuid)}'
            let params = {'type': 'suggested'}
            this.$http.get(url, {params: params}).then(response => {
                this.suggestedPriceHistoryDataRaw = response.data
                this.suggestedPriceHistoryLoading = false
            })
        }

        ThisPageData.showingCostHistory = false
        ThisPageData.costHistoryDataRaw = ${json.dumps(cost_history_grid.get_table_data()['data'])|n}
        ThisPageData.costHistoryLoading = false

        ThisPage.computed.costHistoryData = function() {
            let data = []
            this.costHistoryDataRaw.forEach(raw => {
                data.push({
                    cost: raw.cost_display,
                    vendor: raw.vendor,
                    since: raw.since,
                    changed: raw.changed_display_html,
                    changed_by: raw.changed_by_display,
                })
            })
            return data
        }

        ThisPage.methods.showCostHistory = function() {
            this.showingCostHistory = true
            this.costHistoryLoading = true

            let url = '${url("products.cost_history", uuid=instance.uuid)}'
            this.$http.get(url).then(response => {
                this.costHistoryDataRaw = response.data
                this.costHistoryLoading = false
            })
        }

    % endif
  </script>
</%def>
