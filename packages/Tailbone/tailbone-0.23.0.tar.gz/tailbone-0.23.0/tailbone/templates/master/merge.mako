## -*- coding: utf-8 -*-
<%inherit file="/page.mako" />

<%def name="title()">Merge 2 ${model_title_plural}</%def>

<%def name="extra_styles()">
  ${parent.extra_styles()}
  <style type="text/css">
    p {
        margin: 20px auto;
    }
    p.warning,
    p.warning strong {
        color: red;
    }
    a.merge-object {
        font-weight: bold;
    }

    table.diff {
        background-color: White;
        border-collapse: collapse;
        border-left: 1px solid black;
        border-top: 1px solid black;
        font-size: 11pt;
        margin-left: 50px;
        min-width: 80%;
    }

    table th,
    table td {
        border-bottom: 1px solid black;
        border-right: 1px solid black;
    }

    table td {
        padding: 5px 10px;
    }

    table td.value {
        font-family: monospace;
        white-space: pre;
    }

    table.diff tr.diff td.keep-value {
        background-color: #cfc;
    }
    table.diff tr.diff td.remove-value {
        background-color: #fcc;
    }
    table.diff td.result-value.diff {
        background-color: #fe8;
    }
    div.buttons {
        margin-top: 20px;
    }
  </style>
</%def>

<%def name="context_menu_items()">
  <li>${h.link_to("Back to {}".format(model_title_plural), url(route_prefix))}</li>
</%def>

<%def name="page_content()">
  <p>
    You are about to <strong>merge</strong> two ${model_title} records,
    (possibly) along with various related data.&nbsp; The tool you are using now
    is somewhat generic and is not able to give you the full picture of the
    implications of this merge.&nbsp; You are urged to proceed with caution!&nbsp;
  </p>

  <p class="warning">
    <strong>Unless you know what you're doing, a good rule of thumb (though still no
    guarantee) is to merge <em>only</em> if the "resulting" column is all-white.</strong>&nbsp;
    (You may be able to swap kept/removed in order to achieve this.)
  </p>

  <p>
    The ${h.link_to("{} on the left".format(model_title), view_url(object_to_remove), target='_blank', class_='merge-object')}
    will be <strong>deleted</strong>
    and the ${h.link_to("{} on the right".format(model_title), view_url(object_to_keep), target='_blank', class_='merge-object')}
    will be <strong>kept</strong>.&nbsp; The one which is to be kept may also
    be updated to reflect certain aspects of the one being deleted; however again
    the details are up to the app logic for this type of merge and aren't fully
    known to the generic tool which you're using now.
  </p>

  <table class="diff">
    <thead>
      <tr>
        <th>field name</th>
        <th>deleting ${model_title}</th>
        <th>keeping ${model_title}</th>
        <th>resulting ${model_title}</th>
      </tr>
    </thead>
    <tbody>
      % for field in sorted(merge_fields):
          <tr${' class="diff"' if keep_data[field] != remove_data[field] else ''|n}>
            <td class="field">${field}</td>
            <td class="value remove-value">${repr(remove_data[field])}</td>
            <td class="value keep-value">${repr(keep_data[field])}</td>
            <td class="value result-value${' diff' if resulting_data[field] != keep_data[field] else ''}">${repr(resulting_data[field])}</td>
          </tr>
      % endfor
    </tbody>
  </table>

  <merge-buttons></merge-buttons>
</%def>

<%def name="render_vue_templates()">
  ${parent.render_vue_templates()}

  <script type="text/x-template" id="merge-buttons-template">
    <div class="level" style="margin-top: 2em;">
      <div class="level-left">

        <div class="level-item">
          <a class="button" href="${index_url}">Whoops, nevermind</a>
        </div>

        <div class="level-item">
          ${h.form(request.current_route_url(), **{'@submit': 'submitSwapForm'})}
          ${h.csrf_token(request)}
          ${h.hidden('uuids', value=f'{keeping_uuid},{removing_uuid}')}
          <b-button native-type="submit"
                    :disabled="swapFormSubmitting">
            {{ swapFormButtonText }}
          </b-button>
          ${h.end_form()}
        </div>

        <div class="level-item">
          ${h.form(request.current_route_url(), **{'@submit': 'submitMergeForm'})}
          ${h.csrf_token(request)}
          ${h.hidden('uuids', value=f'{removing_uuid},{keeping_uuid}')}
          ${h.hidden('commit-merge', value='yes')}
          <b-button type="is-primary"
                    native-type="submit"
                    :disabled="mergeFormSubmitting">
            {{ mergeFormButtonText }}
          </b-button>
          ${h.end_form()}
        </div>

      </div>
    </div>
  </script>
  <script>

    const MergeButtons = {
        template: '#merge-buttons-template',
        data() {
            return {
                swapFormButtonText: "Swap which ${model_title} is kept/removed",
                swapFormSubmitting: false,
                mergeFormButtonText: "Yes, perform this merge",
                mergeFormSubmitting: false,
            }
        },
        methods: {
            submitSwapForm() {
                this.swapFormSubmitting = true
                this.swapFormButtonText = "Swapping, please wait..."
            },
            submitMergeForm() {
                this.mergeFormSubmitting = true
                this.mergeFormButtonText = "Merging, please wait..."
            },
        }
    }

  </script>
</%def>

<%def name="make_vue_components()">
  ${parent.make_vue_components()}
  <script>
    Vue.component('merge-buttons', MergeButtons)
    <% request.register_component('merge-buttons', 'MergeButtons') %>
  </script>
</%def>
