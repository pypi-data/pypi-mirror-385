## -*- coding: utf-8; -*-
<%inherit file="/master/view.mako" />
<%namespace file="/util.mako" import="view_profiles_helper" />

<%def name="page_content()">
  ${parent.page_content()}
  % if not instance.users and request.has_perm('users.create'):
      ${h.form(url('people.make_user'), ref='makeUserForm')}
      ${h.csrf_token(request)}
      ${h.hidden('person_uuid', value=instance.uuid)}
      ${h.end_form()}
  % endif
</%def>

<%def name="object_helpers()">
  ${parent.object_helpers()}
  ${view_profiles_helper([instance])}
</%def>

<%def name="render_form()">
  <div class="form">
    <${form.vue_tagname} v-on:make-user="makeUser"></${form.vue_tagname}>
  </div>
</%def>

<%def name="modify_vue_vars()">
  ${parent.modify_vue_vars()}
  <script>

    ${form.vue_component}.methods.clickMakeUser = function(event) {
        this.$emit('make-user')
    }

    ThisPage.methods.makeUser = function(event) {
        if (confirm("Really make a user account for this person?")) {
            this.$refs.makeUserForm.submit()
        }
    }

  </script>
</%def>
