## -*- coding: utf-8; -*-
<%inherit file="/master/view.mako" />

## TODO: what was this about?
<%def name="content_title()">
  ## ${instance_title}
  #${instance.id} for ${instance.customer} (${enum.WORKORDER_STATUS[instance.status_code]})
</%def>

<%def name="object_helpers()">
  % if instance.status_code not in (enum.WORKORDER_STATUS_DELIVERED, enum.WORKORDER_STATUS_CANCELED):
      ${self.render_workflow_helper()}
  % endif
</%def>

<%def name="render_workflow_helper()">
  <nav class="panel">
    <p class="panel-heading">Workflow</p>

    % if instance.status_code == enum.WORKORDER_STATUS_SUBMITTED:
        <div class="panel-block">
          <div class="buttons">
            ${h.form(url('{}.receive'.format(route_prefix), uuid=instance.uuid), ref='receiveForm')}
            ${h.csrf_token(request)}
            <b-button type="is-primary"
                      icon-pack="fas"
                      icon-left="arrow-right"
                      @click="receive()"
                      :disabled="receiveButtonDisabled">
              {{ receiveButtonText }}
            </b-button>
            ${h.end_form()}
          </div>
        </div>
    % endif

    % if instance.status_code == enum.WORKORDER_STATUS_RECEIVED:
        <div class="panel-block">
          <div class="buttons">
            ${h.form(url('{}.await_estimate'.format(route_prefix), uuid=instance.uuid), ref='awaitEstimateForm')}
            ${h.csrf_token(request)}
            <b-button type="is-primary"
                      icon-pack="fas"
                      icon-left="arrow-right"
                      @click="awaitEstimate()"
                      :disabled="awaitEstimateButtonDisabled">
              {{ awaitEstimateButtonText }}
            </b-button>
            ${h.end_form()}
          </div>
        </div>
    % endif

    % if instance.status_code in (enum.WORKORDER_STATUS_RECEIVED, enum.WORKORDER_STATUS_PENDING_ESTIMATE):
        <div class="panel-block">
          <div class="buttons">
            ${h.form(url('{}.await_parts'.format(route_prefix), uuid=instance.uuid), ref='awaitPartsForm')}
            ${h.csrf_token(request)}
            <b-button type="is-primary"
                      icon-pack="fas"
                      icon-left="arrow-right"
                      @click="awaitParts()"
                      :disabled="awaitPartsButtonDisabled">
              {{ awaitPartsButtonText }}
            </b-button>
            ${h.end_form()}
          </div>
        </div>
    % endif

    % if instance.status_code in (enum.WORKORDER_STATUS_RECEIVED, enum.WORKORDER_STATUS_PENDING_ESTIMATE, enum.WORKORDER_STATUS_WAITING_FOR_PARTS):
        <div class="panel-block">
          <div class="buttons">
            ${h.form(url('{}.work_on_it'.format(route_prefix), uuid=instance.uuid), ref='workOnItForm')}
            ${h.csrf_token(request)}
            <b-button type="is-primary"
                      icon-pack="fas"
                      icon-left="arrow-right"
                      @click="workOnIt()"
                      :disabled="workOnItButtonDisabled">
              {{ workOnItButtonText }}
            </b-button>
            ${h.end_form()}
          </div>
        </div>
    % endif

    % if instance.status_code == enum.WORKORDER_STATUS_WORKING_ON_IT:
        <div class="panel-block">
          <div class="buttons">
            ${h.form(url('{}.release'.format(route_prefix), uuid=instance.uuid), ref='releaseForm')}
            ${h.csrf_token(request)}
            <b-button type="is-primary"
                      icon-pack="fas"
                      icon-left="arrow-right"
                      @click="release()"
                      :disabled="releaseButtonDisabled">
              {{ releaseButtonText }}
            </b-button>
            ${h.end_form()}
          </div>
        </div>
    % endif

    % if instance.status_code == enum.WORKORDER_STATUS_RELEASED:
        <div class="panel-block">
          <div class="buttons">
            ${h.form(url('{}.deliver'.format(route_prefix), uuid=instance.uuid), ref='deliverForm')}
            ${h.csrf_token(request)}
            <b-button type="is-primary"
                      icon-pack="fas"
                      icon-left="arrow-right"
                      @click="deliver()"
                      :disabled="deliverButtonDisabled">
              {{ deliverButtonText }}
            </b-button>
            ${h.end_form()}
          </div>
        </div>
    % endif

    % if instance.status_code not in (enum.WORKORDER_STATUS_DELIVERED, enum.WORKORDER_STATUS_CANCELED):
        <div class="panel-block">
          <p class="is-italic has-text-centered"
             style="width: 100%;">
            OR
          </p>
        </div>
        <div class="panel-block">
          <div class="buttons">
            ${h.form(url('{}.cancel'.format(route_prefix), uuid=instance.uuid), ref='cancelForm')}
            ${h.csrf_token(request)}
            <b-button type="is-warning"
                      icon-pack="fas"
                      icon-left="ban"
                      @click="confirmCancel()"
                      :disabled="cancelButtonDisabled">
              {{ cancelButtonText }}
            </b-button>
            ${h.end_form()}
          </div>
        </div>
    % endif

  </nav>
</%def>

<%def name="modify_vue_vars()">
  ${parent.modify_vue_vars()}
  <script>

    ThisPageData.receiveButtonDisabled = false
    ThisPageData.receiveButtonText = "I've received the order from customer"

    ThisPageData.awaitEstimateButtonDisabled = false
    ThisPageData.awaitEstimateButtonText = "I'm waiting for estimate confirmation"

    ThisPageData.awaitPartsButtonDisabled = false
    ThisPageData.awaitPartsButtonText = "I'm waiting for parts"

    ThisPageData.workOnItButtonDisabled = false
    ThisPageData.workOnItButtonText = "I'm working on it"

    ThisPageData.releaseButtonDisabled = false
    ThisPageData.releaseButtonText = "I've sent this back to customer"

    ThisPageData.deliverButtonDisabled = false
    ThisPageData.deliverButtonText = "Customer has the completed order!"

    ThisPageData.cancelButtonDisabled = false
    ThisPageData.cancelButtonText = "Cancel this Work Order"

    ThisPage.methods.receive = function() {
        this.receiveButtonDisabled = true
        this.receiveButtonText = "Working, please wait..."
        this.$refs.receiveForm.submit()
    }

    ThisPage.methods.awaitEstimate = function() {
        this.awaitEstimateButtonDisabled = true
        this.awaitEstimateButtonText = "Working, please wait..."
        this.$refs.awaitEstimateForm.submit()
    }

    ThisPage.methods.awaitParts = function() {
        this.awaitPartsButtonDisabled = true
        this.awaitPartsButtonText = "Working, please wait..."
        this.$refs.awaitPartsForm.submit()
    }

    ThisPage.methods.workOnIt = function() {
        this.workOnItButtonDisabled = true
        this.workOnItButtonText = "Working, please wait..."
        this.$refs.workOnItForm.submit()
    }

    ThisPage.methods.release = function() {
        this.releaseButtonDisabled = true
        this.releaseButtonText = "Working, please wait..."
        this.$refs.releaseForm.submit()
    }

    ThisPage.methods.deliver = function() {
        this.deliverButtonDisabled = true
        this.deliverButtonText = "Working, please wait..."
        this.$refs.deliverForm.submit()
    }

    ThisPage.methods.confirmCancel = function() {
        if (confirm("Are you sure you wish to cancel this Work Order?")) {
            this.cancelButtonDisabled = true
            this.cancelButtonText = "Working, please wait..."
            this.$refs.cancelForm.submit()
        }
    }

  </script>
</%def>
