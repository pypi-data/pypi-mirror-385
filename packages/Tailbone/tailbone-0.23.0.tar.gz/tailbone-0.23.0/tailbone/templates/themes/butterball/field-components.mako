## -*- coding: utf-8; -*-

<%def name="make_field_components()">
  ${self.make_numeric_input_component()}
  ${self.make_tailbone_autocomplete_component()}
  ${self.make_tailbone_datepicker_component()}
  ${self.make_tailbone_timepicker_component()}
</%def>

<%def name="make_numeric_input_component()">
  <% request.register_component('numeric-input', 'NumericInput') %>
  ${h.javascript_link(request.static_url('tailbone:static/js/numeric.js') + f'?ver={tailbone.__version__}')}
  <script type="text/x-template" id="numeric-input-template">
    <o-input v-model="orugaValue"
             @update:model-value="orugaValueUpdated"
             ref="input"
             :disabled="disabled"
             :icon="icon"
             :name="name"
             :placeholder="placeholder"
             :size="size"
             />
  </script>
  <script>

    const NumericInput = {
        template: '#numeric-input-template',

        props: {
            modelValue: [Number, String],
            allowEnter: Boolean,
            disabled: Boolean,
            icon: String,
            iconPack: String,   // ignored
            name: String,
            placeholder: String,
            size: String,
        },

        data() {
            return {
                orugaValue: this.modelValue,
                inputElement: null,
            }
        },

        watch: {
            modelValue(to, from) {
                this.orugaValue = to
            },
        },

        mounted() {
            this.inputElement = this.$refs.input.$el.querySelector('input')
            this.inputElement.addEventListener('keydown', this.keyDown)
        },

        beforeDestroy() {
            this.inputElement.removeEventListener('keydown', this.keyDown)
        },

        methods: {

            focus() {
                this.$refs.input.focus()
            },

            keyDown(event) {
                // by default we only allow numeric keys, and general navigation
                // keys, but we might also allow Enter key
                if (!key_modifies(event) && !key_allowed(event)) {
                    if (!this.allowEnter || event.which != 13) {
                        event.preventDefault()
                    }
                }
            },

            orugaValueUpdated(value) {
                this.$emit('update:modelValue', value)
                this.$emit('input', value)
            },

            select() {
                this.$el.children[0].select()
            },
        },
    }

  </script>
</%def>

<%def name="make_tailbone_autocomplete_component()">
  <% request.register_component('tailbone-autocomplete', 'TailboneAutocomplete') %>
  <script type="text/x-template" id="tailbone-autocomplete-template">
    <div>

      <o-button v-if="modelValue"
                style="width: 100%; justify-content: left;"
                @click="clearSelection(true)"
                expanded>
        {{ internalLabel }} (click to change)
      </o-button>

      <o-autocomplete ref="autocompletex"
                      v-show="!modelValue"
                      v-model="orugaValue"
                      :placeholder="placeholder"
                      :data="filteredData"
                      :field="field"
                      :formatter="customFormatter"
                      @input="inputChanged"
                      @select="optionSelected"
                      keep-first
                      open-on-focus
                      :expanded="expanded"
                      :clearable="clearable"
                      :clear-on-select="clearOnSelect">
        <template #default="{ option }">
          {{ option.label }}
        </template>
      </o-autocomplete>

      <input type="hidden" :name="name" :value="modelValue" />
    </div>
  </script>
  <script>

    const TailboneAutocomplete = {
        template: '#tailbone-autocomplete-template',

        props: {

            // this is the "input" field name essentially.  primarily
            // is useful for "traditional" tailbone forms; it normally
            // is not used otherwise.  it is passed as-is to the oruga
            // autocomplete component `name` prop
            name: String,

            // static data set; used when serviceUrl is not provided
            data: Array,

            // the url from which search results are to be obtained.  the
            // url should expect a GET request with a query string with a
            // single `term` parameter, and return results as a JSON array
            // containing objects with `value` and `label` properties.
            serviceUrl: String,

            // callers do not specify this directly but rather by way of
            // the `v-model` directive.  this component will emit `input`
            // events when the value changes
            modelValue: String,

            // callers may set an initial label if needed.  this is useful
            // in cases where the autocomplete needs to "already have a
            // value" on page load.  for instance when a user fills out
            // the autocomplete field, but leaves other required fields
            // blank and submits the form; page will re-load showing
            // errors but the autocomplete field should remain "set" -
            // normally it is only given a "value" (e.g. uuid) but this
            // allows for the "label" to display correctly as well
            initialLabel: String,

            // while the `initialLabel` above is useful for setting the
            // *initial* label (of course), it cannot be used to
            // arbitrarily update the label during the component's life.
            // if you do need to *update* the label after initial page
            // load, then you should set `assignedLabel` instead.  one
            // place this happens is in /custorders/create page, where
            // product autocomplete shows some results, and user clicks
            // one, but then handler logic can forcibly "swap" the
            // selection, causing *different* product data to come back
            // from the server, and autocomplete label should be updated
            // to match.  this feels a bit awkward still but does work..
            assignedLabel: String,

            // simple placeholder text for the input box
            placeholder: String,

            // these are passed as-is to <o-autocomplete>
            clearable: Boolean,
            clearOnSelect: Boolean,
            customFormatter: null,
            expanded: Boolean,
            field: String,
        },

        data() {

            const internalLabel = this.assignedLabel || this.initialLabel

            // we want to track the "currently selected option" - which
            // should normally be `null` to begin with, unless we were
            // given a value, in which case we use `initialLabel` to
            // complete the option
            let selected = null
            if (this.modelValue) {
                selected = {
                    value: this.modelValue,
                    label: internalLabel,
                }
            }

            return {

                // this contains the search results; its contents may
                // change over time as new searches happen.  the
                // "currently selected option" should be one of these,
                // unless it is null
                fetchedData: [],

                // this tracks our "currently selected option" - per above
                selected,

                // since we are wrapping a component which also makes
                // use of the "value" paradigm, we must separate the
                // concerns.  so we use our own `modelValue` prop to
                // interact with the caller, but then we use this
                // `orugaValue` data point to communicate with the
                // oruga autocomplete component.  note that
                // `this.modelValue` will always be either a uuid or
                // null, whereas `this.orugaValue` may be raw text as
                // entered by the user.
                // orugaValue: this.modelValue,
                orugaValue: null,

                // this stores the "internal" label for the button
                internalLabel,
            }
        },

        computed: {

            filteredData() {

                // do not filter if data comes from backend
                if (this.serviceUrl) {
                    return this.fetchedData
                }

                if (!this.orugaValue || !this.orugaValue.length) {
                    return this.data
                }

                const terms = []
                for (let term of this.orugaValue.toLowerCase().split(' ')) {
                    term = term.trim()
                    if (term) {
                        terms.push(term)
                    }
                }
                if (!terms.length) {
                    return this.data
                }

                // all terms must match
                return this.data.filter((option) => {
                    const label = option.label.toLowerCase()
                    for (const term of terms) {
                        if (label.indexOf(term) < 0) {
                            return false
                        }
                    }
                    return true
                })
            },
        },

        watch: {

            assignedLabel(to, from) {
                // update button label when caller changes it
                this.internalLabel = to
            },
        },

        methods: {

            inputChanged(entry) {
                if (this.serviceUrl) {
                    this.getAsyncData(entry)
                }
            },

            // fetch new search results from the server.  this is
            // invoked via the `@input` event from oruga autocomplete
            // component.
            getAsyncData(entry) {

                // since the `@input` event from oruga component does
                // not "self-regulate" in any way (?), we skip the
                // search unless we have at least 3 characters of
                // input from user
                if (entry.length < 3) {
                    this.fetchedData = []
                    return
                }

                // and perform the search
                this.$http.get(this.serviceUrl + '?term=' + encodeURIComponent(entry))
                    .then(({ data }) => {
                        this.fetchedData = data
                    })
                    .catch((error) => {
                        this.fetchedData = []
                        throw error
                    })
            },

            // this method is invoked via the `@select` event of the
            // oruga autocomplete component.  the `option` received
            // will be one of:
            // - object with (at least) `value` and `label` keys
            // - simple string (e.g. when data set is static)
            // - null
            optionSelected(option) {

                this.selected = option
                this.internalLabel = option?.label || option

                // reset the internal value for oruga autocomplete
                // component.  note that this value will normally hold
                // either the raw text entered by the user, or a uuid.
                // we will not be needing either of those b/c they are
                // not visible to user once selection is made, and if
                // the selection is cleared we want user to start over
                // anyway
                this.orugaValue = null
                this.fetchedData = []

                // here is where we alert callers to the new value
                if (option) {
                    this.$emit('newLabel', option.label)
                }
                const value = option?.[this.field || 'value'] || option
                this.$emit('update:modelValue', value)
                // this.$emit('select', option)
                // this.$emit('input', value)
            },

##             // set selection to the given option, which should a simple
##             // object with (at least) `value` and `label` properties
##             setSelection(option) {
##                 this.$refs.autocomplete.setSelected(option)
##             },

            // clear the field of any value, i.e. set the "currently
            // selected option" to null.  this is invoked when you click
            // the button, which is visible while the field has a value.
            // but callers can invoke it directly as well.
            clearSelection(focus) {

                this.$emit('update:modelValue', null)
                this.$emit('input', null)
                this.$emit('newLabel', null)
                this.internalLabel = null
                this.selected = null
                this.orugaValue = null

##                 // clear selection for the oruga autocomplete component
##                 this.$refs.autocomplete.setSelected(null)

                // maybe set focus to our (autocomplete) component
                if (focus) {
                    this.$nextTick(function() {
                        this.focus()
                    })
                }
            },

            // nb. this used to be relevant but now is here only for sake
            // of backward-compatibility (for callers)
            getDisplayText() {
                return this.internalLabel
            },

            // set focus to this component, which will just set focus
            // to the oruga autocomplete component
            focus() {
                // TODO: why is this ref null?!
                if (this.$refs.autocompletex) {
                    this.$refs.autocompletex.focus()
                }
            },

            // returns the "raw" user input from the underlying oruga
            // autocomplete component
            getUserInput() {
                return this.orugaValue
            },
        },
    }

  </script>
</%def>

<%def name="make_tailbone_datepicker_component()">
  <% request.register_component('tailbone-datepicker', 'TailboneDatepicker') %>
  <script type="text/x-template" id="tailbone-datepicker-template">
    <o-datepicker placeholder="Click to select ..."
                  icon="calendar-alt"
                  :date-formatter="formatDate"
                  :date-parser="parseDate"
                  v-model="orugaValue"
                  @update:model-value="orugaValueUpdated"
                  :disabled="disabled"
                  ref="trueDatePicker">
    </o-datepicker>
  </script>
  <script>

    const TailboneDatepicker = {
        template: '#tailbone-datepicker-template',

        props: {
            modelValue: [Date, String],
            disabled: Boolean,
        },

        data() {
            return {
                orugaValue: this.parseDate(this.modelValue),
            }
        },

        watch: {
            modelValue(to, from) {
                this.orugaValue = this.parseDate(to)
            },
        },

        methods: {

            formatDate(date) {
                if (date === null) {
                    return null
                }
                if (typeof(date) == 'string') {
                    return date
                }
                // just need to convert to simple ISO date format here, seems
                // like there should be a more obvious way to do that?
                var year = date.getFullYear()
                var month = date.getMonth() + 1
                var day = date.getDate()
                month = month < 10 ? '0' + month : month
                day = day < 10 ? '0' + day : day
                return year + '-' + month + '-' + day
            },

            parseDate(value) {
                if (typeof(value) == 'object') {
                    // nb. we are assuming it is a Date here
                    return value
                }
                if (value) {
                    // note, this assumes classic YYYY-MM-DD (i.e. ISO?) format
                    const parts = value.split('-')
                    return new Date(parts[0], parseInt(parts[1]) - 1, parts[2])
                }
                return null
            },

            orugaValueUpdated(date) {
                this.$emit('update:modelValue', date)
            },

            focus() {
                this.$refs.trueDatePicker.focus()
            },
        },
    }

  </script>
</%def>

<%def name="make_tailbone_timepicker_component()">
  <% request.register_component('tailbone-timepicker', 'TailboneTimepicker') %>
  <script type="text/x-template" id="tailbone-timepicker-template">
    <o-timepicker :name="name"
                  v-model="orugaValue"
                  @update:model-value="orugaValueUpdated"
                  placeholder="Click to select ..."
                  icon="clock"
                  hour-format="12"
                  :time-formatter="formatTime" />
  </script>
  <script>

    const TailboneTimepicker = {
        template: '#tailbone-timepicker-template',

        props: {
            modelValue: [Date, String],
            name: String,
        },

        data() {
            return {
                orugaValue: this.parseTime(this.modelValue),
            }
        },

        watch: {
            modelValue(to, from) {
                this.orugaValue = this.parseTime(to)
            },
        },

        methods: {

            formatTime(value) {
                if (!value) {
                    return null
                }

                return value.toLocaleTimeString('en-US')
            },

            parseTime(value) {
                if (!value) {
                    return value
                }

                if (value.getHours) {
                    return value
                }

                let found = value.match(/^(\d\d):(\d\d):\d\d$/)
                if (found) {
                    return new Date(null, null, null,
                                    parseInt(found[1]), parseInt(found[2]))
                }
            },

            orugaValueUpdated(value) {
                this.$emit('update:modelValue', value)
            },
        },
    }

  </script>
</%def>
