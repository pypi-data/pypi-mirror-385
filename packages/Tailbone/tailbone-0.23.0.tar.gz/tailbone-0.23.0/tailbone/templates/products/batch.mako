## -*- coding: utf-8; -*-
<%inherit file="/form.mako" />

<%def name="title()">Create Batch</%def>

<%def name="context_menu_items()">
  <li>${h.link_to("Back to Products", url('products'))}</li>
</%def>

<%def name="render_deform_field(form, field)">
  <b-field horizontal
           % if field.description:
           message="${field.description}"
           % endif
           % if field.error:
           type="is-danger"
           :message='${form.messages_json(field.error.messages())|n}'
           % endif
           label="${field.title}">
    ${field.serialize()|n}
  </b-field>
</%def>

<%def name="render_form_innards()">
  ${h.form(request.current_route_url(), **{'@submit': 'submit{}'.format(form.vue_component)})}
  ${h.csrf_token(request)}

  <section>
    ${render_deform_field(form, dform['batch_type'])}
    ${render_deform_field(form, dform['description'])}
    ${render_deform_field(form, dform['notes'])}

    % for key, pform in params_forms.items():
        <div v-show="field_model_batch_type == '${key}'">
          % for field in pform.make_deform_form():
              ${render_deform_field(pform, field)}
          % endfor
        </div>
    % endfor
  </section>

  <br />
  <div class="buttons">
    <b-button type="is-primary"
              native-type="submit"
              :disabled="${form.vue_component}Submitting">
      {{ ${form.vue_component}ButtonText }}
    </b-button>
    <b-button tag="a" href="${url('products')}">
      Cancel
    </b-button>
  </div>

  ${h.end_form()}
</%def>

<%def name="render_form_template()">
  <script type="text/x-template" id="${form.vue_tagname}-template">
    ${self.render_form_innards()}
  </script>
</%def>

<%def name="modify_vue_vars()">
  ${parent.modify_vue_vars()}
  <% request.register_component(form.vue_tagname, form.vue_component) %>
  <script>

    ## TODO: ugh, an awful lot of duplicated code here (from /forms/deform.mako)

    let ${form.vue_component} = {
        template: '#${form.vue_tagname}-template',
        methods: {

            ## TODO: deprecate / remove the latter option here
            % if form.auto_disable_save or form.auto_disable:
                submit${form.vue_component}() {
                    this.${form.vue_component}Submitting = true
                    this.${form.vue_component}ButtonText = "Working, please wait..."
                }
            % endif
        }
    }

    let ${form.vue_component}Data = {

        ## TODO: ugh, this seems pretty hacky.  need to declare some data models
        ## for various field components to bind to...
        % if not form.readonly:
            % for field in form.fields:
                % if field in dform:
                    <% field = dform[field] %>
                    field_model_${field.name}: ${form.get_vuejs_model_value(field)|n},
                % endif
            % endfor
        % endif

        ## TODO: deprecate / remove the latter option here
        % if form.auto_disable_save or form.auto_disable:
            ${form.vue_component}Submitting: false,
            ${form.vue_component}ButtonText: ${json.dumps(getattr(form, 'submit_label', getattr(form, 'save_label', "Submit")))|n},
        % endif

        ## TODO: more hackiness, this is for the sake of batch params
        ## (this of course was *not* copied from normal deform template!)
        % for key, pform in params_forms.items():
            <% pdform = pform.make_deform_form() %>
            % for field in pform.fields:
                % if field in pdform:
                    <% field = pdform[field] %>
                    field_model_${field.name}: ${pform.get_vuejs_model_value(field)|n},
                % endif
            % endfor
        % endfor
    }

  </script>
</%def>
