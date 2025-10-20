## -*- coding: utf-8; -*-
<%inherit file="/page.mako" />

<%def name="title()">Generate Feature</%def>

<%def name="content_title()"></%def>

<%def name="page_content()">

  <b-field horizontal label="App Prefix"
           message="Unique naming prefix for the app.">
    <b-input v-model="app.app_prefix"
             @input="appPrefixChanged">
    </b-input>
  </b-field>

  <b-field horizontal label="App CapPrefix"
           message="Unique naming prefix for the app, in CapWords style.">
    <b-input v-model="app.app_cap_prefix"></b-input>
  </b-field>

  <b-field horizontal label="Feature Type">
    <b-select v-model="featureType">
      <option value="new-report">New Report</option>
      <option value="new-table">New Table</option>
    </b-select>
  </b-field>

  <div v-if="featureType == 'new-table'">
    ${h.form(request.current_route_url(), ref='new-table-form')}
    ${h.csrf_token(request)}
    ${h.hidden('feature_type', value='new-table')}
    ${h.hidden('app_prefix', **{'v-model': 'app.app_prefix'})}
    ${h.hidden('app_cap_prefix', **{'v-model': 'app.app_cap_prefix'})}
    ${h.hidden('columns', **{':value': 'JSON.stringify(new_table.columns)'})}

    <br />
    <div class="card">
      <header class="card-header">
        <p class="card-header-title">New Table</p>
      </header>
      <div class="card-content">
        <div class="content">

          <b-field horizontal label="Table Name"
                   :message="`Name for the table within the DB.  With prefix this becomes: ${'$'}{app.app_prefix}_${'$'}{new_table.table_name}`">
            <b-input name="table_name"
                     v-model="new_table.table_name"
                     @input="tableNameChanged">
            </b-input>
          </b-field>

          <b-field horizontal label="Model Name"
                   :message="`Model name for the table, in CapWords style.  With prefix this becomes: ${'$'}{app.app_cap_prefix}${'$'}{new_table.model_name}`">
            <b-input name="model_name" v-model="new_table.model_name"></b-input>
          </b-field>

          <b-field horizontal label="Model Title"
                   message="Human-friendly singular model title.">
            <b-input name="model_title" v-model="new_table.model_title"></b-input>
          </b-field>

          <b-field horizontal label="Plural Model Title"
                   message="Human-friendly plural model title.">
            <b-input name="model_title_plural" v-model="new_table.model_title_plural"></b-input>
          </b-field>

          <b-field horizontal label="Description"
                   message="Description of what a record in this table represents.">
            <b-input name="description" v-model="new_table.description"></b-input>
          </b-field>

          <b-field horizontal label="Versioned"
                   message="Whether to record version data for this table.">
            <b-checkbox name="versioned"
                        v-model="new_table.versioned"
                        native-value="true">
              {{ new_table.versioned }}
            </b-checkbox>
          </b-field>

          <b-field horizontal label="Columns">
            <div class="control">

              <div class="level">
                <div class="level-left">
                  <div class="level-item">
                    <b-button type="is-primary"
                              icon-pack="fas"
                              icon-left="plus"
                              @click="addColumn()">
                      New Column
                    </b-button>
                  </div>
                </div>
                <div class="level-right">
                  <div class="level-item">
                    <b-button type="is-danger"
                              icon-pack="fas"
                              icon-left="trash"
                              @click="new_table.columns = []"
                              :disabled="!new_table.columns.length">
                      Delete All
                    </b-button>
                  </div>
                </div>
              </div>

              <${b}-table
                 :data="new_table.columns">

                <${b}-table-column field="name"
                                label="Name"
                                v-slot="props">
                  {{ props.row.name }}
                </${b}-table-column>

                <${b}-table-column field="data_type"
                                label="Data Type"
                                v-slot="props">
                  {{ props.row.data_type }}
                </${b}-table-column>

                <${b}-table-column field="nullable"
                                label="Nullable"
                                v-slot="props">
                  {{ props.row.nullable }}
                </${b}-table-column>

                <${b}-table-column field="description"
                                label="Description"
                                v-slot="props">
                  {{ props.row.description }}
                </${b}-table-column>

                <${b}-table-column field="actions"
                                label="Actions"
                                v-slot="props">
                  <a href="#" class="grid-action"
                     @click.prevent="editColumnRow(props)">
                    % if request.use_oruga:
                        <o-icon icon="edit" />
                    % else:
                        <i class="fas fa-edit"></i>
                    % endif
                    Edit
                  </a>
                  &nbsp;

                  <a href="#" class="grid-action has-text-danger"
                     @click.prevent="deleteColumn(props.index)">
                    % if request.use_oruga:
                        <o-icon icon="trash" />
                    % else:
                        <i class="fas fa-trash"></i>
                    % endif
                    Delete
                  </a>
                  &nbsp;
                </${b}-table-column>

              </${b}-table>

              <${b}-modal has-modal-card
                       % if request.use_oruga:
                       v-model:active="showingEditColumn"
                       % else:
                       :active.sync="showingEditColumn"
                       % endif
                       >
                <div class="modal-card">

                  <header class="modal-card-head">
                    <p class="modal-card-title">Edit Column</p>
                  </header>

                  <section class="modal-card-body">

                    <b-field label="Name">
                      <b-input v-model="editingColumnName"
                               expanded />
                    </b-field>

                    <b-field label="Data Type">
                      <b-input v-model="editingColumnDataType"
                               expanded />
                    </b-field>

                    <b-field label="Nullable">
                      <b-checkbox v-model="editingColumnNullable"
                                  native-value="true">
                        {{ editingColumnNullable }}
                      </b-checkbox>
                    </b-field>

                    <b-field label="Description">
                      <b-input v-model="editingColumnDescription"
                               expanded />
                    </b-field>

                  </section>

                  <footer class="modal-card-foot">
                    <b-button @click="showingEditColumn = false">
                      Cancel
                    </b-button>
                    <b-button type="is-primary"
                              @click="saveColumn()">
                      Save
                    </b-button>
                  </footer>
                </div>
              </${b}-modal>

            </div>
          </b-field>

        </div>
      </div>
    </div>

    ${h.end_form()}
  </div>

  <div v-if="featureType == 'new-report'">
    ${h.form(request.current_route_url(), ref='new-report-form')}
    ${h.csrf_token(request)}
    ${h.hidden('feature_type', value='new-report')}
    ${h.hidden('app_prefix', **{'v-model': 'app.app_prefix'})}
    ${h.hidden('app_cap_prefix', **{'v-model': 'app.app_cap_prefix'})}

    <br />
    <div class="card">
      <header class="card-header">
        <p class="card-header-title">New Report</p>
      </header>
      <div class="card-content">
        <div class="content">

          <b-field horizontal label="Name"
                   message="Human-friendly name for the report.">
            <b-input name="name" v-model="new_report.name"></b-input>
          </b-field>

          <b-field horizontal label="Description"
                   message="Description of the report.">
            <b-input name="description" v-model="new_report.description"></b-input>
          </b-field>

        </div>
      </div>
    </div>

    ${h.end_form()}
  </div>

  <br />
  <div class="buttons" style="padding-left: 8rem;">
    <once-button type="is-primary"
                 @click="submitFeatureForm()"
                 text="Generate Feature">
    </once-button>
  </div>

  <div class="card"
       v-if="resultGenerated">
    <header class="card-header">
      <p class="card-header-title">
        <a name="instructions" href="#instructions">Please follow these instructions carefully.</a>
      </p>
    </header>
    <div class="card-content">
      <div class="content result rendered-markdown">${rendered_result or ""|n}</div>
    </div>
  </div>

</%def>

<%def name="modify_vue_vars()">
  ${parent.modify_vue_vars()}
  <script>

    ThisPageData.featureType = ${json.dumps(feature_type)|n}
    ThisPageData.resultGenerated = ${json.dumps(bool(result))|n}

    % if result:
    ThisPage.mounted = function() {
        location.href = '#instructions'
    }
    % endif

    ThisPageData.app = {
        <% dform = app_form.make_deform_form() %>
        % for field in dform:
            ${field.name}: ${app_form.get_vuejs_model_value(field)|n},
        % endfor
    }

    % for key, form in feature_forms.items():
        <% safekey = key.replace('-', '_') %>
        ThisPageData.${safekey} = {
            <% dform = feature_forms[key].make_deform_form() %>
            % for field in dform:
                ${field.name}: ${feature_forms[key].get_vuejs_model_value(field)|n},
            % endfor
        }
    % endfor

    ThisPage.methods.appPrefixChanged = function(prefix) {
        let words = prefix.split('_')
        let capitalized = []
        words.forEach(word => {
            capitalized.push(word[0].toUpperCase() + word.substr(1))
        })

        this.app.app_cap_prefix = capitalized.join('')
    }

    ThisPage.methods.tableNameChanged = function(name) {
        let words = name.split('_')
        let capitalized = []
        words.forEach(word => {
            capitalized.push(word[0].toUpperCase() + word.substr(1))
        })

        this.new_table.model_name = capitalized.join('')
        this.new_table.model_title = capitalized.join(' ')
        this.new_table.model_title_plural = capitalized.join(' ') + 's'
        this.new_table.description = `Represents a ${'$'}{this.new_table.model_title}.`
    }

    ThisPageData.showingEditColumn = false
    ThisPageData.editingColumn = null
    ThisPageData.editingColumnIndex = null
    ThisPageData.editingColumnName = null
    ThisPageData.editingColumnDataType = null
    ThisPageData.editingColumnNullable = null
    ThisPageData.editingColumnDescription = null

    ThisPage.methods.addColumn = function(column) {
        this.editingColumn = null
        this.editingColumnIndex = null
        this.editingColumnName = null
        this.editingColumnDataType = null
        this.editingColumnNullable = true
        this.editingColumnDescription = null
        this.showingEditColumn = true
    }

    ThisPage.methods.editColumnRow = function(props) {
        const column = props.row
        this.editingColumn = column
        this.editingColumnIndex = props.index
        this.editingColumnName = column.name
        this.editingColumnDataType = column.data_type
        this.editingColumnNullable = column.nullable
        this.editingColumnDescription = column.description
        this.showingEditColumn = true
    }

    ThisPage.methods.saveColumn = function() {
        if (this.editingColumn) {
            column = this.new_table.columns[this.editingColumnIndex]
        } else {
            column = {}
            this.new_table.columns.push(column)
        }
        column.name = this.editingColumnName
        column.data_type = this.editingColumnDataType
        column.nullable = this.editingColumnNullable
        column.description = this.editingColumnDescription
        this.showingEditColumn = false
    }

    ThisPage.methods.deleteColumn = function(index) {
        this.new_table.columns.splice(index, 1)
    }

    ThisPage.methods.submitFeatureForm = function() {
        let form = this.$refs[this.featureType + '-form']
        // TODO: why do we have to set this?  hidden field value is blank?!
        form['feature_type'].value = this.featureType
        form.submit()
    }

  </script>
</%def>
