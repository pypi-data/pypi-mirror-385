## -*- coding: utf-8; -*-
<%inherit file="/master/view_row.mako" />

<%def name="extra_styles()">
  ${parent.extra_styles()}
  <style type="text/css">

    nav.panel {
        margin: 0.5rem;
    }

    .header-fields {
        margin-top: 1rem;
    }

    .header-fields .field.is-horizontal {
        margin-left: 3rem;
    }

    .header-fields .field.is-horizontal .field-label .label {
        white-space: nowrap;
    }

    .quantity-form-fields {
        margin: 2rem;
    }

    .quantity-form-fields .field.is-horizontal .field-label .label {
        text-align: left;
        width: 8rem;
    }

    .remove-credit .field.is-horizontal .field-label .label {
        white-space: nowrap;
    }

  </style>
</%def>

<%def name="page_content()">

  <b-field grouped class="header-fields">

    <b-field label="Sequence" horizontal>
      {{ rowData.sequence }}
    </b-field>

    <b-field label="Status" horizontal>
      {{ rowData.status }}
    </b-field>

    <b-field label="Calculated Total" horizontal>
      {{ rowData.invoice_total_calculated }}
    </b-field>

  </b-field>

  <div style="display: flex;">

    <nav class="panel">
      <p class="panel-heading">Product</p>
      <div class="panel-block">
        <div style="display: flex; gap: 1rem;">
          <div style="flex-grow: 1;"
             % if request.use_oruga:
                 class="form-wrapper"
             % endif
            >
            ${form.render_field_readonly('item_entry')}
            % if row.product:
                ${form.render_field_readonly(product_key_field)}
                ${form.render_field_readonly('product')}
            % else:
                ${form.render_field_readonly(product_key_field)}
                % if product_key_field != 'upc':
                    ${form.render_field_readonly('upc')}
                % endif
                ${form.render_field_readonly('brand_name')}
                ${form.render_field_readonly('description')}
                ${form.render_field_readonly('size')}
            % endif
            ${form.render_field_readonly('vendor_code')}
            ${form.render_field_readonly('case_quantity')}
            ${form.render_field_readonly('catalog_unit_cost')}
          </div>
          % if image_url:
              <div>
                ${h.image(image_url, "Product Image", width=150, height=150)}
              </div>
          % endif
        </div>
      </div>
    </nav>

    <nav class="panel">
      <p class="panel-heading">Quantities</p>
      <div class="panel-block">
        <div>
          <div class="quantity-form-fields">

            <b-field label="Ordered" horizontal>
              {{ rowData.ordered }}
            </b-field>

            <hr />

            <b-field label="Shipped" horizontal>
              {{ rowData.shipped }}
            </b-field>

            <hr />

            <b-field label="Received" horizontal
                     v-if="rowData.received">
              {{ rowData.received }}
            </b-field>

            <b-field label="Damaged" horizontal
                     v-if="rowData.damaged">
              {{ rowData.damaged }}
            </b-field>

            <b-field label="Expired" horizontal
                     v-if="rowData.expired">
              {{ rowData.expired }}
            </b-field>

            <b-field label="Mispick" horizontal
                     v-if="rowData.mispick">
              {{ rowData.mispick }}
            </b-field>

            <b-field label="Missing" horizontal
                     v-if="rowData.missing">
              {{ rowData.missing }}
            </b-field>

          </div>

          % if master.has_perm('edit_row') and master.row_editable(row):
              <div class="buttons">
                <b-button type="is-primary"
                          @click="accountForProductInit()"
                          icon-pack="fas"
                          icon-left="check">
                  Account for Product
                </b-button>
                <b-button type="is-warning"
                          @click="declareCreditInit()"
                          :disabled="!rowData.received"
                          icon-pack="fas"
                          icon-left="thumbs-down">
                  Declare Credit
                </b-button>
              </div>
          % endif

        </div>
      </div>
    </nav>

  </div>

  <${b}-modal has-modal-card
              % if request.use_oruga:
                  v-model:active="accountForProductShowDialog"
              % else:
                  :active.sync="accountForProductShowDialog"
              % endif
              >
    <div class="modal-card">

      <header class="modal-card-head">
        <p class="modal-card-title">Account for Product</p>
      </header>

      <section class="modal-card-body">

        <p class="block">
          This is for declaring that you have encountered some
          amount of the product.&nbsp; Ideally you will just
          "receive" it normally, but you can indicate a "credit"
          state if there is something amiss.
        </p>

        <b-field grouped>

          % if allow_cases:
              <b-field label="Case Qty.">
                <span class="control">
                  {{ rowData.case_quantity }}
                </span>
              </b-field>

              <span class="control">
                &nbsp;
              </span>
          % endif

          <b-field label="Product State"
                   :type="accountForProductMode ? null : 'is-danger'">
            <b-select v-model="accountForProductMode">
              <option v-for="mode in possibleReceivingModes"
                      :key="mode"
                      :value="mode">
                {{ mode }}
              </option>
            </b-select>
          </b-field>

          <b-field label="Expiration Date"
                   v-show="accountForProductMode == 'expired'"
                   :type="accountForProductExpiration ? null : 'is-danger'">
            <tailbone-datepicker v-model="accountForProductExpiration">
            </tailbone-datepicker>
          </b-field>

        </b-field>

        <div style="display: flex; gap: 0.5rem; align-items: center;">

          <numeric-input v-model="accountForProductQuantity"
                         ref="accountForProductQuantityInput">
          </numeric-input>

          % if allow_cases:
              % if request.use_oruga:
                  <div>
                    <o-button label="Units"
                              :variant="accountForProductUOM == 'units' ? 'primary' : null"
                              @click="accountForProductUOMClicked('units')" />
                    <o-button label="Cases"
                              :variant="accountForProductUOM == 'cases' ? 'primary' : null"
                              @click="accountForProductUOMClicked('cases')" />
                  </div>
              % else:
                  <b-field
                    ## TODO: a bit hacky, but otherwise buefy styles throw us off here
                    style="margin-bottom: 0;">
                    <b-radio-button v-model="accountForProductUOM"
                                    @click.native="accountForProductUOMClicked('units')"
                                    native-value="units">
                      Units
                    </b-radio-button>
                    <b-radio-button v-model="accountForProductUOM"
                                    @click.native="accountForProductUOMClicked('cases')"
                                    native-value="cases">
                      Cases
                    </b-radio-button>
                  </b-field>
              % endif
              <span v-if="accountForProductUOM == 'cases' && accountForProductQuantity">
                = {{ accountForProductTotalUnits }}
              </span>

          % else:
              <input type="hidden" v-model="accountForProductUOM" />
              <span>Units</span>
          % endif

        </div>
      </section>

      <footer class="modal-card-foot">
        <b-button @click="accountForProductShowDialog = false">
          Cancel
        </b-button>
        <b-button type="is-primary"
                  @click="accountForProductSubmit()"
                  :disabled="accountForProductSubmitDisabled"
                  icon-pack="fas"
                  icon-left="check">
          {{ accountForProductSubmitting ? "Working, please wait..." : "Account for Product" }}
        </b-button>
      </footer>
    </div>
  </${b}-modal>

  <${b}-modal has-modal-card
              % if request.use_oruga:
                  v-model:active="declareCreditShowDialog"
              % else:
                  :active.sync="declareCreditShowDialog"
              % endif
              >
    <div class="modal-card">

      <header class="modal-card-head">
        <p class="modal-card-title">Declare Credit</p>
      </header>

      <section class="modal-card-body">

        <p class="block">
          This is for <span class="is-italic">converting</span>
          some amount you <span class="is-italic">already
          received</span>, and now declaring there is something
          wrong with it.
        </p>

        <b-field grouped>

          <b-field label="Received">
            <span class="control">
              {{ rowData.received }}
            </span>
          </b-field>

          <span class="control">
            &nbsp;
          </span>

          <b-field label="Credit Type"
                   :type="declareCreditType ? null : 'is-danger'">
            <b-select v-model="declareCreditType">
              <option v-for="typ in possibleCreditTypes"
                      :key="typ"
                      :value="typ">
                {{ typ }}
              </option>
            </b-select>
          </b-field>

          <b-field label="Expiration Date"
                   v-show="declareCreditType == 'expired'"
                   :type="declareCreditExpiration ? null : 'is-danger'">
            <tailbone-datepicker v-model="declareCreditExpiration">
            </tailbone-datepicker>
          </b-field>

        </b-field>

        <div style="display: flex; gap: 0.5rem; align-items: center;">

            <numeric-input v-model="declareCreditQuantity"
                           ref="declareCreditQuantityInput">
            </numeric-input>

            % if allow_cases:

                % if request.use_oruga:
                    <div>
                      <o-button label="Units"
                                :variant="declareCreditUOM == 'units' ? 'primary' : null"
                                @click="declareCreditUOM = 'units'" />
                      <o-button label="Cases"
                                :variant="declareCreditUOM == 'cases' ? 'primary' : null"
                                @click="declareCreditUOM = 'cases'" />
                    </div>
                % else:
                    <b-field
                      ## TODO: a bit hacky, but otherwise buefy styles throw us off here
                      style="margin-bottom: 0;">
                      <b-radio-button v-model="declareCreditUOM"
                                      @click.native="declareCreditUOMClicked('units')"
                                      native-value="units">
                        Units
                      </b-radio-button>
                      <b-radio-button v-model="declareCreditUOM"
                                      @click.native="declareCreditUOMClicked('cases')"
                                      native-value="cases">
                        Cases
                      </b-radio-button>
                    </b-field>
                % endif
                <span v-if="declareCreditUOM == 'cases' && declareCreditQuantity">
                  = {{ declareCreditTotalUnits }}
                </span>

            % else:
                <b-field>
                  <input type="hidden" v-model="declareCreditUOM" />
                  Units
                </b-field>
            % endif

        </div>
      </section>

      <footer class="modal-card-foot">
        <b-button @click="declareCreditShowDialog = false">
          Cancel
        </b-button>
        <b-button type="is-warning"
                  @click="declareCreditSubmit()"
                  :disabled="declareCreditSubmitDisabled"
                  icon-pack="fas"
                  icon-left="thumbs-down">
          {{ declareCreditSubmitting ? "Working, please wait..." : "Declare this Credit" }}
        </b-button>
      </footer>
    </div>
  </${b}-modal>

  <nav class="panel" >
    <p class="panel-heading">Credits</p>
    <div class="panel-block">
      <div>
        ${form.render_field_value('credits')}
      </div>
    </div>
  </nav>

  <b-modal has-modal-card
           :active.sync="removeCreditShowDialog">
    <div class="modal-card remove-credit">

      <header class="modal-card-head">
        <p class="modal-card-title">Un-Declare Credit</p>
      </header>

      <section class="modal-card-body">

        <p class="block">
          If you un-declare this credit, the quantity below will
          be added back to the
          <span class="has-text-weight-bold">Received</span> tally.
        </p>

        <b-field label="Credit Type" horizontal>
          {{ removeCreditRow.credit_type }}
        </b-field>

        <b-field label="Quantity" horizontal>
          {{ removeCreditRow.shorted }}
        </b-field>

      </section>

      <footer class="modal-card-foot">
        <b-button @click="removeCreditShowDialog = false">
          Cancel
        </b-button>
        <b-button type="is-danger"
                  @click="removeCreditSubmit()"
                  :disabled="removeCreditSubmitting"
                  icon-pack="fas"
                  icon-left="trash">
          {{ removeCreditSubmitting ? "Working, please wait..." : "Un-Declare this Credit" }}
        </b-button>
      </footer>
    </div>
  </b-modal>

  <div style="display: flex;">

    % if master.batch_handler.has_purchase_order(batch):
        <nav class="panel" >
          <p class="panel-heading">Purchase Order</p>
          <div class="panel-block">
            <div
              % if request.use_oruga:
                  class="form-wrapper"
              % endif
              >
              ${form.render_field_readonly('po_line_number')}
              ${form.render_field_readonly('po_unit_cost')}
              ${form.render_field_readonly('po_case_size')}
              ${form.render_field_readonly('po_total')}
            </div>
          </div>
        </nav>
    % endif

    % if master.batch_handler.has_invoice_file(batch):
        <nav class="panel" >
          <p class="panel-heading">Invoice</p>
          <div class="panel-block">
            <div
              % if request.use_oruga:
                  class="form-wrapper"
              % endif
              >
              ${form.render_field_readonly('invoice_number')}
              ${form.render_field_readonly('invoice_line_number')}
              ${form.render_field_readonly('invoice_unit_cost')}
              ${form.render_field_readonly('invoice_case_size')}
              ${form.render_field_readonly('invoice_total', label="Invoice Total")}
            </div>
          </div>
        </nav>
    % endif

  </div>
</%def>

<%def name="modify_vue_vars()">
  ${parent.modify_vue_vars()}
  <script>

##     ThisPage.methods.editUnitCost = function() {
##         alert("TODO: not yet implemented")
##     }

    ThisPage.methods.confirmUnitCost = function() {
        alert("TODO: not yet implemented")
    }

    ThisPageData.rowData = ${json.dumps(row_context)|n}
    ThisPageData.possibleReceivingModes = ${json.dumps(possible_receiving_modes)|n}
    ThisPageData.possibleCreditTypes = ${json.dumps(possible_credit_types)|n}

    ThisPageData.accountForProductShowDialog = false
    ThisPageData.accountForProductMode = null
    ThisPageData.accountForProductQuantity = null
    ThisPageData.accountForProductUOM = 'units'
    ThisPageData.accountForProductExpiration = null
    ThisPageData.accountForProductSubmitting = false

    ThisPage.computed.accountForProductTotalUnits = function() {
        return this.renderQuantity(this.accountForProductQuantity,
                                   this.accountForProductUOM)
    }

    ThisPage.computed.accountForProductSubmitDisabled = function() {
        if (!this.accountForProductMode) {
            return true
        }
        if (this.accountForProductMode == 'expired' && !this.accountForProductExpiration) {
            return true
        }
        if (!this.accountForProductQuantity || this.accountForProductQuantity == 0) {
            return true
        }
        if (this.accountForProductSubmitting) {
            return true
        }
        return false
    }

    ThisPage.methods.accountForProductInit = function() {
        this.accountForProductMode = 'received'
        this.accountForProductExpiration = null
        this.accountForProductQuantity = 0
        this.accountForProductUOM = 'units'
        this.accountForProductShowDialog = true
        this.$nextTick(() => {
            this.$refs.accountForProductQuantityInput.select()
            this.$refs.accountForProductQuantityInput.focus()
        })
    }

    ThisPage.methods.accountForProductUOMClicked = function(uom) {

        % if request.use_oruga:
            this.accountForProductUOM = uom
        % endif

        // TODO: this does not seem to work as expected..even though
        // the code appears to be correct
        this.$nextTick(() => {
            this.$refs.accountForProductQuantityInput.focus()
        })
    }

    ThisPage.methods.accountForProductSubmit = function() {

        let qty = parseFloat(this.accountForProductQuantity)
        if (qty == NaN || !qty) {
            this.$buefy.toast.open({
                message: "You must enter a quantity.",
                type: 'is-warning',
                duration: 4000, // 4 seconds
            })
            return
        }

        if (this.accountForProductMode != 'received' && qty < 0) {
            this.$buefy.toast.open({
                message: "Negative amounts are only allowed for the \"received\" state.",
                type: 'is-warning',
                duration: 4000, // 4 seconds
            })
            return
        }

        this.accountForProductSubmitting = true
        let url = '${url('{}.receive_row'.format(route_prefix), uuid=batch.uuid, row_uuid=row.uuid)}'
        let params = {
            mode: this.accountForProductMode,
            quantity: {cases: null, units: null},
            expiration_date: this.accountForProductExpiration,
        }

        if (this.accountForProductUOM == 'cases') {
            params.quantity.cases = this.accountForProductQuantity
        } else {
            params.quantity.units = this.accountForProductQuantity
        }

        this.submitForm(url, params, response => {
            this.rowData = response.data.row
            this.accountForProductSubmitting = false
            this.accountForProductShowDialog = false
        }, response => {
            this.accountForProductSubmitting = false
        })
    }

    ThisPageData.declareCreditShowDialog = false
    ThisPageData.declareCreditType = null
    ThisPageData.declareCreditExpiration = null
    ThisPageData.declareCreditQuantity = null
    ThisPageData.declareCreditUOM = 'units'
    ThisPageData.declareCreditSubmitting = false

    ThisPage.methods.renderQuantity = function(qty, uom) {
        qty = parseFloat(qty)
        if (qty == NaN) {
            return "n/a"
        }
        if (uom == 'cases') {
            qty *= this.rowData.case_quantity
        }
        if (qty == NaN) {
            return "n/a"
        }
        if (qty == 1) {
            return "1 unit"
        }
        if (qty == -1) {
            return "-1 unit"
        }
        if (Math.round(qty) == qty) {
            return qty.toString() + " units"
        }
        return qty.toFixed(4) + " units"
    }

    ThisPage.computed.declareCreditTotalUnits = function() {
        return this.renderQuantity(this.declareCreditQuantity,
                                   this.declareCreditUOM)
    }

    ThisPage.computed.declareCreditSubmitDisabled = function() {
        if (!this.declareCreditType) {
            return true
        }
        if (this.declareCreditType == 'expired' && !this.declareCreditExpiration) {
            return true
        }
        if (!this.declareCreditQuantity || this.declareCreditQuantity == 0) {
            return true
        }
        if (this.declareCreditSubmitting) {
            return true
        }
        return false
    }

    ThisPage.methods.declareCreditInit = function() {
        this.declareCreditType = null
        this.declareCreditExpiration = null
        % if allow_cases:
            if (this.rowData.cases_received) {
                this.declareCreditQuantity = this.rowData.cases_received
                this.declareCreditUOM = 'cases'
            } else {
                this.declareCreditQuantity = this.rowData.units_received
                this.declareCreditUOM = 'units'
            }
        % else:
            this.declareCreditQuantity = this.rowData.units_received
            this.declareCreditUOM = 'units'
        % endif
        this.declareCreditShowDialog = true
    }

    ThisPage.methods.declareCreditSubmit = function() {
        this.declareCreditSubmitting = true
        let url = '${url('{}.declare_credit'.format(route_prefix), uuid=batch.uuid, row_uuid=row.uuid)}'
        let params = {
            credit_type: this.declareCreditType,
            cases: null,
            units: null,
            expiration_date: this.declareCreditExpiration,
        }

        % if allow_cases:
            if (this.declareCreditUOM == 'cases') {
                params.cases = this.declareCreditQuantity
            } else {
                params.units = this.declareCreditQuantity
            }
        % else:
            params.units = this.declareCreditQuantity
        % endif

        this.submitForm(url, params, response => {
            this.rowData = response.data.row
            this.declareCreditSubmitting = false
            this.declareCreditShowDialog = false
        }, response => {
            this.declareCreditSubmitting = false
        })
    }

    ThisPageData.removeCreditShowDialog = false
    ThisPageData.removeCreditRow = {}
    ThisPageData.removeCreditSubmitting = false

    ThisPage.methods.removeCreditInit = function(row) {
        this.removeCreditRow = row
        this.removeCreditShowDialog = true
    }

    ThisPage.methods.removeCreditSubmit = function() {
        this.removeCreditSubmitting = true
        let url = '${url('{}.undeclare_credit'.format(route_prefix), uuid=batch.uuid, row_uuid=row.uuid)}'
        let params = {
            uuid: this.removeCreditRow.uuid,
        }

        this.submitForm(url, params, response => {
            this.rowData = response.data.row
            this.removeCreditSubmitting = false
            this.removeCreditShowDialog = false
        })
    }

  </script>
</%def>
