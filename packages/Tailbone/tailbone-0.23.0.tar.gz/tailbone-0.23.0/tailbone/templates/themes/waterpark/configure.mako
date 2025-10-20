## -*- coding: utf-8; -*-
<%inherit file="wuttaweb:templates/configure.mako" />
<%namespace name="tailbone_base" file="tailbone:templates/configure.mako" />

<%def name="input_file_templates_section()">
  ${tailbone_base.input_file_templates_section()}
</%def>

<%def name="output_file_templates_section()">
  ${tailbone_base.output_file_templates_section()}
</%def>

<%def name="modify_vue_vars()">
  ${parent.modify_vue_vars()}
  <script>

    ##############################
    ## input file templates
    ##############################

    % if input_file_template_settings is not Undefined:

        ThisPageData.inputFileTemplateSettings = ${json.dumps(input_file_template_settings)|n}
        ThisPageData.inputFileTemplateFileOptions = ${json.dumps(input_file_options)|n}
        ThisPageData.inputFileTemplateUploads = {
            % for key in input_file_templates:
                '${key}': null,
            % endfor
        }

        ThisPage.methods.validateInputFileTemplateSettings = function() {
            % for tmpl in input_file_templates.values():
                if (this.inputFileTemplateSettings['${tmpl['setting_mode']}'] == 'hosted') {
                    if (!this.inputFileTemplateSettings['${tmpl['setting_file']}']) {
                        if (!this.inputFileTemplateUploads['${tmpl['key']}']) {
                            return "You must provide a file to upload for the ${tmpl['label']} template."
                        }
                    }
                }
            % endfor
        }

        ThisPageData.validators.push(ThisPage.methods.validateInputFileTemplateSettings)

    % endif

    ##############################
    ## output file templates
    ##############################

    % if output_file_template_settings is not Undefined:

        ThisPageData.outputFileTemplateSettings = ${json.dumps(output_file_template_settings)|n}
        ThisPageData.outputFileTemplateFileOptions = ${json.dumps(output_file_options)|n}
        ThisPageData.outputFileTemplateUploads = {
            % for key in output_file_templates:
                '${key}': null,
            % endfor
        }

        ThisPage.methods.validateOutputFileTemplateSettings = function() {
            % for tmpl in output_file_templates.values():
                if (this.outputFileTemplateSettings['${tmpl['setting_mode']}'] == 'hosted') {
                    if (!this.outputFileTemplateSettings['${tmpl['setting_file']}']) {
                        if (!this.outputFileTemplateUploads['${tmpl['key']}']) {
                            return "You must provide a file to upload for the ${tmpl['label']} template."
                        }
                    }
                }
            % endfor
        }

        ThisPageData.validators.push(ThisPage.methods.validateOutputFileTemplateSettings)

    % endif

  </script>
</%def>
