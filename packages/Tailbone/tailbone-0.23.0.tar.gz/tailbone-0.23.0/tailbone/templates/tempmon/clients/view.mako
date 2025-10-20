## -*- coding: utf-8; -*-
<%inherit file="/master/view.mako" />

<%def name="context_menu_items()">
  ${parent.context_menu_items()}
  % if request.has_perm('tempmon.appliances.dashboard'):
      <li>${h.link_to("Go to the Dashboard", url('tempmon.dashboard'))}</li>
  % endif
</%def>

<%def name="object_helpers()">
  % if instance.enabled and master.restartable_client(instance) and request.has_perm('{}.restart'.format(route_prefix)):
      <div class="object-helper">
        <h3>Client Tools</h3>
        <div class="object-helper-content">
          <once-button tag="a" href="${url('{}.restart'.format(route_prefix), uuid=instance.uuid)}"
                       type="is-primary"
                       text="Restart tempmon-client daemon">
          </once-button>
        </div>
      </div>
  % endif
</%def>

<%def name="modify_vue_vars()">
  ${parent.modify_vue_vars()}
  <script>
    ${form.vue_component}Data.probesData = ${json.dumps(probes_data)|n}
  </script>
</%def>
