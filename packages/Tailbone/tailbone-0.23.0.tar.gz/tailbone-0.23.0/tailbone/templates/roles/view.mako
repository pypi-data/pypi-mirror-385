## -*- coding: utf-8; -*-
<%inherit file="/master/view.mako" />

<%def name="extra_styles()">
  ${parent.extra_styles()}
  ${h.stylesheet_link(request.static_url('tailbone:static/css/perms.css'))}
</%def>

<%def name="modify_vue_vars()">
  ${parent.modify_vue_vars()}
  <script>

    % if users_data is not Undefined:
        ${form.vue_component}Data.usersData = ${json.dumps(users_data)|n}
    % endif

    ThisPage.methods.detachPerson = function(url) {
        ## TODO: this should require POST! but for now we just redirect..
        if (confirm("Are you sure you want to detach this person from this customer account?")) {
            location.href = url
        }
    }

  </script>
</%def>
