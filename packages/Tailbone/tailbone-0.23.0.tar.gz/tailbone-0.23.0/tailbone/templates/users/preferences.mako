## -*- coding: utf-8; -*-
<%inherit file="/configure.mako" />

<%def name="title()">
  % if current_user:
      Edit Preferences
  % else:
      ${index_title} &raquo; ${instance_title} &raquo; Preferences
  % endif
</%def>

<%def name="content_title()">Preferences</%def>

<%def name="intro_message()">
  <p class="block">
    % if current_user:
        This page lets you modify your preferences.
    % else:
        This page lets you modify the preferences for ${config_title}.
    % endif
  </p>
</%def>

<%def name="form_content()">

  <h3 class="block is-size-3">Display</h3>
  <div class="block" style="padding-left: 2rem;">

    <b-field label="Theme Style">
        <b-select name="tailbone.${user.uuid}.user_css"
                  v-model="simpleSettings['tailbone.${user.uuid}.user_css']"
                  @input="settingsNeedSaved = true">
          <option v-for="option in themeStyleOptions"
                  :key="option.value"
                  :value="option.value">
            {{ option.label }}
          </option>
        </b-select>

    </b-field>  

  </div>
</%def>

<%def name="modify_vue_vars()">
  ${parent.modify_vue_vars()}
  <script>
    ThisPageData.themeStyleOptions = ${json.dumps(theme_style_options)|n}
  </script>
</%def>
