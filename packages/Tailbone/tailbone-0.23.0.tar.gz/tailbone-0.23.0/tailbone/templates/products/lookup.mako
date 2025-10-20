## -*- coding: utf-8; -*-

<%def name="tailbone_product_lookup_template()">
  <script type="text/x-template" id="tailbone-product-lookup-template">
    <div style="width: 100%;">
      <div style="display: flex; gap: 0.5rem;">

        <b-field :style="{'flex-grow': product ? '0' : '1'}">
          <${b}-autocomplete v-if="!product"
                             ref="productAutocomplete"
                             v-model="autocompleteValue"
                             expanded
                             placeholder="Enter UPC or brand, description etc."
                             :data="autocompleteOptions"
                             % if request.use_oruga:
                                 @input="getAutocompleteOptions"
                                 :formatter="option => option.label"
                             % else:
                                 @typing="getAutocompleteOptions"
                                 :custom-formatter="option => option.label"
                                 field="value"
                             % endif
                             @select="autocompleteSelected"
                             style="width: 100%;">
          </${b}-autocomplete>
          <b-button v-if="product"
                    @click="clearSelection(true)">
            {{ product.full_description }}
          </b-button>
        </b-field>

        <b-button type="is-primary"
                  v-if="!product"
                  @click="lookupInit()"
                  icon-pack="fas"
                  icon-left="search">
          Full Lookup
        </b-button>

        <b-button v-if="product"
                  type="is-primary"
                  tag="a" target="_blank"
                  :href="product.url"
                  :disabled="!product.url"
                  icon-pack="fas"
                  icon-left="external-link-alt">
          View Product
        </b-button>

      </div>

      <b-modal :active.sync="lookupShowDialog">
        <div class="card">
          <div class="card-content">

            <b-field grouped>

              <b-input v-model="searchTerm" 
                       ref="searchTermInput"
                       % if not request.use_oruga:
                           @keydown.native="searchTermInputKeydown"
                       % endif
                       />

              <b-button class="control"
                        type="is-primary"
                        @click="performSearch()">
                Search
              </b-button>

              <b-checkbox v-model="searchProductKey"
                          native-value="true">
                ${request.rattail_config.product_key_title()}
              </b-checkbox>

              <b-checkbox v-model="searchVendorItemCode"
                          native-value="true">
                Vendor Code
              </b-checkbox>

              <b-checkbox v-model="searchAlternateCode"
                          native-value="true">
                Alt Code
              </b-checkbox>

              <b-checkbox v-model="searchProductBrand"
                          native-value="true">
                Brand
              </b-checkbox>

              <b-checkbox v-model="searchProductDescription"
                          native-value="true">
                Description
              </b-checkbox>

            </b-field>

            <${b}-table :data="searchResults"
                        narrowed
                        % if request.use_oruga:
                            v-model:selected="searchResultSelected"
                        % else:
                            :selected.sync="searchResultSelected"
                            icon-pack="fas"
                        % endif
                        :loading="searchResultsLoading">

              <${b}-table-column label="${request.rattail_config.product_key_title()}"
                              field="product_key"
                              v-slot="props">
                {{ props.row.product_key }}
              </${b}-table-column>

              <${b}-table-column label="Brand"
                              field="brand_name"
                              v-slot="props">
                {{ props.row.brand_name }}
              </${b}-table-column>

              <${b}-table-column label="Description"
                              field="description"
                              v-slot="props">
                <span :class="{organic: props.row.organic}">
                  {{ props.row.description }}
                  {{ props.row.size }}
                </span>
              </${b}-table-column>

              <${b}-table-column label="Unit Price"
                              field="unit_price"
                              v-slot="props">
                {{ props.row.unit_price_display }}
              </${b}-table-column>

              <${b}-table-column label="Sale Price"
                              field="sale_price"
                              v-slot="props">
                <span class="has-background-warning">
                  {{ props.row.sale_price_display }}
                </span>
              </${b}-table-column>

              <${b}-table-column label="Sale Ends"
                              field="sale_ends"
                              v-slot="props">
                <span class="has-background-warning">
                  {{ props.row.sale_ends_display }}
                </span>
              </${b}-table-column>

              <${b}-table-column label="Department"
                              field="department_name"
                              v-slot="props">
                {{ props.row.department_name }}
              </${b}-table-column>

              <${b}-table-column label="Vendor"
                              field="vendor_name"
                              v-slot="props">
                {{ props.row.vendor_name }}
              </${b}-table-column>

              <${b}-table-column label="Actions"
                              v-slot="props">
                <a :href="props.row.url"
                   % if not request.use_oruga:
                       class="grid-action"
                   % endif
                   target="_blank">
                  % if request.use_oruga:
                      <span class="icon-text">
                        <o-icon icon="external-link-alt" />
                        <span>View</span>
                      </span>
                  % else:
                      <i class="fas fa-external-link-alt"></i>
                      View
                  % endif
                </a>
              </${b}-table-column>

              <template #empty>
                <div class="content has-text-grey has-text-centered">
                  <p>
                    <b-icon
                      pack="fas"
                      icon="sad-tear"
                      size="is-large">
                    </b-icon>
                  </p>
                  <p>Nothing here.</p>
                </div>
              </template>
            </${b}-table>

            <br />
            <div class="level">
              <div class="level-left">
                <div class="level-item buttons">
                  <b-button @click="cancelDialog()">
                    Cancel
                  </b-button>
                  <b-button type="is-primary"
                            @click="selectResult()"
                            :disabled="!searchResultSelected">
                    Choose Selected
                  </b-button>
                </div>
              </div>
              <div class="level-right">
                <div class="level-item">
                  <span v-if="searchResultsElided"
                        class="has-text-danger">
                    {{ searchResultsElided }} results are not shown
                  </span>
                </div>
              </div>
            </div>

          </div>
        </div>
      </b-modal>

    </div>
  </script>
</%def>

<%def name="tailbone_product_lookup_component()">
  <script type="text/javascript">

    const TailboneProductLookup = {
        template: '#tailbone-product-lookup-template',
        props: {
            product: {
                type: Object,
            },
            autocompleteUrl: {
                type: String,
                default: '${url('products.autocomplete')}',
            },
        },
        data() {
            return {
                autocompleteValue: '',
                autocompleteOptions: [],

                lookupShowDialog: false,

                searchTerm: null,
                searchTermLastUsed: null,
                % if request.use_oruga:
                    searchTermInputElement: null,
                % endif

                searchProductKey: true,
                searchVendorItemCode: true,
                searchProductBrand: true,
                searchProductDescription: true,
                searchAlternateCode: true,

                searchResults: [],
                searchResultsLoading: false,
                searchResultsElided: 0,
                searchResultSelected: null,
            }
        },

        % if request.use_oruga:

            mounted() {
                this.searchTermInputElement = this.$refs.searchTermInput.$el.querySelector('input')
                this.searchTermInputElement.addEventListener('keydown', this.searchTermInputKeydown)
            },

            beforeDestroy() {
                this.searchTermInputElement.removeEventListener('keydown', this.searchTermInputKeydown)
            },

        % endif

        methods: {

            focus() {
                if (!this.product) {
                    this.$refs.productAutocomplete.focus()
                }
            },

            clearSelection(focus) {

                // clear data
                this.autocompleteValue = ''
                this.$emit('selected', null)

                // maybe set focus to our (autocomplete) component
                if (focus) {
                    this.$nextTick(() => {
                        this.focus()
                    })
                }
            },

            ## TODO: add debounce for oruga?
            % if request.use_oruga:
            getAutocompleteOptions(entry) {
            % else:
            getAutocompleteOptions: debounce(function (entry) {
            % endif

                // since the `@typing` event from buefy component does not
                // "self-regulate" in any way, we a) use `debounce` above,
                // but also b) skip the search unless we have at least 3
                // characters of input from user
                if (entry.length < 3) {
                    this.data = []
                    return
                }

                // and perform the search
                this.$http.get(this.autocompleteUrl + '?term=' + encodeURIComponent(entry))
                    .then(({ data }) => {
                        this.autocompleteOptions = data
                    }).catch((error) => {
                        this.autocompleteOptions = []
                        throw error
                    })
            % if request.use_oruga:
            },
            % else:
            }),
            % endif

            autocompleteSelected(option) {
                this.$emit('selected', {
                    uuid: option.value,
                    full_description: option.label,
                    url: option.url,
                    image_url: option.image_url,
                })
            },

            lookupInit() {
                this.searchResultSelected = null
                this.lookupShowDialog = true

                this.$nextTick(() => {

                    this.searchTerm = this.autocompleteValue
                    if (this.searchTerm != this.searchTermLastUsed) {
                        this.searchTermLastUsed = null
                        this.performSearch()
                    }

                    this.$refs.searchTermInput.focus()
                })
            },

            searchTermInputKeydown(event) {
                if (event.which == 13) {
                    this.performSearch()
                }
            },

            performSearch() {
                if (this.searchResultsLoading) {
                    return
                }

                if (!this.searchTerm || !this.searchTerm.length) {
                    this.$refs.searchTermInput.focus()
                    return
                }

                this.searchResultsLoading = true
                this.searchResultSelected = null

                let url = '${url('products.search')}'
                let params = {
                    term: this.searchTerm,
                    search_product_key: this.searchProductKey,
                    search_vendor_code: this.searchVendorItemCode,
                    search_brand_name: this.searchProductBrand,
                    search_description: this.searchProductDescription,
                    search_alt_code: this.searchAlternateCode,
                }

                this.$http.get(url, {params: params}).then((response) => {
                    this.searchTermLastUsed = params.term
                    this.searchResults = response.data.results
                    this.searchResultsElided = response.data.elided
                    this.searchResultsLoading = false
                })
            },

            selectResult() {
                this.lookupShowDialog = false
                this.$emit('selected', this.searchResultSelected)
            },

            cancelDialog() {
                this.searchResultSelected = null
                this.lookupShowDialog = false
            },
        },
    }

    Vue.component('tailbone-product-lookup', TailboneProductLookup)
    <% request.register_component('tailbone-product-lookup', 'TailboneProductLookup') %>

  </script>
</%def>
