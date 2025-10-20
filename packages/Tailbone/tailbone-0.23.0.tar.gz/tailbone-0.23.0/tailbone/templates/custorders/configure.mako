## -*- coding: utf-8; -*-
<%inherit file="/configure.mako" />

<%def name="form_content()">

  <h3 class="block is-size-3">Customer Handling</h3>
  <div class="block" style="padding-left: 2rem;">

    <b-field message="If not set, only a Person is required.">
      <b-checkbox name="rattail.custorders.new_order_requires_customer"
                  v-model="simpleSettings['rattail.custorders.new_order_requires_customer']"
                  native-value="true"
                  @input="settingsNeedSaved = true">
        Require a Customer account
      </b-checkbox>
    </b-field>

    <b-field message="If not set, default contact info is always assumed.">
      <b-checkbox name="rattail.custorders.new_orders.allow_contact_info_choice"
                  v-model="simpleSettings['rattail.custorders.new_orders.allow_contact_info_choice']"
                  native-value="true"
                  @input="settingsNeedSaved = true">
        Allow user to choose contact info
      </b-checkbox>
    </b-field>

    <div v-show="simpleSettings['rattail.custorders.new_orders.allow_contact_info_choice']"
         style="padding-left: 2rem;">

      <b-field message="Only applies if user is allowed to choose contact info.">
        <b-checkbox name="rattail.custorders.new_orders.allow_contact_info_create"
                    v-model="simpleSettings['rattail.custorders.new_orders.allow_contact_info_create']"
                    native-value="true"
                    @input="settingsNeedSaved = true">
          Allow user to enter new contact info
        </b-checkbox>
      </b-field>

      <div v-show="simpleSettings['rattail.custorders.new_orders.allow_contact_info_create']"
           style="padding-left: 2rem;">

        <p class="block">
          If you allow users to enter new contact info, the default action
          when the order is submitted, is to send email with details of
          the new contact info.&nbsp; Settings for these are at:
        </p>

        <ul class="list">
          <li class="list-item">
            ${h.link_to("New Phone Request", url('emailprofiles.view', key='new_phone_requested'))}
          </li>
          <li class="list-item">
            ${h.link_to("New Email Request", url('emailprofiles.view', key='new_email_requested'))}
          </li>
        </ul>

      </div>
    </div>
  </div>

  <h3 class="block is-size-3">Product Handling</h3>
  <div class="block" style="padding-left: 2rem;">

    <b-field>
      <b-checkbox name="rattail.custorders.allow_case_orders"
                  v-model="simpleSettings['rattail.custorders.allow_case_orders']"
                  native-value="true"
                  @input="settingsNeedSaved = true">
        Allow "case" orders
      </b-checkbox>
    </b-field>

    <b-field>
      <b-checkbox name="rattail.custorders.allow_unit_orders"
                  v-model="simpleSettings['rattail.custorders.allow_unit_orders']"
                  native-value="true"
                  @input="settingsNeedSaved = true">
        Allow "unit" orders
      </b-checkbox>
    </b-field>

    <b-field>
      <b-checkbox name="rattail.custorders.product_price_may_be_questionable"
                  v-model="simpleSettings['rattail.custorders.product_price_may_be_questionable']"
                  native-value="true"
                  @input="settingsNeedSaved = true">
        Allow prices to be flagged as "questionable"
      </b-checkbox>
    </b-field>

    <b-field>
      <b-checkbox name="rattail.custorders.allow_item_discounts"
                  v-model="simpleSettings['rattail.custorders.allow_item_discounts']"
                  native-value="true"
                  @input="settingsNeedSaved = true">
        Allow per-item discounts
      </b-checkbox>
    </b-field>

    <b-field>
      <b-checkbox name="rattail.custorders.allow_item_discounts_if_on_sale"
                  v-model="simpleSettings['rattail.custorders.allow_item_discounts_if_on_sale']"
                  native-value="true"
                  @input="settingsNeedSaved = true"
                  :disabled="!simpleSettings['rattail.custorders.allow_item_discounts']">
        Allow discount even if item is on sale
      </b-checkbox>
    </b-field>

    <div class="level-left block">
      <div class="level-item">Default item discount</div>
      <div class="level-item">
        <b-input name="rattail.custorders.default_item_discount"
                 v-model="simpleSettings['rattail.custorders.default_item_discount']"
                 @input="settingsNeedSaved = true"
                 style="width: 5rem;"
                 :disabled="!simpleSettings['rattail.custorders.allow_item_discounts']">
        </b-input>
      </div>
      <div class="level-item">%</div>
    </div>

    <b-field>
      <b-checkbox name="rattail.custorders.allow_past_item_reorder"
                  v-model="simpleSettings['rattail.custorders.allow_past_item_reorder']"
                  native-value="true"
                  @input="settingsNeedSaved = true">
        Allow re-order via past item lookup
      </b-checkbox>
    </b-field>

  </div>

  <h3 class="block is-size-3">Unknown Products</h3>
  <div class="block" style="padding-left: 2rem;">

    <b-field message="If set, user can enter details of an arbitrary new &quot;pending&quot; product.">
      <b-checkbox name="rattail.custorders.allow_unknown_product"
                  v-model="simpleSettings['rattail.custorders.allow_unknown_product']"
                  native-value="true"
                  @input="settingsNeedSaved = true">
        Allow creating orders for "unknown" products
      </b-checkbox>
    </b-field>

    <div v-if="simpleSettings['rattail.custorders.allow_unknown_product']">

      <p class="block">
        Require these fields for new product:
      </p>

      <div class="block"
           style="margin-left: 2rem;">
        % for field in pending_product_fields:
            <b-field>
              <b-checkbox name="rattail.custorders.unknown_product.fields.${field}.required"
                          v-model="simpleSettings['rattail.custorders.unknown_product.fields.${field}.required']"
                          native-value="true"
                          @input="settingsNeedSaved = true">
                ${field}
              </b-checkbox>
            </b-field>
        % endfor
      </div>

      <b-field message="If set, user is always prompted to confirm price when adding new product.">
        <b-checkbox name="rattail.custorders.unknown_product.always_confirm_price"
                    v-model="simpleSettings['rattail.custorders.unknown_product.always_confirm_price']"
                    native-value="true"
                    @input="settingsNeedSaved = true">
          Require price confirmation
        </b-checkbox>
      </b-field>

    </div>

  </div>
</%def>


${parent.body()}
