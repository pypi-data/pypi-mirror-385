## -*- coding: utf-8; -*-
<%inherit file="/form.mako" />

<%def name="title()">Clone ${model_title}: ${instance_title}</%def>

<%def name="render_form()">
  <br />
  <b-notification :closable="false">
    You are about to clone the following ${model_title} as a new record:
  </b-notification>
  ${parent.render_form()}
</%def>

<%def name="render_form_buttons()">
  <br />
  <b-notification :closable="false">
    Are you sure about this?
  </b-notification>
  <br />

  ${h.form(request.current_route_url(), **{'@submit': 'submitForm'})}
  ${h.csrf_token(request)}
  ${h.hidden('clone', value='clone')}
    <div class="buttons">
      <once-button tag="a" href="${form.cancel_url}"
                   text="Whoops, nevermind...">
      </once-button>
      <b-button type="is-primary"
                native-type="submit"
                :disabled="formSubmitting">
        {{ submitButtonText }}
      </b-button>
    </div>
  ${h.end_form()}
</%def>

<%def name="modify_vue_vars()">
  ${parent.modify_vue_vars()}
  <script>

    TailboneFormData.formSubmitting = false
    TailboneFormData.submitButtonText = "Yes, please clone away"

    TailboneForm.methods.submitForm = function() {
        this.formSubmitting = true
        this.submitButtonText = "Working, please wait..."
    }

  </script>
</%def>
