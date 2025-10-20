## -*- coding: utf-8; -*-
<%inherit file="/master/index.mako" />

<%def name="context_menu_items()">
  % if request.has_perm('messages.create'):
      <li>${h.link_to("Send a new Message", url('messages.create'))}</li>
  % endif
</%def>

<%def name="grid_tools()">
  % if request.matched_route.name in ('messages.inbox', 'messages.archive'):
      ${h.form(url('messages.move_bulk'), **{'@submit': 'moveMessagesSubmit'})}
      ${h.csrf_token(request)}
      ${h.hidden('destination', value='archive' if request.matched_route.name == 'messages.inbox' else 'inbox')}
      ${h.hidden('uuids', v_model='selected_uuids')}
      <b-button type="is-primary"
                native-type="submit"
                :disabled="moveMessagesSubmitting || !checkedRows.length">
        {{ moveMessagesTextCurrent }}
      </b-button>
      ${h.end_form()}
  % endif
</%def>

<%def name="modify_vue_vars()">
  ${parent.modify_vue_vars()}
  % if request.matched_route.name in ('messages.inbox', 'messages.archive'):
      <script>

        ${grid.vue_component}Data.moveMessagesSubmitting = false
        ${grid.vue_component}Data.moveMessagesText = null

        ${grid.vue_component}.computed.moveMessagesTextCurrent = function() {
            if (this.moveMessagesText) {
                return this.moveMessagesText
            }
            let count = this.checkedRows.length
            return "Move " + count.toString() + " selected to ${'Archive' if request.matched_route.name == 'messages.inbox' else 'Inbox'}"
        }

        ${grid.vue_component}.methods.moveMessagesSubmit = function() {
            this.moveMessagesSubmitting = true
            this.moveMessagesText = "Working, please wait..."
        }

      </script>
  % endif
</%def>
