## -*- coding: utf-8; -*-
<%inherit file="/configure.mako" />

<%def name="form_content()">

  <h3 class="block is-size-3">Workflows</h3>
  <div class="block" style="padding-left: 2rem;">

    <p class="block">
      Users can only choose from the workflows enabled below.
    </p>

    <b-field>
      <b-checkbox name="rattail.batch.purchase.allow_ordering_from_scratch"
                  v-model="simpleSettings['rattail.batch.purchase.allow_ordering_from_scratch']"
                  native-value="true"
                  @input="settingsNeedSaved = true">
        From Scratch
      </b-checkbox>
    </b-field>

    <b-field>
      <b-checkbox name="rattail.batch.purchase.allow_ordering_from_file"
                  v-model="simpleSettings['rattail.batch.purchase.allow_ordering_from_file']"
                  native-value="true"
                  @input="settingsNeedSaved = true">
        From Order File
      </b-checkbox>
    </b-field>

  </div>

  <h3 class="block is-size-3">Vendors</h3>
  <div class="block" style="padding-left: 2rem;">

    <b-field message="If not set, user must choose a &quot;supported&quot; vendor.">
      <b-checkbox name="rattail.batch.purchase.allow_ordering_any_vendor"
                  v-model="simpleSettings['rattail.batch.purchase.allow_ordering_any_vendor']"
                  native-value="true"
                  @input="settingsNeedSaved = true">
        Allow ordering for <span class="has-text-weight-bold">any</span> vendor
      </b-checkbox>
    </b-field>

  </div>

  <h3 class="block is-size-3">Order Parsers</h3>
  <div class="block" style="padding-left: 2rem;">

    <p class="block">
      Only the selected file parsers will be exposed to users.
    </p>

    % for Parser in order_parsers:
        <b-field message="${Parser.key}">
          <b-checkbox name="order_parser_${Parser.key}"
                      v-model="orderParsers['${Parser.key}']"
                      native-value="true"
                      @input="settingsNeedSaved = true">
            ${Parser.title}
          </b-checkbox>
        </b-field>
    % endfor

  </div>

</%def>

<%def name="modify_vue_vars()">
  ${parent.modify_vue_vars()}
  <script>
    ThisPageData.orderParsers = ${json.dumps(order_parsers_data)|n}
  </script>
</%def>
