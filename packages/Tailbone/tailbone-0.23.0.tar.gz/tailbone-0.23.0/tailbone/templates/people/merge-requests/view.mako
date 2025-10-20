## -*- coding: utf-8; -*-
<%inherit file="/master/view.mako" />

<%def name="page_content()">
  ${parent.page_content()}
  % if not instance.merged and request.has_perm('people.merge'):
      ${h.form(url('people.merge'), **{'@submit': 'submitMergeForm'})}
      ${h.csrf_token(request)}
      ${h.hidden('uuids', value=','.join([instance.removing_uuid, instance.keeping_uuid]))}
      <b-button type="is-primary"
                native-type="submit"
                :disabled="mergeFormSubmitting"
                icon-pack="fas"
                icon-left="object-ungroup">
        {{ mergeFormButtonText }}
      </b-button>
      ${h.end_form()}
  % endif
</%def>

<%def name="modify_vue_vars()">
  ${parent.modify_vue_vars()}
  % if not instance.merged and request.has_perm('people.merge'):
      <script>

        ThisPageData.mergeFormButtonText = "Perform Merge"
        ThisPageData.mergeFormSubmitting = false

        ThisPage.methods.submitMergeForm = function() {
            this.mergeFormButtonText = "Working, please wait..."
            this.mergeFormSubmitting = true
        }

      </script>
  % endif
</%def>
