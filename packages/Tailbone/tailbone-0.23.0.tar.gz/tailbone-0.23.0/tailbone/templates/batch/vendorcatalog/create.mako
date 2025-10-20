## -*- coding: utf-8; -*-
<%inherit file="/batch/create.mako" />

<%def name="modify_vue_vars()">
  ${parent.modify_vue_vars()}
  <script>

    ${form.vue_component}Data.parsers = ${json.dumps(parsers_data)|n}

    ${form.vue_component}Data.vendorName = null
    ${form.vue_component}Data.vendorNameReplacement = null

    ${form.vue_component}.watch.field_model_parser_key = function(val) {
        let parser = this.parsers[val]
        if (parser.vendor_uuid) {
            if (this.field_model_vendor_uuid != parser.vendor_uuid) {
                // this.field_model_vendor_uuid = parser.vendor_uuid
                // this.vendorName = parser.vendor_name
                this.$refs.vendorAutocomplete.setSelection({
                    value: parser.vendor_uuid,
                    label: parser.vendor_name,
                })
            }
        }
    }

    ${form.vue_component}.methods.vendorLabelChanging = function(label) {
        this.vendorNameReplacement = label
    }

    ${form.vue_component}.methods.vendorChanged = function(uuid) {
        if (uuid) {
            this.vendorName = this.vendorNameReplacement
            this.vendorNameReplacement = null
        }
    }

  </script>
</%def>
