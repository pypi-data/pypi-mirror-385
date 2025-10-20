## -*- coding: utf-8; -*-
<%inherit file="/batch/worksheet.mako" />

<%def name="title()">Ordering Worksheet</%def>

<%def name="extra_styles()">
  ${parent.extra_styles()}
  <style type="text/css">

    .order-form th.department {
        border-top: 1px solid black;
        font-size: 1.2em;
        padding: 15px;
        text-align: left;
        text-transform: uppercase;
    }

    .order-form th.subdepartment {
        background-color: white;
        border-bottom: 1px solid black;
        border-top: 1px solid black;
        padding: 15px;
        text-align: left;
    }

    .order-form tr.active {
        border: 5px solid Blue;
    }

    .order-form td {
        border-right: 1px solid #000000;
        border-top: 1px solid #000000;
    }

    .order-form td.upc,
    .order-form td.case-qty,
    .order-form td.code,
    .order-form td.preferred,
    .order-form td.scratch_pad {
        text-align: center;
    }

    .order-form td.scratch_pad {
        width: 40px;
    }

    .order-form td.current-order input {
        text-align: center;
        width: 3em;
    }

    .order-form td.unit-cost,
    .order-form td.po-total {
        text-align: right;
    }

  </style>
</%def>

<%def name="context_menu_items()">
  <li>${h.link_to("Back to {}".format(model_title), url('ordering.view', uuid=batch.uuid))}</li>
</%def>

<%def name="extra_vendor_fields()"></%def>

<%def name="extra_count()">0</%def>

<%def name="extra_th()"></%def>

<%def name="extra_td(cost)"></%def>

<%def name="order_form_grid()">
  <div class="grid">
    <table class="order-form">
      <% column_count = 8 + len(header_columns) + (0 if ignore_cases else 1) + int(capture(self.extra_count)) %>
      % for department in sorted(departments.values(), key=lambda d: d.name if d else ''):
          <thead>
            <tr>
              <th class="department" colspan="${column_count}">Department
                % if department.number or department.name:
                    ${department.number} ${department.name}
                % else:
                    (N/A)
                % endif
              </th>
            </tr>
            % for subdepartment in sorted(department._order_subdepartments.values(), key=lambda s: s.name if s else ''):
                <tr>
                  <th class="subdepartment" colspan="${column_count}">Subdepartment
                    % if subdepartment.number or subdepartment.name:
                        ${subdepartment.number} ${subdepartment.name}
                    % else:
                        (N/A)
                    % endif
                  </th>
                </tr>
                <tr>
                  % for title in header_columns:
                      <th>${title}</th>
                  % endfor
                  % for data in history:
                      <th>
                        % if data:
                            % if data['purchase']['date_received']:
                                Rec.<br />
                                ${data['purchase']['date_received'].strftime('%m/%d')}
                            % elif data['purchase']['date_ordered']:
                                Ord.<br />
                                ${data['purchase']['date_ordered'].strftime('%m/%d')}
                            % else:
                                ??
                            % endif
                        % endif
                      </th>
                  % endfor
                  % if not ignore_cases:
                      <th>
                        ${order_date.strftime('%m/%d')}<br />
                        Cases
                      </th>
                  % endif
                  <th>
                    ${order_date.strftime('%m/%d')}<br />
                    Units
                  </th>
                  <th>PO Total</th>
                  ${self.extra_th()}
                </tr>
              </thead>
              <tbody>
                % for i, cost in enumerate(subdepartment._order_costs, 1):
                    <tr data-uuid="${cost.product_uuid}" class="${'even' if i % 2 == 0 else 'odd'}"
                        :class="{active: activeUUID == '${cost.uuid}'}">
                      ${self.order_form_row(cost)}
                      % for data in history:
                          <td class="scratch_pad">
                            % if data:
                                <% item = data['items'].get(cost.product_uuid) %>
                                % if item:
                                    % if ignore_cases:
                                        % if item['units_received'] is not None:
                                            ${int(item['units_received'] or 0)}
                                        % elif item['units_ordered'] is not None:
                                            ${int(item['units_ordered'] or 0)}
                                        % endif
                                    % else:
                                        % if item['cases_received'] is not None or item['units_received'] is not None:
                                            ${'{} / {}'.format(int(item['cases_received'] or 0), int(item['units_received'] or 0))}
                                        % elif item['cases_ordered'] is not None or item['units_ordered'] is not None:
                                            ${'{} / {}'.format(int(item['cases_ordered'] or 0), int(item['units_ordered'] or 0))}
                                        % endif
                                    % endif
                                % endif
                            % endif
                          </td>
                      % endfor
                      % if not ignore_cases:
                          <td class="current-order">
                            <numeric-input v-model="worksheet.cost_${cost.uuid}_cases"
                                           @focus="activeUUID = '${cost.uuid}'; $event.target.select()"
                                           @blur="activeUUID = null"
                                           @keydown.native="inputKeydown($event, '${cost.uuid}', '${cost.product_uuid}')">
                            </numeric-input>
                          </td>
                      % endif
                      <td class="current-order">
                        <numeric-input v-model="worksheet.cost_${cost.uuid}_units"
                                       @focus="activeUUID = '${cost.uuid}'; $event.target.select()"
                                       @blur="activeUUID = null"
                                       @keydown.native="inputKeydown($event, '${cost.uuid}', '${cost.product_uuid}')">
                        </numeric-input>
                      </td>
                      <td class="po-total">{{ worksheet.cost_${cost.uuid}_total_display }}</td>
                      ${self.extra_td(cost)}
                    </tr>
                % endfor
              </tbody>
          % endfor
      % endfor
    </table>
  </div>
</%def>

<%def name="order_form_row(cost)">
  <td class="upc">${get_upc(cost.product)}</td>
  <td class="brand">${cost.product.brand or ''}</td>
  <td class="desc">${cost.product.description} ${cost.product.size or ''}</td>
  <td class="case-qty">${h.pretty_quantity(cost.case_size)} ${"LB" if cost.product.weighed else "EA"}</td>
  <td class="code">${cost.code or ''}</td>
  <td class="preferred">${'X' if cost.preference == 1 else ''}</td>
  <td class="unit-cost">
    % if cost.unit_cost is not None:
        $${'{:0.2f}'.format(cost.unit_cost)}
    % endif
  </td>
</%def>

<%def name="page_content()">
  <ordering-worksheet></ordering-worksheet>
</%def>

<%def name="render_vue_templates()">
  ${parent.render_vue_templates()}
  <script type="text/x-template" id="ordering-worksheet-template">
    <div>
      <div class="form-wrapper">
        <div class="form">

          <b-field horizontal label="Vendor">
            ${h.link_to(vendor, url('vendors.view', uuid=vendor.uuid))}
          </b-field>

          <b-field horizontal label="Vendor Email">
            <span>${vendor.email or ''}</span>
          </b-field>

          <b-field horizontal label="Vendor Fax">
            <span>${vendor.fax_number or ''}</span>
          </b-field>

          <b-field horizontal label="Vendor Contact">
            <span>${vendor.contact or ''}</span>
          </b-field>

          <b-field horizontal label="Vendor Phone">
            <span>${vendor.phone or ''}</span>
          </b-field>

          ${self.extra_vendor_fields()}

          <b-field horizontal label="PO Total">
            <span>{{ poTotalDisplay }}</span>
          </b-field>

        </div> <!-- form -->
      </div><!-- form-wrapper -->

      ${self.order_form_grid()}
    </div>
  </script>
  <script>

    const OrderingWorksheet = {
        template: '#ordering-worksheet-template',
        data() {
            return {
                worksheet: ${json.dumps(worksheet_data)|n},
                activeUUID: null,
                poTotalDisplay: "$${'{:0,.2f}'.format(batch.po_total_calculated or batch.po_total or 0)}",
                submitting: false,

                ## TODO: should find a better way to handle CSRF token
                csrftoken: ${json.dumps(h.get_csrf_token(request))|n},
            }
        },
        methods: {

            inputKeydown(event, cost_uuid, product_uuid) {
                if (event.which == 13) {
                    if (!this.submitting) {
                        this.submitting = true

                        let url = '${url('ordering.worksheet_update', uuid=batch.uuid)}'

                        let params = {
                            product_uuid: product_uuid,
                            % if not ignore_cases:
                            cases_ordered: this.worksheet['cost_' + cost_uuid + '_cases'],
                            % endif
                            units_ordered: this.worksheet['cost_' + cost_uuid + '_units'],
                        }

                        let headers = {
                            ## TODO: should find a better way to handle CSRF token
                            'X-CSRF-TOKEN': this.csrftoken,
                        }

                        ## TODO: should find a better way to handle CSRF token
                        this.$http.post(url, params, {headers: headers}).then(response => {
                            if (response.data.error) {
                                alert(response.data.error)
                            } else {
                                this.worksheet['cost_' + cost_uuid + '_cases'] = response.data.row_cases_ordered
                                this.worksheet['cost_' + cost_uuid + '_units'] = response.data.row_units_ordered
                                this.worksheet['cost_' + cost_uuid + '_total_display'] = response.data.row_po_total_display
                                this.poTotalDisplay = response.data.batch_po_total_display
                            }
                            this.submitting = false
                        })
                    }
                }
            },
        },
    }

  </script>
</%def>

<%def name="make_vue_components()">
  ${parent.make_vue_components()}
  <script>
    Vue.component('ordering-worksheet', OrderingWorksheet)
  </script>
</%def>
