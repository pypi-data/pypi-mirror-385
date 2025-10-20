## -*- coding: utf-8; -*-
<%inherit file="/master/create.mako" />
<%namespace file="/messages/recipients.mako" import="message_recipients_template" />

<%def name="content_title()"></%def>

<%def name="extra_javascript()">
  ${parent.extra_javascript()}
  ${h.javascript_link(request.static_url('tailbone:static/js/tailbone.buefy.message_recipients.js'))}
</%def>

<%def name="extra_styles()">
  ${parent.extra_styles()}
  <style type="text/css">

    .this-page-content {
      width: 100%;
    }

    .this-page-content .buttons {
        margin-left: 20rem;
    }

  </style>
</%def>

<%def name="context_menu_items()">
  % if request.has_perm('messages.list'):
      <li>${h.link_to("Go to my Message Inbox", url('messages.inbox'))}</li>
      <li>${h.link_to("Go to my Message Archive", url('messages.archive'))}</li>
      <li>${h.link_to("Go to my Sent Messages", url('messages.sent'))}</li>
  % endif
</%def>

<%def name="render_vue_templates()">
  ${parent.render_vue_templates()}
  ${message_recipients_template()}
</%def>

<%def name="modify_vue_vars()">
  ${parent.modify_vue_vars()}
  <script>

    TailboneFormData.possibleRecipients = new Map(${json.dumps(available_recipients)|n})
    TailboneFormData.recipientDisplayMap = ${json.dumps(recipient_display_map)|n}

    TailboneForm.methods.subjectKeydown = function(event) {

        // do not auto-submit form when user presses enter in subject field
        if (event.which == 13) {
            event.preventDefault()

            // set focus to msg body input if possible
            if (this.$refs.messageBody && this.$refs.messageBody.focus) {
                this.$refs.messageBody.focus()
            }
        }
    }

  </script>
</%def>
