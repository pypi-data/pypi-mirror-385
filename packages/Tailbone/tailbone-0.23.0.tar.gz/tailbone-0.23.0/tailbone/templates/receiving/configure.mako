## -*- coding: utf-8; -*-
<%inherit file="/configure.mako" />

<%def name="form_content()">

  <h3 class="block is-size-3">Workflows</h3>
  <div class="block" style="padding-left: 2rem;">

    <p class="block">
      Users can only choose from the workflows enabled below.
    </p>

    <b-field>
      <b-checkbox name="rattail.batch.purchase.allow_receiving_from_scratch"
                  v-model="simpleSettings['rattail.batch.purchase.allow_receiving_from_scratch']"
                  native-value="true"
                  @input="settingsNeedSaved = true">
        From Scratch
      </b-checkbox>
    </b-field>

    <b-field>
      <b-checkbox name="rattail.batch.purchase.allow_receiving_from_invoice"
                  v-model="simpleSettings['rattail.batch.purchase.allow_receiving_from_invoice']"
                  native-value="true"
                  @input="settingsNeedSaved = true">
        From Single Invoice
      </b-checkbox>
    </b-field>

    <b-field>
      <b-checkbox name="rattail.batch.purchase.allow_receiving_from_multi_invoice"
                  v-model="simpleSettings['rattail.batch.purchase.allow_receiving_from_multi_invoice']"
                  native-value="true"
                  @input="settingsNeedSaved = true">
        From Multiple (Combined) Invoices
      </b-checkbox>
    </b-field>

    <b-field>
      <b-checkbox name="rattail.batch.purchase.allow_receiving_from_purchase_order"
                  v-model="simpleSettings['rattail.batch.purchase.allow_receiving_from_purchase_order']"
                  native-value="true"
                  @input="settingsNeedSaved = true">
        From Purchase Order
      </b-checkbox>
    </b-field>

    <b-field>
      <b-checkbox name="rattail.batch.purchase.allow_receiving_from_purchase_order_with_invoice"
                  v-model="simpleSettings['rattail.batch.purchase.allow_receiving_from_purchase_order_with_invoice']"
                  native-value="true"
                  @input="settingsNeedSaved = true">
        From Purchase Order, with Invoice
      </b-checkbox>
    </b-field>

    <b-field>
      <b-checkbox name="rattail.batch.purchase.allow_truck_dump_receiving"
                  v-model="simpleSettings['rattail.batch.purchase.allow_truck_dump_receiving']"
                  native-value="true"
                  @input="settingsNeedSaved = true">
        Truck Dump
      </b-checkbox>
    </b-field>

  </div>

  <h3 class="block is-size-3">Vendors</h3>
  <div class="block" style="padding-left: 2rem;">

    <b-field message="If not set, user must choose a &quot;supported&quot; vendor.">
      <b-checkbox name="rattail.batch.purchase.allow_receiving_any_vendor"
                  v-model="simpleSettings['rattail.batch.purchase.allow_receiving_any_vendor']"
                  native-value="true"
                  @input="settingsNeedSaved = true">
        Allow receiving for <span class="has-text-weight-bold">any</span> vendor
      </b-checkbox>
    </b-field>

  </div>

  <h3 class="block is-size-3">Display</h3>
  <div class="block" style="padding-left: 2rem;">

    <b-field>
      <b-checkbox name="rattail.batch.purchase.receiving.show_ordered_column_in_grid"
                  v-model="simpleSettings['rattail.batch.purchase.receiving.show_ordered_column_in_grid']"
                  native-value="true"
                  @input="settingsNeedSaved = true">
        Show "ordered" quantities in row grid
      </b-checkbox>
    </b-field>

    <b-field>
      <b-checkbox name="rattail.batch.purchase.receiving.show_shipped_column_in_grid"
                  v-model="simpleSettings['rattail.batch.purchase.receiving.show_shipped_column_in_grid']"
                  native-value="true"
                  @input="settingsNeedSaved = true">
        Show "shipped" quantities in row grid
      </b-checkbox>
    </b-field>

  </div>

  <h3 class="block is-size-3">Product Handling</h3>
  <div class="block" style="padding-left: 2rem;">

    <b-field message="NB. Allow Cases setting also affects Ordering behavior.">
      <b-checkbox name="rattail.batch.purchase.allow_cases"
                  v-model="simpleSettings['rattail.batch.purchase.allow_cases']"
                  native-value="true"
                  @input="settingsNeedSaved = true">
        Allow Cases
      </b-checkbox>
    </b-field>

    <b-field message="NB. Allow Decimal Quantities setting also affects Ordering behavior.">
      <b-checkbox name="rattail.batch.purchase.allow_decimal_quantities"
                  v-model="simpleSettings['rattail.batch.purchase.allow_decimal_quantities']"
                  native-value="true"
                  @input="settingsNeedSaved = true">
        Allow Decimal Quantities
      </b-checkbox>
    </b-field>

    <b-field>
      <b-checkbox name="rattail.batch.purchase.allow_expired_credits"
                  v-model="simpleSettings['rattail.batch.purchase.allow_expired_credits']"
                  native-value="true"
                  @input="settingsNeedSaved = true">
        Allow "Expired" Credits
      </b-checkbox>
    </b-field>

    <b-field>
      <b-checkbox name="rattail.batch.purchase.receiving.should_autofix_invoice_case_vs_unit"
                  v-model="simpleSettings['rattail.batch.purchase.receiving.should_autofix_invoice_case_vs_unit']"
                  native-value="true"
                  @input="settingsNeedSaved = true">
        Try to auto-correct "case vs. unit" mistakes from invoice parser
      </b-checkbox>
    </b-field>

    <b-field>
      <b-checkbox name="rattail.batch.purchase.receiving.allow_edit_catalog_unit_cost"
                  v-model="simpleSettings['rattail.batch.purchase.receiving.allow_edit_catalog_unit_cost']"
                  native-value="true"
                  @input="settingsNeedSaved = true">
        Allow edit of Catalog Unit Cost
      </b-checkbox>
    </b-field>

    <b-field>
      <b-checkbox name="rattail.batch.purchase.receiving.allow_edit_invoice_unit_cost"
                  v-model="simpleSettings['rattail.batch.purchase.receiving.allow_edit_invoice_unit_cost']"
                  native-value="true"
                  @input="settingsNeedSaved = true">
        Allow edit of Invoice Unit Cost
      </b-checkbox>
    </b-field>

    <b-field>
      <b-checkbox name="rattail.batch.purchase.receiving.auto_missing_credits"
                  v-model="simpleSettings['rattail.batch.purchase.receiving.auto_missing_credits']"
                  native-value="true"
                  @input="settingsNeedSaved = true">
        Auto-generate "missing" (DNR) credits for items not accounted for
      </b-checkbox>
    </b-field>

  </div>

  <h3 class="block is-size-3">Mobile Interface</h3>
  <div class="block" style="padding-left: 2rem;">

    <b-field message="TODO: this may also affect Ordering (?)">
      <b-checkbox name="rattail.batch.purchase.mobile_images"
                  v-model="simpleSettings['rattail.batch.purchase.mobile_images']"
                  native-value="true"
                  @input="settingsNeedSaved = true">
        Show Product Images
      </b-checkbox>
    </b-field>

    <b-field message="If set, one or more &quot;quick receive&quot; buttons will be available for mobile receiving.">
      <b-checkbox name="rattail.batch.purchase.mobile_quick_receive"
                  v-model="simpleSettings['rattail.batch.purchase.mobile_quick_receive']"
                  native-value="true"
                  @input="settingsNeedSaved = true">
        Allow "Quick Receive"
      </b-checkbox>
    </b-field>

    <b-field message="If set, only a &quot;quick receive all&quot; button will be shown.  Only applicable if quick receive (above) is enabled.">
      <b-checkbox name="rattail.batch.purchase.mobile_quick_receive_all"
                  v-model="simpleSettings['rattail.batch.purchase.mobile_quick_receive_all']"
                  native-value="true"
                  @input="settingsNeedSaved = true">
        Quick Receive "All or Nothing"
      </b-checkbox>
    </b-field>

  </div>
</%def>


${parent.body()}
