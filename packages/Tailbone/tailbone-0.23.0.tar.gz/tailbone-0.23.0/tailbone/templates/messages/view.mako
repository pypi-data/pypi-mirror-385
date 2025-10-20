## -*- coding: utf-8; -*-
<%inherit file="/master/view.mako" />

<%def name="extra_styles()">
  ${parent.extra_styles()}
  <style type="text/css">
    .everyone {
        cursor: pointer;
    }
    .tailbone-message-body {
        margin: 1rem auto;
        min-height: 10rem;
    }
    .tailbone-message-body p {
        margin-bottom: 1rem;
    }
  </style>
</%def>

<%def name="context_menu_items()">
  % if request.has_perm('messages.create'):
      <li>${h.link_to("Send a new Message", url('messages.create'))}</li>
  % endif
  % if recipient:
      % if recipient.status == enum.MESSAGE_STATUS_INBOX:
          <li>${h.link_to("Back to Message Inbox", url('messages.inbox'))}</li>
          <li>${h.link_to("Go to my Message Archive", url('messages.archive'))}</li>
          <li>${h.link_to("Go to my Sent Messages", url('messages.sent'))}</li>
      % else:
          <li>${h.link_to("Back to Message Archive", url('messages.archive'))}</li>
          <li>${h.link_to("Go to my Message Inbox", url('messages.inbox'))}</li>
          <li>${h.link_to("Go to my Sent Messages", url('messages.sent'))}</li>
      % endif
  % else:
      <li>${h.link_to("Back to Sent Messages", url('messages.sent'))}</li>
      <li>${h.link_to("Go to my Message Inbox", url('messages.inbox'))}</li>
      <li>${h.link_to("Go to my Message Archive", url('messages.archive'))}</li>
  % endif
</%def>

<%def name="message_tools()">
  % if recipient:
      <div class="buttons">
        % if request.has_perm('messages.create'):
            <once-button type="is-primary"
                         tag="a" href="${url('messages.reply', uuid=instance.uuid)}"
                         text="Reply">
            </once-button>
            <once-button type="is-primary"
                         tag="a" href="${url('messages.reply_all', uuid=instance.uuid)}"
                         text="Reply to All">
            </once-button>
        % endif
        % if recipient.status == enum.MESSAGE_STATUS_INBOX:
            <once-button type="is-primary"
                         tag="a" href="${url('messages.move', uuid=instance.uuid)}?dest=archive"
                         text="Move to Archive">
            </once-button>
        % else:
            <once-button type="is-primary"
                         tag="a" href="${url('messages.move', uuid=instance.uuid)}?dest=inbox"
                         text="Move to Inbox">
            </once-button>
        % endif
      </div>
  % endif
</%def>

<%def name="message_body()">
  ${instance.body}
</%def>

<%def name="page_content()">
  ${parent.page_content()}
  <br />
  <div style="margin-left: 5rem;">
    ${self.message_tools()}
    <div class="tailbone-message-body">
      ${self.message_body()}
    </div>
    ${self.message_tools()}
  </div>
</%def>

<%def name="modify_vue_vars()">
  ${parent.modify_vue_vars()}
  <script>

    ${form.vue_component}Data.showingAllRecipients = false

    ${form.vue_component}.methods.showMoreRecipients = function() {
        this.showingAllRecipients = true
    }

    ${form.vue_component}.methods.hideMoreRecipients = function() {
        this.showingAllRecipients = false
    }

  </script>
</%def>
