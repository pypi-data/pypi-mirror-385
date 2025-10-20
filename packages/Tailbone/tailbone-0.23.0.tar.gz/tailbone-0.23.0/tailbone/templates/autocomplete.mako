## -*- coding: utf-8; -*-

<%def name="tailbone_autocomplete_template()">
  <script type="text/x-template" id="tailbone-autocomplete-template">
    <div>

      <b-autocomplete ref="autocomplete"
                      :name="name"
                      v-show="!value && !selected"
                      v-model="buefyValue"
                      :placeholder="placeholder"
                      :data="data"
                      @typing="getAsyncData"
                      @select="selectionMade"
                      keep-first>
        <template slot-scope="props">
          {{ props.option.label }}
        </template>
      </b-autocomplete>

      <b-button v-if="value || selected"
                style="width: 100%; justify-content: left;"
                @click="clearSelection(true)">
        {{ getDisplayText() }} (click to change)
      </b-button>

    </div>
  </script>
</%def>
