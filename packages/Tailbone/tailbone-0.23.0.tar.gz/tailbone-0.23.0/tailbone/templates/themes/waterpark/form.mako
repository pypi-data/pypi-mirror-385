## -*- coding: utf-8; -*-
<%inherit file="wuttaweb:templates/form.mako" />

<%def name="render_vue_template_form()">
  % if form is not Undefined:
      ${form.render_vue_template(buttons=capture(self.render_form_buttons))}
  % endif
</%def>

<%def name="render_form_buttons()"></%def>
