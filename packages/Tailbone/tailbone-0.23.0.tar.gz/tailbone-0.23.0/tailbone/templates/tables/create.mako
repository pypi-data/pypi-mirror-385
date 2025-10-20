## -*- coding: utf-8; -*-
<%inherit file="/master/create.mako" />

<%def name="extra_styles()">
  ${parent.extra_styles()}
  <style type="text/css">
    .label {
        white-space: nowrap;
    }
  </style>
</%def>

<%def name="render_this_page()">

  ## scroll target used when navigating prev/next
  <div ref="showme"></div>

  % if not alembic_current_head:
      <b-notification type="is-warning"
                      :closable="false">
        <p class="block">
          DB is not up to date!  There are
          ${h.link_to("pending migrations", url('{}.migrations'.format(route_prefix)))}.
        </p>
        <p class="block">
          (This will be a problem if you wish to auto-generate a migration for a new table.)
        </p>
      </b-notification>
  % endif

  <b-steps v-model="activeStep"
           animated
           rounded
           :has-navigation="false"
           vertical
           icon-pack="fas">

    <b-step-item step="1"
                 value="enter-details"
                 label="Enter Details"
                 clickable>
      <h3 class="is-size-3 block">
        Enter Details
      </h3>

      <b-field label="Schema Branch"
               message="Leave this set to your custom app branch, unless you know what you're doing.">
        <b-select v-model="alembicBranch"
                  @input="dirty = true">
          <option v-for="branch in alembicBranchOptions"
                  :key="branch"
                  :value="branch">
            {{ branch }}
          </option>
        </b-select>
      </b-field>

      <b-field grouped>

        <b-field label="Table Name"
                 message="Should be singular in nature, i.e. 'widget' not 'widgets'">
          <b-input v-model="tableName"
                   @input="dirty = true">
          </b-input>
        </b-field>

        <b-field label="Model/Class Name"
                 message="Should be singular in nature, i.e. 'Widget' not 'Widgets'">
          <b-input v-model="tableModelName"
                   @input="dirty = true">
          </b-input>
        </b-field>

      </b-field>

      <b-field grouped>

        <b-field label="Model Title"
                 message="Human-friendly singular model title.">
          <b-input v-model="tableModelTitle"
                   @input="dirty = true">
          </b-input>
        </b-field>

        <b-field label="Model Title Plural"
                 message="Human-friendly plural model title.">
          <b-input v-model="tableModelTitlePlural"
                   @input="dirty = true">
          </b-input>
        </b-field>

      </b-field>

      <b-field label="Description"
               message="Brief description of what a record in this table represents.">
        <b-input v-model="tableDescription"
                 @input="dirty = true">
        </b-input>
      </b-field>

      <b-field>
        <b-checkbox v-model="tableVersioned"
                    @input="dirty = true">
          Record version data for this table
        </b-checkbox>
      </b-field>

      <br />

      <div class="level-left">
        <div class="level-item">
          <h4 class="block is-size-4">Columns</h4>
        </div>
        <div class="level-item">
          <b-button type="is-primary"
                    icon-pack="fas"
                    icon-left="plus"
                    @click="tableAddColumn()">
            New
          </b-button>
        </div>
      </div>

      <b-table
        :data="tableColumns">

        <b-table-column field="name"
                        label="Name"
                        v-slot="props">
          {{ props.row.name }}
        </b-table-column>

        <b-table-column field="data_type"
                        label="Data Type"
                        v-slot="props">
          {{ formatDataType(props.row.data_type) }}
        </b-table-column>

        <b-table-column field="nullable"
                        label="Nullable"
                        v-slot="props">
          {{ props.row.nullable ? "Yes" : "No" }}
        </b-table-column>

        <b-table-column field="versioned"
                        label="Versioned"
                        :visible="tableVersioned"
                        v-slot="props">
          {{ props.row.versioned ? "Yes" : "No" }}
        </b-table-column>

        <b-table-column field="description"
                        label="Description"
                        v-slot="props">
          {{ props.row.description }}
        </b-table-column>

        <b-table-column field="actions"
                        label="Actions"
                        v-slot="props">
          <a v-if="props.row.name != 'uuid'"
             href="#"
             @click.prevent="tableEditColumn(props.row)">
            <i class="fas fa-edit"></i>
            Edit
          </a>
          &nbsp;

          <a v-if="props.row.name != 'uuid'"
             href="#"
             class="has-text-danger"
             @click.prevent="tableDeleteColumn(props.index)">
            <i class="fas fa-trash"></i>
            Delete
          </a>
          &nbsp;
        </b-table-column>

      </b-table>

      <b-modal has-modal-card
               :active.sync="editingColumnShowDialog">
        <div class="modal-card">

          <header class="modal-card-head">
            <p class="modal-card-title">
              {{ (editingColumn && editingColumn.name) ? "Edit" : "New" }} Column
            </p>
          </header>

          <section class="modal-card-body">

            <b-field label="Name">
              <b-input v-model="editingColumnName"
                       ref="editingColumnName">
              </b-input>
            </b-field>

            <b-field grouped>

              <b-field label="Data Type">
                <b-select v-model="editingColumnDataType">
                  <option value="String">String</option>
                  <option value="Boolean">Boolean</option>
                  <option value="Integer">Integer</option>
                  <option value="Numeric">Numeric</option>
                  <option value="Date">Date</option>
                  <option value="DateTime">DateTime</option>
                  <option value="Text">Text</option>
                  <option value="LargeBinary">LargeBinary</option>
                  <option value="_fk_uuid_">FK/UUID</option>
                  <option value="_other_">Other</option>
                </b-select>
              </b-field>

              <b-field v-if="editingColumnDataType == 'String'"
                       label="Length"
                       :type="{'is-danger': !editingColumnDataTypeLength}"
                       style="max-width: 6rem;">
                <b-input v-model="editingColumnDataTypeLength">
                </b-input>
              </b-field>

              <b-field v-if="editingColumnDataType == 'Numeric'"
                       label="Precision"
                       :type="{'is-danger': !editingColumnDataTypePrecision}"
                       style="max-width: 6rem;">
                <b-input v-model="editingColumnDataTypePrecision">
                </b-input>
              </b-field>

              <b-field v-if="editingColumnDataType == 'Numeric'"
                       label="Scale"
                       :type="{'is-danger': !editingColumnDataTypeScale}"
                       style="max-width: 6rem;">
                <b-input v-model="editingColumnDataTypeScale">
                </b-input>
              </b-field>

              <b-field v-if="editingColumnDataType == '_fk_uuid_'"
                       label="Reference Table"
                       :type="{'is-danger': !editingColumnDataTypeReference}">
                <b-select v-model="editingColumnDataTypeReference">
                  <option v-for="table in existingTables"
                          :key="table.name"
                          :value="table.name">
                    {{ table.name }}
                  </option>
                </b-select>
              </b-field>

              <b-field v-if="editingColumnDataType == '_other_'"
                       label="Literal (include parens!)"
                       :type="{'is-danger': !editingColumnDataTypeLiteral}"
                       expanded>
                <b-input v-model="editingColumnDataTypeLiteral">
                </b-input>
              </b-field>

            </b-field>

            <b-field grouped>

              <b-field label="Nullable">
                <b-checkbox v-model="editingColumnNullable"
                            native-value="true">
                  {{ editingColumnNullable }}
                </b-checkbox>
              </b-field>

              <b-field label="Versioned"
                       v-if="tableVersioned">
                <b-checkbox v-model="editingColumnVersioned"
                            native-value="true">
                  {{ editingColumnVersioned }}
                </b-checkbox>
              </b-field>

              <b-field v-if="editingColumnDataType == '_fk_uuid_'"
                       label="Relationship">
                <b-input v-model="editingColumnRelationship"></b-input>
              </b-field>

            </b-field>

            <b-field label="Description">
              <b-input v-model="editingColumnDescription"></b-input>
            </b-field>

          </section>

          <footer class="modal-card-foot">
            <b-button @click="editingColumnShowDialog = false">
              Cancel
            </b-button>
            <b-button type="is-primary"
                      icon-pack="fas"
                      icon-left="save"
                      @click="editingColumnSave()">
              Save
            </b-button>
          </footer>
        </div>
      </b-modal>

      <br />

      <div class="buttons">
        <b-button type="is-primary"
                  icon-pack="fas"
                  icon-left="check"
                  @click="showStep('write-model')">
          Details are complete
        </b-button>
      </div>

    </b-step-item>

    <b-step-item step="2"
                 value="write-model"
                 label="Write Model">
      <h3 class="is-size-3 block">
        Write Model
      </h3>

      <b-field label="Schema Branch" horizontal>
        {{ alembicBranch }}
      </b-field>

      <b-field label="Table Name" horizontal>
        {{ tableName }}
      </b-field>

      <b-field label="Model Class" horizontal>
        {{ tableModelName }}
      </b-field>

      <b-field horizontal label="File">
        <b-input v-model="tableModelFile"></b-input>
      </b-field>

      <b-field horizontal>
        <b-checkbox v-model="tableModelFileOverwrite">
          Overwrite file if it exists
        </b-checkbox>
      </b-field>

      <div class="form">
        <div class="buttons">
          <b-button icon-pack="fas"
                    icon-left="arrow-left"
                    @click="showStep('enter-details')">
            Back
          </b-button>
          <b-button type="is-primary"
                    icon-pack="fas"
                    icon-left="save"
                    @click="writeModelFile()"
                    :disabled="writingModelFile">
            {{ writingModelFile ? "Working, please wait..." : "Write model class to file" }}
          </b-button>
          <b-button icon-pack="fas"
                    icon-left="arrow-right"
                    @click="showStep('review-model')">
            Skip
          </b-button>
        </div>
      </div>
    </b-step-item>

    <b-step-item step="3"
                 value="review-model"
                 label="Review Model"
                 clickable>
      <h3 class="is-size-3 block">
        Review Model
      </h3>

      <p class="block">
        Model code was generated to file:
      </p>

      <p class="block is-family-code" style="padding-left: 3rem;">
        {{ tableModelFile }}
      </p>

      <p class="block">
        First, review that code and adjust to your liking.
      </p>

      <p class="block">
        Next be sure to import the new model.  Typically this is done
        by editing the file...
      </p>

      <p class="block is-family-code" style="padding-left: 3rem;">
        ${model_dir}__init__.py
      </p>

      <p class="block">
        ...and adding a line such as:
      </p>

      <p class="block is-family-code" style="padding-left: 3rem;">
        from .{{ tableModelFileModuleName }} import {{ tableModelName }}
      </p>

      <p class="block">
        Once you&apos;ve done all that, the web app must be restarted.
        This may happen automatically depending on your setup.
        Test the model import status below.
      </p>

      <div class="card block">
        <header class="card-header">
          <p class="card-header-title">
            Model Import Status
          </p>
        </header>
        <div class="card-content">
          <div class="content">
            <div class="level">
              <div class="level-left">

                <div class="level-item">
                  <span v-if="!modelImported && !modelImportProblem">
                    import not yet attempted
                  </span>
                  <span v-if="modelImported"
                        class="has-text-success has-text-weight-bold">
                    imported okay
                  </span>
                  <span v-if="modelImportProblem"
                        class="has-text-danger">
                    import failed: {{ modelImportStatus }}
                  </span>
                </div>
              </div>
              <div class="level-right">
                <div class="level-item">
                  <b-field horizontal label="Model Class">
                    <b-input v-model="modelImportName"></b-input>
                  </b-field>
                </div>
                <div class="level-item">
                  <b-button type="is-primary"
                            icon-pack="fas"
                            icon-left="redo"
                            @click="modelImportTest()">
                    Refresh / Test Import
                  </b-button>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div class="buttons">
        <b-button icon-pack="fas"
                  icon-left="arrow-left"
                  @click="showStep('write-model')">
          Back
        </b-button>
        <b-button type="is-primary"
                  icon-pack="fas"
                  icon-left="check"
                  @click="showStep('write-revision')"
                  :disabled="!modelImported">
          Model class looks good!
        </b-button>
        <b-button icon-pack="fas"
                  icon-left="arrow-right"
                  @click="showStep('write-revision')">
          Skip
        </b-button>
      </div>
    </b-step-item>

    <b-step-item step="4"
                 value="write-revision"
                 label="Write Revision"
                 clickable>
      <h3 class="is-size-3 block">
        Write Revision
      </h3>
      <p class="block">
        You said the model class looked good, so next we will generate
        a revision script, used to modify DB schema.
      </p>

      <b-field label="Schema Branch"
               message="Leave this set to your custom app branch, unless you know what you're doing.">
        <b-select v-model="alembicBranch">
          <option v-for="branch in alembicBranchOptions"
                  :key="branch"
                  :value="branch">
            {{ branch }}
          </option>
        </b-select>
      </b-field>

      <b-field label="Message"
               message="Human-friendly brief description of the changes">
        <b-input v-model="revisionMessage"></b-input>
      </b-field>

      <br />

      <div class="buttons">
        <b-button icon-pack="fas"
                  icon-left="arrow-left"
                  @click="showStep('review-model')">
          Back
        </b-button>
        <b-button type="is-primary"
                  icon-pack="fas"
                  icon-left="save"
                  @click="writeRevisionScript()"
                  :disabled="writingRevisionScript">
          {{ writingRevisionScript ? "Working, please wait..." : "Generate revision script" }}
        </b-button>
        <b-button icon-pack="fas"
                  icon-left="arrow-right"
                  @click="showStep('review-revision')">
          Skip
        </b-button>
      </div>
    </b-step-item>

    <b-step-item step="5"
                 value="review-revision"
                 label="Review Revision">
      <h3 class="is-size-3 block">
        Review Revision
      </h3>

      <p class="block">
        Revision script was generated to file:
      </p>

      <p class="block is-family-code" style="padding-left: 3rem;">
        {{ revisionScript }}
      </p>

      <p class="block">
        Please review that code and adjust to your liking.
      </p>

      <div class="buttons">
        <b-button icon-pack="fas"
                  icon-left="arrow-left"
                  @click="showStep('write-revision')">
          Back
        </b-button>
        <b-button type="is-primary"
                  icon-pack="fas"
                  icon-left="check"
                  @click="showStep('upgrade-db')">
          Revision script looks good!
        </b-button>
      </div>
    </b-step-item>

    <b-step-item step="6"
                 value="upgrade-db"
                 label="Upgrade DB"
                 clickable>
      <h3 class="is-size-3 block">
        Upgrade DB
      </h3>
      <p class="block">
        You said the revision script looked good, so next we will use
        it to upgrade your actual database.
      </p>

      <div class="buttons">
        <b-button icon-pack="fas"
                  icon-left="arrow-left"
                  @click="showStep('review-revision')">
          Back
        </b-button>
        <b-button type="is-primary"
                  icon-pack="fas"
                  icon-left="arrow-up"
                  @click="upgradeDB()"
                  :disabled="upgradingDB">
          {{ upgradingDB ? "Working, please wait..." : "Upgrade database" }}
        </b-button>
      </div>
    </b-step-item>

    <b-step-item step="7"
                 value="review-db"
                 label="Review DB"
                 clickable>
      <h3 class="is-size-3 block">
        Review DB
      </h3>

      <p class="block">
        At this point your new table should be present in the DB.
        Test below.
      </p>

      <div class="card block">
        <header class="card-header">
          <p class="card-header-title">
            Table Status
          </p>
        </header>
        <div class="card-content">
          <div class="content">
            <div class="level">
              <div class="level-left">

                <div class="level-item">
                  <span v-if="!tableCheckAttempted">
                    check not yet attempted
                  </span>
                  <span v-if="tableCheckAttempted && !tableCheckProblem"
                        class="has-text-success has-text-weight-bold">
                    table exists!
                  </span>
                  <span v-if="tableCheckProblem"
                        class="has-text-danger">
                    {{ tableCheckProblem }}
                  </span>
                </div>
              </div>
              <div class="level-right">
                <div class="level-item">
                  <b-field horizontal label="Table Name">
                    <b-input v-model="tableName"></b-input>
                  </b-field>
                </div>
                <div class="level-item">
                  <b-button type="is-primary"
                            icon-pack="fas"
                            icon-left="redo"
                            @click="tableCheck()">
                    Test for Table
                  </b-button>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div class="buttons">
        <b-button icon-pack="fas"
                  icon-left="arrow-left"
                  @click="showStep('upgrade-db')">
          Back
        </b-button>
        <b-button type="is-primary"
                  icon-pack="fas"
                  icon-left="check"
                  @click="showStep('commit-code')"
                  :disabled="!tableCheckAttempted || tableCheckProblem">
          DB looks good!
        </b-button>
      </div>
    </b-step-item>

    <b-step-item step="8"
                 value="commit-code"
                 label="Commit Code">
      <h3 class="is-size-3 block">
        Commit Code
      </h3>

      <p class="block">
        Hope you're having a great day.
      </p>

      <p class="block">
        Don't forget to commit code changes to your source repo.
      </p>

      <div class="buttons">
        <b-button icon-pack="fas"
                  icon-left="arrow-left"
                  @click="showStep('review-db')">
          Back
        </b-button>
        <once-button type="is-primary"
                     tag="a" :href="tableURL"
                     icon-left="arrow-right"
                     :text="`Show me my new table: ${'$'}{tableName}`">
        </once-button>
      </div>
    </b-step-item>
  </b-steps>
</%def>

<%def name="modify_vue_vars()">
  ${parent.modify_vue_vars()}
  <script>

    // nb. for warning user they may lose changes if leaving page
    ThisPageData.dirty = false

    ThisPageData.activeStep = null
    ThisPageData.alembicBranchOptions = ${json.dumps(branch_name_options)|n}

    ThisPageData.existingTables = ${json.dumps(existing_tables)|n}

    ThisPageData.alembicBranch = ${json.dumps(branch_name)|n}
    ThisPageData.tableName = '${rattail_app.get_table_prefix()}_widget'
    ThisPageData.tableModelName = '${rattail_app.get_class_prefix()}Widget'
    ThisPageData.tableModelTitle = 'Widget'
    ThisPageData.tableModelTitlePlural = 'Widgets'
    ThisPageData.tableDescription = "Represents a cool widget."
    ThisPageData.tableVersioned = true

    ThisPageData.tableColumns = [{
        name: 'uuid',
        data_type: {
            type: 'String',
            length: 32,
        },
        nullable: false,
        description: "UUID primary key",
        versioned: true,
    }]

    ThisPageData.editingColumnShowDialog = false
    ThisPageData.editingColumn = null
    ThisPageData.editingColumnName = null
    ThisPageData.editingColumnDataType = null
    ThisPageData.editingColumnDataTypeLength = null
    ThisPageData.editingColumnDataTypePrecision = null
    ThisPageData.editingColumnDataTypeScale = null
    ThisPageData.editingColumnDataTypeReference = null
    ThisPageData.editingColumnDataTypeLiteral = null
    ThisPageData.editingColumnNullable = true
    ThisPageData.editingColumnDescription = null
    ThisPageData.editingColumnVersioned = true
    ThisPageData.editingColumnRelationship = null

    ThisPage.methods.showStep = function(step) {
        this.activeStep = step

        // scroll so top of page is shown
        this.$nextTick(() => {
            this.$refs['showme'].scrollIntoView(true)
        })
    }

    ThisPage.methods.tableAddColumn = function() {
        this.editingColumn = null
        this.editingColumnName = null
        this.editingColumnDataType = null
        this.editingColumnDataTypeLength = null
        this.editingColumnDataTypePrecision = null
        this.editingColumnDataTypeScale = null
        this.editingColumnDataTypeReference = null
        this.editingColumnDataTypeLiteral = null
        this.editingColumnNullable = true
        this.editingColumnDescription = null
        this.editingColumnVersioned = true
        this.editingColumnRelationship = null
        this.editingColumnShowDialog = true
        this.$nextTick(() => {
            this.$refs.editingColumnName.focus()
        })
    }

    ThisPage.methods.tableEditColumn = function(column) {
        this.editingColumn = column
        this.editingColumnName = column.name
        this.editingColumnDataType = column.data_type.type
        this.editingColumnDataTypeLength = column.data_type.length
        this.editingColumnDataTypePrecision = column.data_type.precision
        this.editingColumnDataTypeScale = column.data_type.scale
        this.editingColumnDataTypeReference = column.data_type.reference
        this.editingColumnDataTypeLiteral = column.data_type.literal
        this.editingColumnNullable = column.nullable
        this.editingColumnDescription = column.description
        this.editingColumnVersioned = column.versioned
        this.editingColumnRelationship = column.relationship
        this.editingColumnShowDialog = true
        this.$nextTick(() => {
            this.$refs.editingColumnName.focus()
        })
    }

    ThisPage.methods.formatDataType = function(dataType) {
        if (dataType.type == 'String') {
            return `sa.String(length=${'$'}{dataType.length})`
        } else if (dataType.type == 'Numeric') {
            return `sa.Numeric(precision=${'$'}{dataType.precision}, scale=${'$'}{dataType.scale})`
        } else if (dataType.type == '_fk_uuid_') {
            return 'sa.String(length=32)'
        } else if (dataType.type == '_other_') {
            return dataType.literal
        } else {
            return `sa.${'$'}{dataType.type}()`
        }
    }

    ThisPage.watch.editingColumnDataTypeReference = function(newval, oldval) {
        this.editingColumnRelationship = newval
        if (newval && !this.editingColumnName) {
            this.editingColumnName = `${'$'}{newval}_uuid`
        }
    }

    ThisPage.methods.editingColumnSave = function() {
        let column
        if (this.editingColumn) {
            column = this.editingColumn
        } else {
            column = {}
            this.tableColumns.push(column)
        }

        column.name = this.editingColumnName

        let dataType = {type: this.editingColumnDataType}
        if (dataType.type == 'String') {
            dataType.length = this.editingColumnDataTypeLength
        } else if (dataType.type == 'Numeric') {
            dataType.precision = this.editingColumnDataTypePrecision
            dataType.scale = this.editingColumnDataTypeScale
        } else if (dataType.type == '_fk_uuid_') {
            dataType.reference = this.editingColumnDataTypeReference
        } else if (dataType.type == '_other_') {
            dataType.literal = this.editingColumnDataTypeLiteral
        }
        column.data_type = dataType

        column.nullable = this.editingColumnNullable
        column.description = this.editingColumnDescription
        column.versioned = this.editingColumnVersioned
        column.relationship = this.editingColumnRelationship

        this.dirty = true
        this.editingColumnShowDialog = false
    }

    ThisPage.methods.tableDeleteColumn = function(index) {
        if (confirm("Really delete this column?")) {
            this.tableColumns.splice(index, 1)
            this.dirty = true
        }
    }

    ThisPageData.tableModelFile = '${model_dir}widget.py'
    ThisPageData.tableModelFileOverwrite = false
    ThisPageData.writingModelFile = false

    ThisPage.methods.writeModelFile = function() {
        this.writingModelFile = true

        this.modelImportName = this.tableModelName
        this.modelImported = false
        this.modelImportStatus = "import not yet attempted"
        this.modelImportProblem = false

        for (let column of this.tableColumns) {
            column.formatted_data_type = this.formatDataType(column.data_type)
        }

        let url = '${url('{}.write_model_file'.format(route_prefix))}'
        let params = {
            branch_name: this.alembicBranch,
            table_name: this.tableName,
            model_name: this.tableModelName,
            model_title: this.tableModelTitle,
            model_title_plural: this.tableModelTitlePlural,
            description: this.tableDescription,
            versioned: this.tableVersioned,
            columns: this.tableColumns,
            module_file: this.tableModelFile,
            overwrite: this.tableModelFileOverwrite,
        }
        this.submitForm(url, params, response => {
            this.writingModelFile = false
            this.activeStep = 'review-model'
        }, response => {
            this.writingModelFile = false
        })
    }

    ThisPageData.modelImportName = '${rattail_app.get_class_prefix()}Widget'
    ThisPageData.modelImportStatus = "import not yet attempted"
    ThisPageData.modelImported = false
    ThisPageData.modelImportProblem = false

    ThisPage.computed.tableModelFileModuleName = function() {
        let path = this.tableModelFile
        path = path.replace(/^.*\//, '')
        path = path.replace(/\.py$/, '')
        return path
    }

    ThisPage.methods.modelImportTest = function() {
        let url = '${url('{}.check_model'.format(route_prefix))}'
        let params = {model_name: this.modelImportName}
        this.submitForm(url, params, response => {
            if (response.data.problem) {
                this.modelImportProblem = true
                this.modelImported = false
                this.modelImportStatus = response.data.problem
            } else {
                this.modelImportProblem = false
                this.modelImported = true
                this.revisionMessage = `add table for ${'$'}{this.tableModelTitlePlural}`
            }
        })
    }

    ThisPageData.writingRevisionScript = false
    ThisPageData.revisionMessage = null
    ThisPageData.revisionScript = null

    ThisPage.methods.writeRevisionScript = function() {
        this.writingRevisionScript = true

        let url = '${url('{}.write_revision_script'.format(route_prefix))}'
        let params = {
            branch: this.alembicBranch,
            message: this.revisionMessage,
        }
        this.submitForm(url, params, response => {
            this.writingRevisionScript = false
            this.revisionScript = response.data.script
            this.activeStep = 'review-revision'
        }, response => {
            this.writingRevisionScript = false
        })
    }

    ThisPageData.upgradingDB = false

    ThisPage.methods.upgradeDB = function() {
        this.upgradingDB = true

        let url = '${url('{}.upgrade_db'.format(route_prefix))}'
        let params = {}
        this.submitForm(url, params, response => {
            this.upgradingDB = false
            this.activeStep = 'review-db'
        }, response => {
            this.upgradingDB = false
        })
    }

    ThisPageData.tableCheckAttempted = false
    ThisPageData.tableCheckProblem = null

    ThisPageData.tableURL = null

    ThisPage.methods.tableCheck = function() {
        let url = '${url('{}.check_table'.format(route_prefix))}'
        let params = {table_name: this.tableName}
        this.submitForm(url, params, response => {
            if (response.data.problem) {
                this.tableCheckProblem = response.data.problem
            } else {
                this.tableURL = response.data.url
            }
            this.tableCheckAttempted = true
        })
    }

    // cf. https://stackoverflow.com/a/56551646
    ThisPage.methods.beforeWindowUnload = function(e) {

        // warn user if navigating away would lose changes
        if (this.dirty) {
            e.preventDefault()
            e.returnValue = ''
        }
    }

    ThisPage.created = function() {
        window.addEventListener('beforeunload', this.beforeWindowUnload)
    }

  </script>
</%def>
