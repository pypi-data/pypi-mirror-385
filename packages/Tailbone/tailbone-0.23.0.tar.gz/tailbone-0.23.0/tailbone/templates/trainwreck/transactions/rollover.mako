## -*- coding: utf-8; -*-
<%inherit file="/page.mako" />

<%def name="title()">${index_title} &raquo; Yearly Rollover</%def>

<%def name="content_title()">Yearly Rollover</%def>

<%def name="page_content()">
  <br />

  % if str(next_year) not in trainwreck_engines:
      <b-notification type="is-warning">
        You do not have a database configured for next year (${next_year}).&nbsp;
        You should be sure to configure it before next year rolls around.
      </b-notification>
  % endif

  <p class="block">
    The following Trainwreck databases are configured:
  </p>

  <b-table :data="engines">
    <b-table-column field="key"
                    label="DB Key"
                    v-slot="props">
      {{ props.row.key }}
    </b-table-column>
    <b-table-column field="oldest_date"
                    label="Oldest Date"
                    v-slot="props">
      <span v-if="props.row.error" class="has-text-danger">
        error
      </span>
      <span v-if="!props.row.error">
        {{ props.row.oldest_date }}
      </span>
    </b-table-column>
    <b-table-column field="newest_date"
                    label="Newest Date"
                    v-slot="props">
      <span v-if="props.row.error" class="has-text-danger">
        error
      </span>
      <span v-if="!props.row.error">
        {{ props.row.newest_date }}
      </span>
    </b-table-column>
  </b-table>
</%def>

<%def name="modify_vue_vars()">
  ${parent.modify_vue_vars()}
  <script>
    ThisPageData.engines = ${json.dumps(engines_data)|n}
  </script>
</%def>
