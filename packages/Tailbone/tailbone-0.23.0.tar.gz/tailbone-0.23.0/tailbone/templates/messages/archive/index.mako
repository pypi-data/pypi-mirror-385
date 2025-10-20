## -*- coding: utf-8; -*-
<%inherit file="/messages/index.mako" />

<%def name="title()">Message Archive</%def>

<%def name="context_menu_items()">
  ${parent.context_menu_items()}
  <li>${h.link_to("Go to my Message Inbox", url('messages.inbox'))}</li>
  <li>${h.link_to("Go to my Sent Messages", url('messages.sent'))}</li>
</%def>


${parent.body()}
