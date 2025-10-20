## -*- coding: utf-8; -*-
<%inherit file="/form.mako" />

<%def name="title()">Declare Credit for Row #${row.sequence}</%def>

<%def name="context_menu_items()">
  ${parent.context_menu_items()}
  % if master.rows_viewable and master.has_perm('view'):
      <li>${h.link_to("View this {}".format(row_model_title), row_action_url('view', row))}</li>
  % endif
</%def>

<%def name="render_form()">

  <p class="block">
    Please select the "state" of the product, and enter the
    appropriate quantity.
  </p>

  <p class="block">
    Note that this tool will
    <span class="has-text-weight-bold">deduct</span> from the
    "received" quantity, and
    <span class="has-text-weight-bold">add</span> to the
    corresponding credit quantity.
  </p>

  <p class="block">
    Please see ${h.link_to("Receive Row", url('{}.receive_row'.format(route_prefix), uuid=batch.uuid, row_uuid=row.uuid))}
    if you need to "receive" instead of "convert" the product.
  </p>

  ${parent.render_form()}

</%def>

<%def name="form_body()">

  ${form.render_field_complete('credit_type')}

  ${form.render_field_complete('quantity')}

  ${form.render_field_complete('expiration_date', bfield_attrs={'v-show': "field_model_credit_type == 'expired'"})}

</%def>

<%def name="render_form_template()">
  ${form.render_deform(buttons=capture(self.render_form_buttons), form_body=capture(self.form_body))|n}
</%def>


${parent.body()}
