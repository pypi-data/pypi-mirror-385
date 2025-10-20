## -*- coding: utf-8; -*-
<%inherit file="/master/index.mako" />

<%def name="context_menu_items()">
  ${parent.context_menu_items()}
  % if master.has_perm('find_by_perm'):
      <li>${h.link_to(f"Find {model_title_plural} by Permission", url(f'{route_prefix}.find_by_perm'))}</li>
  % endif
</%def>

${parent.body()}
