## -*- coding: utf-8; -*-
<%inherit file="/master/view.mako" />
<%namespace name="product_lookup" file="/products/lookup.mako" />

<%def name="page_content()">
  ${parent.page_content()}

  % if master.has_perm('ignore_product') and instance.status_code in (enum.PENDING_PRODUCT_STATUS_PENDING, enum.PENDING_PRODUCT_STATUS_READY):
      ${h.form(master.get_action_url('ignore_product', instance), ref='ignoreProductForm')}
      ${h.csrf_token(request)}
      ${h.end_form()}
  % endif

  % if master.has_perm('resolve_product') and instance.status_code in (enum.PENDING_PRODUCT_STATUS_PENDING, enum.PENDING_PRODUCT_STATUS_READY, enum.PENDING_PRODUCT_STATUS_IGNORED):
      <b-modal has-modal-card
               :active.sync="resolveProductShowDialog">
        <div class="modal-card">
          ${h.form(url('{}.resolve_product'.format(route_prefix), uuid=instance.uuid), ref='resolveProductForm')}
          ${h.csrf_token(request)}

          <header class="modal-card-head">
            <p class="modal-card-title">Resolve Product</p>
          </header>

          <section class="modal-card-body">
            <p class="block">
              If this product already exists, you can declare that by
              identifying the record below.
            </p>
            <p class="block">
              The app will take care of updating any Customer Orders
              etc.  as needed once you declare the match.
            </p>
            <b-field label="Pending Product">
              <span>${instance.full_description}</span>
            </b-field>
            <b-field label="Actual Product" expanded>
              <tailbone-product-lookup ref="productLookup"
                                       autocomplete-url="${url('products.autocomplete_special', key='with_key')}"
                                       :product="actualProduct"
                                       @selected="productSelected">
              </tailbone-product-lookup>
            </b-field>
            ${h.hidden('product_uuid', **{':value': 'resolveProductUUID'})}
          </section>

          <footer class="modal-card-foot">
            <b-button @click="resolveProductShowDialog = false">
              Cancel
            </b-button>
            <b-button type="is-primary"
                      :disabled="resolveProductSubmitDisabled"
                      @click="resolveProductSubmit()"
                      icon-pack="fas"
                      icon-left="object-ungroup">
              {{ resolveProductSubmitting ? "Working, please wait..." : "I declare these are the same" }}
            </b-button>
          </footer>
          ${h.end_form()}
        </div>
      </b-modal>
  % endif
</%def>

<%def name="render_vue_templates()">
  ${parent.render_vue_templates()}
  ${product_lookup.tailbone_product_lookup_template()}
</%def>

<%def name="modify_vue_vars()">
  ${parent.modify_vue_vars()}
  <script>

    % if master.has_perm('ignore_product') and instance.status_code in (enum.PENDING_PRODUCT_STATUS_PENDING, enum.PENDING_PRODUCT_STATUS_READY):

        ThisPage.methods.ignoreProductInit = function() {
            if (!confirm("Really ignore this product?\n\n"
                         + "This will leave it unresolved, but hidden via default filters.")) {
                return
            }
            this.$refs.ignoreProductForm.submit()
        }

    % endif

    % if master.has_perm('resolve_product') and instance.status_code in (enum.PENDING_PRODUCT_STATUS_PENDING, enum.PENDING_PRODUCT_STATUS_READY, enum.PENDING_PRODUCT_STATUS_IGNORED):

        ThisPageData.resolveProductShowDialog = false
        ThisPageData.resolveProductUUID = null
        ThisPageData.resolveProductSubmitting = false

        ThisPage.computed.resolveProductSubmitDisabled = function() {
            if (this.resolveProductSubmitting) {
                return true
            }
            if (!this.resolveProductUUID) {
                return true
            }
            return false
        }

        ThisPage.methods.resolveProductInit = function() {
            this.resolveProductUUID = null
            this.resolveProductShowDialog = true
            this.$nextTick(() => {
                this.$refs.productLookup.focus()
            })
        }

        ThisPage.methods.resolveProductSubmit = function() {
            this.resolveProductSubmitting = true
            this.$refs.resolveProductForm.submit()
        }

        ThisPageData.actualProduct = null

        ThisPage.methods.productSelected = function(product) {
           this.actualProduct = product
           this.resolveProductUUID = product ? product.uuid : null
        }

    % endif

  </script>
</%def>

<%def name="make_vue_components()">
  ${parent.make_vue_components()}
  ${product_lookup.tailbone_product_lookup_component()}
</%def>
