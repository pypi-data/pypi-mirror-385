## -*- coding: utf-8; -*-
<%inherit file="wuttaweb:templates/auth/login.mako" />

## TODO: this will not be needed with wuttaform
<%def name="extra_styles()">
  ${parent.extra_styles()}
  <style>
    .card-content .buttons {
        justify-content: right;
    }
  </style>
</%def>

## DEPRECATED; remains for back-compat
<%def name="render_this_page()">
  ${self.page_content()}
</%def>
