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
  <b-steps v-model="activeStep"
           :animated="false"
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

      <b-field grouped>

        <b-field label="Model Name">
          <b-select v-model="modelName">
            <option v-for="name in modelNames"
                    :key="name"
                    :value="name">
              {{ name }}
            </option>
          </b-select>
        </b-field>

        <b-field label="View Class Name">
          <b-input v-model="viewClassName">
          </b-input>
        </b-field>

        <b-field label="View Route Prefix">
          <b-input v-model="viewRoutePrefix">
          </b-input>
        </b-field>

      </b-field>

      <br />

      <div class="buttons">
        <b-button type="is-primary"
                  icon-pack="fas"
                  icon-left="check"
                  @click="activeStep = 'write-view'">
          Details are complete
        </b-button>
      </div>

    </b-step-item>

    <b-step-item step="2"
                 value="write-view"
                 label="Write View">
      <h3 class="is-size-3 block">
        Write View
      </h3>

      <b-field label="Model Name" horizontal>
        {{ modelName }}
      </b-field>

      <b-field label="View Class" horizontal>
        {{ viewClassName }}
      </b-field>

      <b-field horizontal label="File">
        <b-input v-model="viewFile"></b-input>
      </b-field>

      <b-field horizontal>
        <b-checkbox v-model="viewFileOverwrite">
          Overwrite file if it exists
        </b-checkbox>
      </b-field>

      <div class="form">
        <div class="buttons">
          <b-button icon-pack="fas"
                    icon-left="arrow-left"
                    @click="activeStep = 'enter-details'">
            Back
          </b-button>
          <b-button type="is-primary"
                    icon-pack="fas"
                    icon-left="save"
                    @click="writeViewFile()"
                    :disabled="writingViewFile">
            {{ writingViewFile ? "Working, please wait..." : "Write view class to file" }}
          </b-button>
          <b-button icon-pack="fas"
                    icon-left="arrow-right"
                    @click="activeStep = 'review-view'">
            Skip
          </b-button>
        </div>
      </div>
    </b-step-item>

    <b-step-item step="3"
                 value="review-view"
                 label="Review View"
                 ## clickable
                 >
      <h3 class="is-size-3 block">
        Review View
      </h3>

      <p class="block">
        View code was generated to file:
      </p>

      <p class="block is-family-code" style="padding-left: 3rem;">
        {{ viewFile }}
      </p>

      <p class="block">
        First, review that code and adjust to your liking.
      </p>

      <p class="block">
        Next be sure to include the new view in your config.
        Typically this is done by editing the file...
      </p>

      <p class="block is-family-code" style="padding-left: 3rem;">
        ${view_dir}__init__.py
      </p>

      <p class="block">
        ...and adding a line to the includeme() block such as:
      </p>

      <pre class="block">
def includeme(config):

    # ...existing config includes here...

    ## TODO: stop hard-coding widgets
    config.include('${pkgroot}.web.views.widgets')
      </pre>

      <p class="block">
        Once you&apos;ve done all that, the web app must be restarted.
        This may happen automatically depending on your setup.
        Test the view status below.
      </p>

      <div class="card block">
        <header class="card-header">
          <p class="card-header-title">
            View Status
          </p>
        </header>
        <div class="card-content">
          <div class="content">
            <div class="level">
              <div class="level-left">

                <div class="level-item">
                  <span v-if="!viewImportAttempted">
                    check not yet attempted
                  </span>
                  <span v-if="viewImported"
                        class="has-text-success has-text-weight-bold">
                    route found!
                  </span>
                  <span v-if="viewImportAttempted && viewImportProblem"
                        class="has-text-danger">
                    {{ viewImportProblem }}
                  </span>
                </div>
              </div>
              <div class="level-right">
                <div class="level-item">
                  <b-field horizontal label="Route Prefix">
                    <b-input v-model="viewRoutePrefix"></b-input>
                  </b-field>
                </div>
                <div class="level-item">
                  <b-button type="is-primary"
                            icon-pack="fas"
                            icon-left="redo"
                            @click="testView()">
                    Test View
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
                  @click="activeStep = 'write-view'">
          Back
        </b-button>
        <b-button type="is-primary"
                  icon-pack="fas"
                  icon-left="check"
                  @click="activeStep = 'commit-code'"
                  :disabled="!viewImported">
          View class looks good!
        </b-button>
        <b-button icon-pack="fas"
                  icon-left="arrow-right"
                  @click="activeStep = 'commit-code'">
          Skip
        </b-button>
      </div>
    </b-step-item>

    <b-step-item step="4"
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
                  @click="activeStep = 'review-view'">
          Back
        </b-button>
        <once-button type="is-primary"
                     tag="a" :href="viewURL"
                     icon-left="arrow-right"
                     :disabled="!viewURL"
                     :text="`Show me my new view: ${'$'}{viewClassName}`">
        </once-button>
      </div>
    </b-step-item>

  </b-steps>
</%def>

<%def name="modify_vue_vars()">
  ${parent.modify_vue_vars()}
  <script>

    ThisPageData.activeStep = 'enter-details'

    ThisPageData.modelNames = ${json.dumps(model_names)|n}
    ThisPageData.modelName = null
    ThisPageData.viewClassName = null
    ThisPageData.viewRoutePrefix = null

    ThisPage.watch.modelName = function(newName, oldName) {
        this.viewClassName = `${'$'}{newName}View`
        this.viewRoutePrefix = newName.toLowerCase()
    }

    ThisPage.mounted = function() {
        let params = new URLSearchParams(location.search)
        if (params.has('model_name')) {
            this.modelName = params.get('model_name')
        }
    }

    ThisPageData.viewFile = '${view_dir}widgets.py'
    ThisPageData.viewFileOverwrite = false
    ThisPageData.writingViewFile = false

    ThisPage.methods.writeViewFile = function() {
        this.writingViewFile = true

        let url = '${url('{}.write_view_file'.format(route_prefix))}'
        let params = {
            view_file: this.viewFile,
            overwrite: this.viewFileOverwrite,
            view_class_name: this.viewClassName,
            model_name: this.modelName,
            route_prefix: this.viewRoutePrefix,
        }
        this.submitForm(url, params, response => {
            this.writingViewFile = false
            this.activeStep = 'review-view'
        }, response => {
            this.writingViewFile = false
        })
    }

    ThisPageData.viewImported = false
    ThisPageData.viewImportAttempted = false
    ThisPageData.viewImportProblem = null

    ThisPage.methods.testView = function() {

        this.viewImported = false
        this.viewImportProblem = null

        let url = '${url('{}.check_view'.format(route_prefix))}'

        let params = {
            route_prefix: this.viewRoutePrefix,
        }
        this.submitForm(url, params, response => {
            this.viewImportAttempted = true
            if (response.data.problem) {
                this.viewImportProblem = response.data.problem
            } else {
                this.viewImported = true
                this.viewURL = response.data.url
            }
        })
    }

    ThisPageData.viewURL = null

  </script>
</%def>
