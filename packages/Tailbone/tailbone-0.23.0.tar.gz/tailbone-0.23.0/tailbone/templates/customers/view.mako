## -*- coding: utf-8; -*-
<%inherit file="/master/view.mako" />
<%namespace file="/util.mako" import="view_profiles_helper" />

<%def name="object_helpers()">
  ${parent.object_helpers()}
  % if show_profiles_helper and show_profiles_people:
      ${view_profiles_helper(show_profiles_people)}
  % endif
</%def>

<%def name="render_form()">
  <div class="form">
    <tailbone-form @detach-person="detachPerson">
    </tailbone-form>
  </div>
</%def>

<%def name="modify_vue_vars()">
  ${parent.modify_vue_vars()}
  <script>

    % if expose_shoppers:
    ${form.vue_component}Data.shoppers = ${json.dumps(shoppers_data)|n}
    % endif
    % if expose_people:
    ${form.vue_component}Data.peopleData = ${json.dumps(people_data)|n}
    % endif

    ThisPage.methods.detachPerson = function(url) {
        ## TODO: this should require POST! but for now we just redirect..
        if (confirm("Are you sure you want to detach this person from this customer account?")) {
            location.href = url
        }
    }

  </script>
</%def>
