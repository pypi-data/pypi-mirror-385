## -*- coding: utf-8; -*-
<%inherit file="wuttaweb:templates/base_meta.mako" />

<%def name="app_title()">${app.get_node_title()}</%def>

<%def name="favicon()">
  <link rel="icon" type="image/x-icon" href="${request.rattail_config.get('tailbone', 'favicon_url', default=request.static_url('tailbone:static/img/rattail.ico'))}" />
</%def>

<%def name="header_logo()">
  ${h.image(request.rattail_config.get('tailbone', 'header_image_url', default=request.static_url('tailbone:static/img/rattail.ico')), "Header Logo", style="height: 49px;")}
</%def>
