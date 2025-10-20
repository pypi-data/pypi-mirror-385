## -*- coding: utf-8; -*-
<%inherit file="/master/index.mako" />

<%def name="context_menu_items()">
  ${parent.context_menu_items()}
  % if master.has_perm('migrations'):
      <li>${h.link_to("View / Apply Migrations", url('{}.migrations'.format(route_prefix)))}</li>
  % endif
</%def>


${parent.body()}
