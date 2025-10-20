## -*- coding: utf-8; -*-
<%inherit file="/master/index.mako" />

<%def name="grid_tools()">
  ${parent.grid_tools()}
  % if label_profiles and master.has_perm('print_labels'):
      <b-field grouped>
        <b-field label="Label">
          <b-select v-model="quickLabelProfile">
            % for profile in label_profiles:
                <option value="${profile.uuid}">
                  ${profile.description}
                </option>
            % endfor
          </b-select>
        </b-field>
        <b-field label="Qty.">
          <b-input v-model="quickLabelQuantity"
                   ref="quickLabelQuantityInput"
                   style="width: 4rem;">
          </b-input>
        </b-field>
      </b-field>
  % endif
</%def>

<%def name="render_grid_component()">
  <${grid.component} :csrftoken="csrftoken"
     % if master.deletable and master.has_perm('delete') and master.delete_confirm == 'simple':
     @deleteActionClicked="deleteObject"
     % endif
     % if label_profiles and master.has_perm('print_labels'):
     @quick-label-print="quickLabelPrint"
     % endif
     >
  </${grid.component}>
</%def>

<%def name="modify_vue_vars()">
  ${parent.modify_vue_vars()}
  % if label_profiles and master.has_perm('print_labels'):
      <script>

        ${grid.vue_component}Data.quickLabelProfile = ${json.dumps(label_profiles[0].uuid)|n}
        ${grid.vue_component}Data.quickLabelQuantity = 1
        ${grid.vue_component}Data.quickLabelSpeedbumpThreshold = ${json.dumps(quick_label_speedbump_threshold)|n}

        ${grid.vue_component}.methods.quickLabelPrint = function(row) {

            let quantity = parseInt(this.quickLabelQuantity)
            if (isNaN(quantity)) {
                alert("You must provide a valid label quantity.")
                this.$refs.quickLabelQuantityInput.focus()
                return
            }

            if (this.quickLabelSpeedbumpThreshold && quantity >= this.quickLabelSpeedbumpThreshold) {
                if (!confirm("Are you sure you want to print " + quantity + " labels?")) {
                    return
                }
            }

            this.$emit('quick-label-print', row.uuid, this.quickLabelProfile, quantity)
        }

        ThisPage.methods.quickLabelPrint = function(product, profile, quantity) {
            let url = '${url('products.print_labels')}'

            let data = new FormData()
            data.append('product', product)
            data.append('profile', profile)
            data.append('quantity', quantity)

            this.submitForm(url, data, response => {
                if (quantity == 1) {
                    alert("1 label has been printed.")
                } else {
                    alert(quantity.toString() + " labels have been printed.")
                }
            })
        }

      </script>
  % endif
</%def>
