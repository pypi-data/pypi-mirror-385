## -*- coding: utf-8; -*-
<%inherit file="/page.mako" />

<%def name="extra_styles()">
  ${parent.extra_styles()}
  <style type="text/css">

    .worksheet tr.active {
        border: 5px solid Blue;
    }

    .worksheet .current-entry {
        text-align: center;
    }

    .worksheet .current-entry input {
        text-align: center;
        width: 3em;
    }

  </style>
</%def>

<%def name="worksheet_grid()"></%def>

<%def name="page_content()">
  ${self.worksheet_grid()}
</%def>


${parent.body()}
