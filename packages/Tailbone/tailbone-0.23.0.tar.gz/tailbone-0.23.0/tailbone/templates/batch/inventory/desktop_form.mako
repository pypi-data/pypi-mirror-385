## -*- coding: utf-8; -*-
<%inherit file="/form.mako" />

<%def name="title()">Inventory Form</%def>

<%def name="object_helpers()">
  <nav class="panel">
    <p class="panel-heading">Batch</p>
    <div class="panel-block buttons">
      <div style="display: flex; flex-direction: column;">

        <once-button type="is-primary"
                     icon-left="eye"
                     tag="a" href="${url('batch.inventory.view', uuid=batch.uuid)}"
                     text="View Batch">
        </once-button>

        % if not batch.executed and master.has_perm('edit'):
            ${h.form(master.get_action_url('toggle_complete', batch), **{'@submit': 'toggleCompleteSubmitting = true'})}
            ${h.csrf_token(request)}
            ${h.hidden('complete', value='true')}
            <b-button type="is-primary"
                      native-type="submit"
                      icon-pack="fas"
                      icon-left="check"
                      :disabled="toggleCompleteSubmitting">
              {{ toggleCompleteSubmitting ? "Working, please wait..." : "Mark Complete" }}
            </b-button>
            ${h.end_form()}
        % endif

      </div>
    </div>
  </nav>
</%def>

<%def name="render_form_template()">
  <script type="text/x-template" id="${form.component}-template">
    <div class="product-info">

      ${h.form(form.action_url, **{'@submit': 'handleSubmit'})}
      ${h.csrf_token(request)}

      ${h.hidden('product', **{':value': 'productInfo.uuid'})}
      ${h.hidden('upc', **{':value': 'productInfo.upc'})}
      ${h.hidden('brand_name', **{':value': 'productInfo.brand_name'})}
      ${h.hidden('description', **{':value': 'productInfo.description'})}
      ${h.hidden('size', **{':value': 'productInfo.size'})}
      ${h.hidden('case_quantity', **{':value': 'productInfo.case_quantity'})}

      <b-field label="Product UPC" horizontal>
        <div style="display: flex; flex-direction: column;">
          <b-input v-model="productUPC"
                   ref="productUPC"
                   @input="productChanged"
                   @keydown.native="productKeydown">
          </b-input>
          <div class="has-text-centered block">

            <p v-if="!productInfo.uuid"
               class="block">
              please ENTER a scancode
            </p>

            <p v-if="productInfo.uuid"
               class="block">
              {{ productInfo.full_description }}
            </p>

            <div style="min-height: 150px; margin: 0.5rem 0;">
              <img v-if="productInfo.uuid"
                   :src="productInfo.image_url" />
            </div>

            <div v-if="alreadyPresentInBatch"
                 class="has-background-danger">
              product already exists in batch, please confirm count
            </div>

            <div v-if="forceUnitItem"
                 class="has-background-danger">
              pack item scanned, but must count units instead
            </div>

##                 <div v-if="productNotFound"
##                      class="has-background-danger">
##                   please confirm UPC and provide more details
##                 </div>

          </div>
        </div>
      </b-field>

##           <div v-if="productNotFound"
##                ## class="product-fields"
##                >
##
##             <div class="field-wrapper brand_name">
##               <label for="brand_name">Brand Name</label>
##               <div class="field">${h.text('brand_name')}</div>
##             </div>
##
##             <div class="field-wrapper description">
##               <label for="description">Description</label>
##               <div class="field">${h.text('description')}</div>
##             </div>
##
##             <div class="field-wrapper size">
##               <label for="size">Size</label>
##               <div class="field">${h.text('size')}</div>
##             </div>
##
##             <div class="field-wrapper case_quantity">
##               <label for="case_quantity">Units in Case</label>
##               <div class="field">${h.text('case_quantity')}</div>
##             </div>
##
##           </div>

      % if allow_cases:
          <b-field label="Cases" horizontal>
            <b-input name="cases"
                     v-model="productCases"
                     ref="productCases"
                     :disabled="!productInfo.uuid">
            </b-input>
          </b-field>
      % endif

      <b-field label="Units" horizontal>
        <b-input name="units"
                 v-model="productUnits"
                 ref="productUnits"
                 :disabled="!productInfo.uuid">
        </b-input>
      </b-field>

      <b-button type="is-primary"
                native-type="submit"
                :disabled="submitting">
        {{ submitting ? "Working, please wait..." : "Submit" }}
      </b-button>

      ${h.end_form()}
    </div>
  </script>

  <script type="text/javascript">

    let ${form.vue_component} = {
        template: '#${form.component}-template',
        mixins: [SimpleRequestMixin],

        mounted() {
            this.$refs.productUPC.focus()
        },

        methods: {

            clearProduct() {
                this.productInfo = {}
                ## this.productNotFound = false
                this.alreadyPresentInBatch = false
                this.forceUnitItem = false
                this.productCases = null
                this.productUnits = null
            },

            assertQuantity() {

                % if allow_cases:
                    let cases = parseFloat(this.productCases)
                    if (!isNaN(cases)) {
                        if (cases > 999999) {
                            alert("Case amount is invalid!")
                            this.$refs.productCases.focus()
                            return false
                        }
                        return true
                    }
                % endif

                let units = parseFloat(this.productUnits)
                if (!isNaN(units)) {
                    if (units > 999999) {
                        alert("Unit amount is invalid!")
                        this.$refs.productUnits.focus()
                        return false
                    }
                    return true
                }

                alert("Please provide case and/or unit quantity")
                % if allow_cases:
                    this.$refs.productCases.focus()
                % else:
                    this.$refs.productUnits.focus()
                % endif
            },

            handleSubmit(event) {
                if (!this.assertQuantity()) {
                    event.preventDefault()
                    return
                }
                this.submitting = true
            },

            productChanged() {
                this.clearProduct()
            },

            productKeydown(event) {
                if (event.which == 13) { // ENTER
                    this.productLookup()
                    event.preventDefault()
                }
            },

            productLookup() {
                let url = '${url('batch.inventory.desktop_lookup', uuid=batch.uuid)}'
                let params = {
                    upc: this.productUPC,
                }
                this.simpleGET(url, params, response => {

                    if (response.data.product.uuid) {

                        this.productUPC = response.data.product.upc_pretty
                        this.productInfo = response.data.product
                        this.forceUnitItem = response.data.force_unit_item
                        this.alreadyPresentInBatch = response.data.already_present_in_batch

                        if (this.alreadyPresentInBatch) {
                            this.productCases = response.data.cases
                            this.productUnits = response.data.units
                        } else if (this.productInfo.type2) {
                            this.productUnits = this.productInfo.units
                        }

                        this.$nextTick(() => {
                            if (this.productInfo.type2) {
                                this.$refs.productUnits.focus()
                            } else {
                                % if allow_cases and prefer_cases:
                                    if (this.productCases) {
                                        this.$refs.productCases.focus()
                                    } else if (this.productUnits) {
                                        this.$refs.productUnits.focus()
                                    } else {
                                        this.$refs.productCases.focus()
                                    }
                                % else:
                                    this.$refs.productUnits.focus()
                                % endif
                            }
                        })

                    } else {
                        ## this.productNotFound = true
                        alert("Product not found!")

                        // focus/select UPC entry
                        this.$refs.productUPC.focus()
                        // nb. must traverse into the <b-input> element
                        this.$refs.productUPC.$el.firstChild.select()
                    }

                }, response => {
                    if (response.data.error) {
                        alert(response.data.error)
                        if (response.data.redirect) {
                            location.href = response.data.redirect
                        }
                    }
                })
            },
        },
    }

    let ${form.vue_component}Data = {
        submitting: false,

        productUPC: null,
        ## productNotFound: false,
        productInfo: {},

        % if allow_cases:
        productCases: null,
        % endif
        productUnits: null,

        alreadyPresentInBatch: false,
        forceUnitItem: false,
    }

  </script>
</%def>

<%def name="modify_vue_vars()">
  ${parent.modify_vue_vars()}
  <script>
    ThisPageData.toggleCompleteSubmitting = false
  </script>
</%def>
