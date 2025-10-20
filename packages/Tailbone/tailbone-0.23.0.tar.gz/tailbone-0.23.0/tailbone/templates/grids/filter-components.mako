## -*- coding: utf-8; -*-

<%def name="make_grid_filter_components()">
  ${self.make_grid_filter_numeric_value_component()}
  ${self.make_grid_filter_date_value_component()}
  ${self.make_grid_filter_component()}
</%def>

<%def name="make_grid_filter_numeric_value_component()">
  <% request.register_component('grid-filter-numeric-value', 'GridFilterNumericValue') %>
  <script type="text/x-template" id="grid-filter-numeric-value-template">
    <div class="level">
      <div class="level-left">
        <div class="level-item">
          <b-input v-model="startValue"
                   ref="startValue"
                   @input="startValueChanged">
          </b-input>
        </div>
        <div v-show="wantsRange"
             class="level-item">
          and
        </div>
        <div v-show="wantsRange"
             class="level-item">
          <b-input v-model="endValue"
                   ref="endValue"
                   @input="endValueChanged">
          </b-input>
        </div>
      </div>
    </div>
  </script>
  <script>

    const GridFilterNumericValue = {
        template: '#grid-filter-numeric-value-template',
        props: {
            ${'modelValue' if request.use_oruga else 'value'}: String,
            wantsRange: Boolean,
        },
        data() {
            const value = this.${'modelValue' if request.use_oruga else 'value'}
            const {startValue, endValue} = this.parseValue(value)
            return {
                startValue,
                endValue,
            }
        },
        watch: {
            // when changing from e.g. 'equal' to 'between' filter verbs,
            // must proclaim new filter value, to reflect (lack of) range
            wantsRange(val) {
                if (val) {
                    this.$emit('input', this.startValue + '|' + this.endValue)
                } else {
                    this.$emit('input', this.startValue)
                }
            },

            ${'modelValue' if request.use_oruga else 'value'}(to, from) {
                const parsed = this.parseValue(to)
                this.startValue = parsed.startValue
                this.endValue = parsed.endValue
            },
        },
        methods: {
            focus() {
                this.$refs.startValue.focus()
            },
            startValueChanged(value) {
                if (this.wantsRange) {
                    value += '|' + this.endValue
                }
                this.$emit("${'update:modelValue' if request.use_oruga else 'input'}", value)
            },
            endValueChanged(value) {
                value = this.startValue + '|' + value
                this.$emit("${'update:modelValue' if request.use_oruga else 'input'}", value)
            },

            parseValue(value) {
                let startValue = null
                let endValue = null
                if (this.wantsRange) {
                    if (value.includes('|')) {
                        let values = value.split('|')
                        if (values.length == 2) {
                            startValue = values[0]
                            endValue = values[1]
                        } else {
                            startValue = value
                        }
                    } else {
                        startValue = value
                    }
                } else {
                    startValue = value
                }

                return {
                    startValue,
                    endValue,
                }
            },
        },
    }

    Vue.component('grid-filter-numeric-value', GridFilterNumericValue)

  </script>
</%def>

<%def name="make_grid_filter_date_value_component()">
  <% request.register_component('grid-filter-date-value', 'GridFilterDateValue') %>
  <script type="text/x-template" id="grid-filter-date-value-template">
    <div class="level">
      <div class="level-left">
        <div class="level-item">
          <tailbone-datepicker v-model="startDate"
                               ref="startDate"
                               @${'update:model-value' if request.use_oruga else 'input'}="startDateChanged">
          </tailbone-datepicker>
        </div>
        <div v-show="dateRange"
             class="level-item">
          and
        </div>
        <div v-show="dateRange"
             class="level-item">
          <tailbone-datepicker v-model="endDate"
                               ref="endDate"
                               @${'update:model-value' if request.use_oruga else 'input'}="endDateChanged">
          </tailbone-datepicker>
        </div>
      </div>
    </div>
  </script>
  <script>

    const GridFilterDateValue = {
        template: '#grid-filter-date-value-template',
        props: {
            ${'modelValue' if request.use_oruga else 'value'}: String,
            dateRange: Boolean,
        },
        data() {
            let startDate = null
            let endDate = null
            let value = this.${'modelValue' if request.use_oruga else 'value'}
            if (value) {

                if (this.dateRange) {
                    let values = value.split('|')
                    if (values.length == 2) {
                        startDate = this.parseDate(values[0])
                        endDate = this.parseDate(values[1])
                    } else {    // no end date specified?
                        startDate = this.parseDate(value)
                    }

                } else {        // not a range, so start date only
                    startDate = this.parseDate(value)
                }
            }

            return {
                startDate,
                endDate,
            }
        },
        methods: {
            focus() {
                this.$refs.startDate.focus()
            },
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
                if (value) {
                    // note, this assumes classic YYYY-MM-DD (i.e. ISO?) format
                    const parts = value.split('-')
                    return new Date(parts[0], parseInt(parts[1]) - 1, parts[2])
                }
            },
            startDateChanged(value) {
                value = this.formatDate(value)
                if (this.dateRange) {
                    value += '|' + this.formatDate(this.endDate)
                }
                this.$emit("${'update:modelValue' if request.use_oruga else 'input'}", value)
            },
            endDateChanged(value) {
                value = this.formatDate(this.startDate) + '|' + this.formatDate(value)
                this.$emit("${'update:modelValue' if request.use_oruga else 'input'}", value)
            },
        },
    }

    Vue.component('grid-filter-date-value', GridFilterDateValue)

  </script>
</%def>

<%def name="make_grid_filter_component()">
  <% request.register_component('grid-filter', 'GridFilter') %>
  <script type="text/x-template" id="grid-filter-template">
    <div class="filter"
         v-show="filter.visible"
         style="display: flex; gap: 0.5rem;">

        <div class="filter-fieldname">
          <b-button @click="filter.active = !filter.active"
                    icon-pack="fas"
                    :icon-left="filter.active ? 'check' : null">
            {{ filter.label }}
          </b-button>
        </div>

        <div v-show="filter.active"
             style="display: flex; gap: 0.5rem;">

          <b-select v-model="filter.verb"
                    @input="focusValue()"
                    class="filter-verb">
            <option v-for="verb in filter.verbs"
                    :key="verb"
                    :value="verb">
              {{ filter.verb_labels[verb] }}
            </option>
          </b-select>

          ## only one of the following "value input" elements will be rendered

          <grid-filter-date-value v-if="filter.data_type == 'date'"
                                  v-model="filter.value"
                                  v-show="valuedVerb()"
                                  :date-range="filter.verb == 'between'"
                                  ref="valueInput">
          </grid-filter-date-value>

          <b-select v-if="filter.data_type == 'choice'"
                    v-model="filter.value"
                    v-show="valuedVerb()"
                    ref="valueInput">
            <option v-for="choice in filter.choices"
                    :key="choice"
                    :value="choice">
              {{ filter.choice_labels[choice] || choice }}
            </option>
          </b-select>

          <grid-filter-numeric-value v-if="filter.data_type == 'number'"
                                    v-model="filter.value"
                                    v-show="valuedVerb()"
                                    :wants-range="filter.verb == 'between'"
                                    ref="valueInput">
          </grid-filter-numeric-value>

          <b-input v-if="filter.data_type == 'string' && !multiValuedVerb()"
                   v-model="filter.value"
                   v-show="valuedVerb()"
                   ref="valueInput">
          </b-input>

          <b-input v-if="filter.data_type == 'string' && multiValuedVerb()"
                   type="textarea"
                   v-model="filter.value"
                   v-show="valuedVerb()"
                   ref="valueInput">
          </b-input>

        </div>
    </div>
  </script>
  <script>

    const GridFilter = {
        template: '#grid-filter-template',
        props: {
            filter: Object
        },

        methods: {

            changeVerb() {
                // set focus to value input, "as quickly as we can"
                this.$nextTick(function() {
                    this.focusValue()
                })
            },

            valuedVerb() {
                /* this returns true if the filter's current verb should expose value input(s) */

                // if filter has no "valueless" verbs, then all verbs should expose value inputs
                if (!this.filter.valueless_verbs) {
                    return true
                }

                // if filter *does* have valueless verbs, check if "current" verb is valueless
                if (this.filter.valueless_verbs.includes(this.filter.verb)) {
                    return false
                }

                // current verb is *not* valueless
                return true
            },

            multiValuedVerb() {
                /* this returns true if the filter's current verb should expose a multi-value input */

                // if filter has no "multi-value" verbs then we safely assume false
                if (!this.filter.multiple_value_verbs) {
                    return false
                }

                // if filter *does* have multi-value verbs, see if "current" is one
                if (this.filter.multiple_value_verbs.includes(this.filter.verb)) {
                    return true
                }

                // current verb is not multi-value
                return false
            },

            focusValue: function() {
                this.$refs.valueInput.focus()
                // this.$refs.valueInput.select()
            }
        }
    }

    Vue.component('grid-filter', GridFilter)

  </script>
</%def>
