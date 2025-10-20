## -*- coding: utf-8; -*-
<%inherit file="/master/view.mako" />

<%def name="extra_styles()">
  ${parent.extra_styles()}
  <style type="text/css">
    .card.personal {
        margin-bottom: 1rem;
    }
    .field.is-horizontal .field-label .label {
        white-space: nowrap;
        min-width: 10rem;
    }
  </style>
</%def>

<%def name="content_title()">
  ${dynamic_content_title or str(instance)}
</%def>

<%def name="render_instance_header_title_extras()">
  % if request.has_perm('people_profile.view_versions'):
      <div class="level-item" style="margin-left: 2rem;">
        <b-button v-if="!viewingHistory"
                  icon-pack="fas"
                  icon-left="history"
                  @click="viewHistory()">
          View History
        </b-button>
        <div v-if="viewingHistory"
             class="buttons">
          <b-button icon-pack="fas"
                    icon-left="user"
                    @click="viewingHistory = false">
            View Profile
          </b-button>
          <b-button icon-pack="fas"
                    icon-left="redo"
                    @click="refreshHistory()"
                    :disabled="gettingRevisions">
            {{ gettingRevisions ? "Working, please wait..." : "Refresh History" }}
          </b-button>
        </div>
      </div>
  % endif
</%def>

<%def name="page_content()">
  <profile-info @change-content-title="changeContentTitle"
                % if request.has_perm('people_profile.view_versions'):
                :viewing-history="viewingHistory"
                :getting-revisions="gettingRevisions"
                :revisions="revisions"
                :revision-version-map="revisionVersionMap"
                % endif
                >
  </profile-info>
</%def>

<%def name="render_this_page_component()">
  ## TODO: should override this in a cleaner way!  too much duplicate code w/ parent template
  <this-page @change-content-title="changeContentTitle"
             % if can_edit_help:
             :configure-fields-help="configureFieldsHelp"
             % endif
             % if request.has_perm('people_profile.view_versions'):
             :viewing-history="viewingHistory"
             :getting-revisions="gettingRevisions"
             :revisions="revisions"
             :revision-version-map="revisionVersionMap"
             % endif
             >
  </this-page>
</%def>

<%def name="render_this_page()">
  ${self.page_content()}
</%def>

<%def name="render_personal_name_card()">
  <div class="card personal"
        ## nb. hack to force refresh for vue3
       :key="refreshPersonalCard">
    <header class="card-header">
      <p class="card-header-title">Name</p>
    </header>
    <div class="card-content">
      <div class="content">
        <div style="display: flex; justify-content: space-between;">
          <div style="flex-grow: 1; margin-right: 1rem;">

            <b-field horizontal label="First Name">
              <span>{{ person.first_name }}</span>
            </b-field>

            % if use_preferred_first_name:
                <b-field horizontal label="Preferred First Name">
                  <span>{{ person.preferred_first_name }}</span>
                </b-field>
            % endif

            <b-field horizontal label="Middle Name">
              <span>{{ person.middle_name }}</span>
            </b-field>

            <b-field horizontal label="Last Name">
              <span>{{ person.last_name }}</span>
            </b-field>

          </div>
          % if request.has_perm('people_profile.edit_person'):
              <div v-if="editNameAllowed()">
                <b-button type="is-primary"
                          @click="editNameInit()"
                          icon-pack="fas"
                          icon-left="edit">
                  Edit Name
                </b-button>
              </div>
              <${b}-modal has-modal-card
                          % if request.use_oruga:
                              v-model:active="editNameShowDialog"
                          % else:
                              :active.sync="editNameShowDialog"
                          % endif
                          >
                <div class="modal-card">

                  <header class="modal-card-head">
                    <p class="modal-card-title">Edit Name</p>
                  </header>

                  <section class="modal-card-body">

                    % if use_preferred_first_name:
                        <b-field grouped>
                          <b-field label="First Name">
                            <b-input v-model.trim="editNameFirst"
                                     :maxlength="maxLengths.person_first_name || null" />
                          </b-field>
                          <b-field label="Preferred First Name" expanded>
                            <b-input v-model.trim="editNameFirstPreferred"
                                     :maxlength="maxLengths.person_preferred_first_name || null">
                            </b-input>
                          </b-field>
                        </b-field>
                    % else:
                        <b-field label="First Name">
                          <b-input v-model.trim="editNameFirst"
                                   :maxlength="maxLengths.person_first_name || null"
                                   expanded />
                        </b-field>
                    % endif

                    <b-field label="Middle Name">
                      <b-input v-model.trim="editNameMiddle"
                               :maxlength="maxLengths.person_middle_name || null"
                               expanded />
                    </b-field>
                    <b-field label="Last Name">
                      <b-input v-model.trim="editNameLast"
                               :maxlength="maxLengths.person_last_name || null"
                               expanded />
                    </b-field>
                  </section>

                  <footer class="modal-card-foot">
                    <b-button type="is-primary"
                              @click="editNameSave()"
                              :disabled="editNameSaveDisabled"
                              icon-pack="fas"
                              icon-left="save">
                      {{ editNameSaving ? "Working, please wait..." : "Save" }}
                    </b-button>
                    <b-button @click="editNameShowDialog = false">
                      Cancel
                    </b-button>
                  </footer>
                </div>
              </${b}-modal>
          % endif
        </div>
      </div>
    </div>
  </div>
</%def>

<%def name="render_personal_address_card()">
  <div class="card personal"
       ## nb. hack to force refresh for vue3
       :key="refreshAddressCard">
    <header class="card-header">
      <p class="card-header-title">Address</p>
    </header>
    <div class="card-content">
      <div class="content">
        <div style="display: flex; justify-content: space-between;">
          <div style="flex-grow: 1; margin-right: 1rem;">

            <b-field horizontal label="Street 1">
              <span>{{ person.address ? person.address.street : null }}</span>
            </b-field>

            <b-field horizontal label="Street 2">
              <span>{{ person.address ? person.address.street2 : null }}</span>
            </b-field>

            <b-field horizontal label="City">
              <span>{{ person.address ? person.address.city : null }}</span>
            </b-field>

            <b-field horizontal label="State">
              <span>{{ person.address ? person.address.state : null }}</span>
            </b-field>

            <b-field horizontal label="Zipcode">
              <span>{{ person.address ? person.address.zipcode : null }}</span>
            </b-field>

            <b-field v-if="person.address && person.address.invalid"
                     horizontal label="Invalid"
                     class="has-text-danger">
              <span>Yes</span>
            </b-field>

          </div>
          % if request.has_perm('people_profile.edit_person'):
              <b-button type="is-primary"
                        @click="editAddressInit()"
                        icon-pack="fas"
                        icon-left="edit">
                Edit Address
              </b-button>
              <${b}-modal has-modal-card
                          % if request.use_oruga:
                              v-model:active="editAddressShowDialog"
                          % else:
                              :active.sync="editAddressShowDialog"
                          % endif
                          >
                <div class="modal-card">

                  <header class="modal-card-head">
                    <p class="modal-card-title">Edit Address</p>
                  </header>

                  <section class="modal-card-body">

                    <b-field label="Street 1" expanded>
                      <b-input v-model.trim="editAddressStreet1"
                               :maxlength="maxLengths.address_street || null"
                               expanded />
                    </b-field>

                    <b-field label="Street 2" expanded>
                      <b-input v-model.trim="editAddressStreet2"
                               :maxlength="maxLengths.address_street2 || null"
                               expanded />
                    </b-field>

                    <b-field label="Zipcode">
                      <b-input v-model.trim="editAddressZipcode"
                               :maxlength="maxLengths.address_zipcode || null"
                               expanded />
                    </b-field>

                    <b-field grouped>
                      <b-field label="City">
                        <b-input v-model.trim="editAddressCity"
                                 :maxlength="maxLengths.address_city || null">
                        </b-input>
                      </b-field>
                      <b-field label="State">
                        <b-input v-model.trim="editAddressState"
                                 :maxlength="maxLengths.address_state || null">
                        </b-input>
                      </b-field>
                    </b-field>

                    <b-field label="Invalid">
                      <b-checkbox v-model="editAddressInvalid"
                                  type="is-danger">
                      </b-checkbox>
                    </b-field>

                  </section>

                  <footer class="modal-card-foot">
                    <once-button type="is-primary"
                                 @click="editAddressSave()"
                                 :disabled="editAddressSaveDisabled"
                                 icon-left="save"
                                 text="Save">
                    </once-button>
                    <b-button @click="editAddressShowDialog = false">
                      Cancel
                    </b-button>
                  </footer>
                </div>
              </${b}-modal>
          % endif
        </div>
      </div>
    </div>
  </div>
</%def>

<%def name="render_personal_phone_card()">
  <div class="card personal">
    <header class="card-header">
      <p class="card-header-title">Phone(s)</p>
    </header>
    <div class="card-content">
      <div class="content">

        <b-notification v-if="person.invalid_phone_number"
                        type="is-warning"
                        has-icon icon-pack="fas"
                        :closable="false">
          We appear to have an invalid phone number on file for this person.
        </b-notification>

        % if request.has_perm('people_profile.edit_person'):
            <div class="has-text-right">
              <b-button type="is-primary"
                        icon-pack="fas"
                        icon-left="plus"
                        @click="addPhoneInit()">
                Add Phone
              </b-button>
            </div>
            <${b}-modal has-modal-card
                        % if request.use_oruga:
                            v-model:active="editPhoneShowDialog"
                        % else:
                            :active.sync="editPhoneShowDialog"
                        % endif
                        >
              <div class="modal-card">

                <header class="modal-card-head">
                  <p class="modal-card-title">
                    {{ editPhoneUUID ? "Edit" : "Add" }} Phone
                  </p>
                </header>

                <section class="modal-card-body">

                  <b-field label="Type">
                    <b-select v-model="editPhoneType">
                      <option v-for="option in phoneTypeOptions"
                              :key="option.value"
                              :value="option.value">
                        {{ option.label }}
                      </option>
                    </b-select>
                  </b-field>

                  <b-field label="Number">
                    <b-input v-model.trim="editPhoneNumber"
                             ref="editPhoneInput"
                             expanded />
                  </b-field>

                  <b-field label="Preferred?">
                    <b-checkbox v-model="editPhonePreferred">
                    </b-checkbox>
                  </b-field>

                </section>

                <footer class="modal-card-foot">
                  <b-button type="is-primary"
                            @click="editPhoneSave()"
                            :disabled="editPhoneSaveDisabled"
                            icon-pack="fas"
                            icon-left="save">
                    {{ editPhoneSaving ? "Working..." : "Save" }}
                  </b-button>
                  <b-button @click="editPhoneShowDialog = false">
                    Cancel
                  </b-button>
                </footer>
              </div>
            </${b}-modal>
        % endif

        <${b}-table :data="person.phones">

          <${b}-table-column field="preference"
                          label="Preferred"
                          v-slot="props">
            {{ props.row.preferred ? "Yes" : "" }}
          </${b}-table-column>

          <${b}-table-column field="type"
                          label="Type"
                          v-slot="props">
            {{ props.row.type }}
          </${b}-table-column>

          <${b}-table-column field="number"
                          label="Number"
                          v-slot="props">
            {{ props.row.number }}
          </${b}-table-column>

          % if request.has_perm('people_profile.edit_person'):
          <${b}-table-column label="Actions"
                          v-slot="props">
            <a href="#" @click.prevent="editPhoneInit(props.row)"
               % if not request.use_oruga:
                   class="grid-action"
               % endif
               >
              % if request.use_oruga:
                  <span class="icon-text">
                    <o-icon icon="edit" />
                    <span>Edit</span>
                  </span>
              % else:
                  <i class="fas fa-edit"></i>
                  Edit
              % endif
            </a>
            <a href="#" @click.prevent="deletePhoneInit(props.row)"
               % if request.use_oruga:
                   class="has-text-danger"
               % else:
                   class="grid-action has-text-danger"
               % endif
               >
              % if request.use_oruga:
                  <span class="icon-text">
                    <o-icon icon="trash" />
                    <span>Delete</span>
                  </span>
              % else:
                  <i class="fas fa-trash"></i>
                  Delete
              % endif
            </a>
            <a v-if="!props.row.preferred"
               href="#" @click.prevent="preferPhoneInit(props.row)"
               % if not request.use_oruga:
                   class="grid-action"
               % endif
               >
              % if request.use_oruga:
                  <span class="icon-text">
                    <o-icon icon="star" />
                    <span>Set Preferred</span>
                  </span>
              % else:
                  <i class="fas fa-star"></i>
                  Set Preferred
              % endif
            </a>
          </${b}-table-column>
          % endif

        </${b}-table>

        % if request.has_perm('people_profile.edit_person'):

            <${b}-modal has-modal-card
                        % if request.use_oruga:
                            v-model:active="deletePhoneShowDialog"
                        % else:
                            :active.sync="deletePhoneShowDialog"
                        % endif
                        >
              <div class="modal-card">

                <header class="modal-card-head">
                  <p class="modal-card-title">Delete Phone</p>
                </header>

                <section class="modal-card-body">
                  <p class="block">Really delete this phone number?</p>
                  <p class="block has-text-weight-bold">{{ deletePhoneNumber }}</p>
                </section>

                <footer class="modal-card-foot">
                  <b-button type="is-danger"
                            @click="deletePhoneSave()"
                            :disabled="deletePhoneSaving"
                            icon-pack="fas"
                            icon-left="trash">
                    {{ deletePhoneSaving ? "Working, please wait..." : "Delete" }}
                  </b-button>
                  <b-button @click="deletePhoneShowDialog = false">
                    Cancel
                  </b-button>
                </footer>
              </div>
            </${b}-modal>

            <${b}-modal has-modal-card
                        % if request.use_oruga:
                            v-model:active="preferPhoneShowDialog"
                        % else:
                            :active.sync="preferPhoneShowDialog"
                        % endif
                        >
              <div class="modal-card">

                <header class="modal-card-head">
                  <p class="modal-card-title">Set Preferred Phone</p>
                </header>

                <section class="modal-card-body">
                  <p class="block">Really make this the preferred phone number?</p>
                  <p class="block has-text-weight-bold">{{ preferPhoneNumber }}</p>
                </section>

                <footer class="modal-card-foot">
                  <b-button type="is-primary"
                            @click="preferPhoneSave()"
                            :disabled="preferPhoneSaving"
                            icon-pack="fas"
                            icon-left="save">
                    {{ preferPhoneSaving ? "Working, please wait..." : "Set Preferred" }}
                  </b-button>
                  <b-button @click="preferPhoneShowDialog = false">
                    Cancel
                  </b-button>
                </footer>
              </div>
            </${b}-modal>

        % endif
      </div>
    </div>
  </div>
</%def>

<%def name="render_personal_email_card()">
  <div class="card personal">
    <header class="card-header">
      <p class="card-header-title">Email(s)</p>
    </header>
    <div class="card-content">
      <div class="content">

        % if request.has_perm('people_profile.edit_person'):
            <div class="has-text-right">
              <b-button type="is-primary"
                        icon-pack="fas"
                        icon-left="plus"
                        @click="addEmailInit()">
                Add Email
              </b-button>
            </div>
            <${b}-modal has-modal-card
                        % if request.use_oruga:
                            v-model:active="editEmailShowDialog"
                        % else:
                            :active.sync="editEmailShowDialog"
                        % endif
                        >
              <div class="modal-card">

                <header class="modal-card-head">
                  <p class="modal-card-title">
                    {{ editEmailUUID ? "Edit" : "Add" }} Email
                  </p>
                </header>

                <section class="modal-card-body">

                  <b-field label="Type">
                    <b-select v-model="editEmailType">
                      <option v-for="option in emailTypeOptions"
                              :key="option.value"
                              :value="option.value">
                        {{ option.label }}
                      </option>
                    </b-select>
                  </b-field>

                  <b-field label="Address">
                    <b-input v-model.trim="editEmailAddress"
                             ref="editEmailInput"
                             expanded />
                  </b-field>

                  <b-field v-if="!editEmailUUID"
                           label="Preferred?">
                    <b-checkbox v-model="editEmailPreferred">
                    </b-checkbox>
                  </b-field>

                  <b-field v-if="editEmailUUID"
                           label="Invalid?">
                    <b-checkbox v-model="editEmailInvalid"
                                :type="editEmailInvalid ? 'is-danger': null">
                    </b-checkbox>
                  </b-field>

                </section>

                <footer class="modal-card-foot">
                  <b-button type="is-primary"
                            @click="editEmailSave()"
                            :disabled="editEmailSaveDisabled"
                            icon-pack="fas"
                            icon-left="save">
                    {{ editEmailSaving ? "Working, please wait..." : "Save" }}
                  </b-button>
                  <b-button @click="editEmailShowDialog = false">
                    Cancel
                  </b-button>
                </footer>
              </div>
            </${b}-modal>
        % endif

        <${b}-table :data="person.emails">

          <${b}-table-column field="preference"
                          label="Preferred"
                          v-slot="props">
            {{ props.row.preferred ? "Yes" : "" }}
          </${b}-table-column>

          <${b}-table-column field="type"
                          label="Type"
                          v-slot="props">
            {{ props.row.type }}
          </${b}-table-column>

          <${b}-table-column field="address"
                          label="Address"
                          v-slot="props">
            {{ props.row.address }}
          </${b}-table-column>

          <${b}-table-column field="invalid"
                          label="Invalid?"
                          v-slot="props">
            <span v-if="props.row.invalid" class="has-text-danger has-text-weight-bold">Invalid</span>
          </${b}-table-column>

          % if request.has_perm('people_profile.edit_person'):
              <${b}-table-column label="Actions"
                              v-slot="props">
                <a href="#" @click.prevent="editEmailInit(props.row)"
                   % if not request.use_oruga:
                       class="grid-action"
                   % endif
                   >
                  % if request.use_oruga:
                      <span class="icon-text">
                        <o-icon icon="edit" />
                        <span>Edit</span>
                      </span>
                  % else:
                      <i class="fas fa-edit"></i>
                      Edit
                  % endif
                </a>
                <a href="#" @click.prevent="deleteEmailInit(props.row)"
                   % if request.use_oruga:
                       class="has-text-danger"
                   % else:
                       class="grid-action has-text-danger"
                   % endif
                   >
                  % if request.use_oruga:
                      <span class="icon-text">
                        <o-icon icon="trash" />
                        <span>Delete</span>
                      </span>
                  % else:
                      <i class="fas fa-trash"></i>
                      Delete
                  % endif
                </a>
                <a v-if="!props.row.preferred"
                   % if not request.use_oruga:
                       class="grid-action"
                   % endif
                   href="#" @click.prevent="preferEmailInit(props.row)">
                  % if request.use_oruga:
                      <span class="icon-text">
                        <o-icon icon="star" />
                        <span>Set Preferred</span>
                      </span>
                  % else:
                      <i class="fas fa-star"></i>
                      Set Preferred
                  % endif
                </a>
              </${b}-table-column>
          % endif

        </${b}-table>

        % if request.has_perm('people_profile.edit_person'):

            <${b}-modal has-modal-card
                        % if request.use_oruga:
                            v-model:active="deleteEmailShowDialog"
                        % else:
                            :active.sync="deleteEmailShowDialog"
                        % endif
                        >
              <div class="modal-card">

                <header class="modal-card-head">
                  <p class="modal-card-title">Delete Email</p>
                </header>

                <section class="modal-card-body">
                  <p class="block">Really delete this email address?</p>
                  <p class="block has-text-weight-bold">{{ deleteEmailAddress }}</p>
                </section>

                <footer class="modal-card-foot">
                  <b-button type="is-danger"
                            @click="deleteEmailSave()"
                            :disabled="deleteEmailSaving"
                            icon-pack="fas"
                            icon-left="trash">
                    {{ deleteEmailSaving ? "Working, please wait..." : "Delete" }}
                  </b-button>
                  <b-button @click="deleteEmailShowDialog = false">
                    Cancel
                  </b-button>
                </footer>
              </div>
            </${b}-modal>

            <${b}-modal has-modal-card
                        % if request.use_oruga:
                            v-model:active="preferEmailShowDialog"
                        % else:
                            :active.sync="preferEmailShowDialog"
                        % endif
                        >
              <div class="modal-card">

                <header class="modal-card-head">
                  <p class="modal-card-title">Set Preferred Email</p>
                </header>

                <section class="modal-card-body">
                  <p class="block">Really make this the preferred email address?</p>
                  <p class="block has-text-weight-bold">{{ preferEmailAddress }}</p>
                </section>

                <footer class="modal-card-foot">
                  <b-button type="is-primary"
                            @click="preferEmailSave()"
                            :disabled="preferEmailSaving"
                            icon-pack="fas"
                            icon-left="save">
                    {{ preferEmailSaving ? "Working, please wait..." : "Set Preferred" }}
                  </b-button>
                  <b-button @click="preferEmailShowDialog = false">
                    Cancel
                  </b-button>
                </footer>
              </div>
            </${b}-modal>

        % endif
      </div>
    </div>
  </div>
</%def>

<%def name="render_personal_tab_cards()">
  ${self.render_personal_name_card()}
  ${self.render_personal_address_card()}
  ${self.render_personal_phone_card()}
  ${self.render_personal_email_card()}
</%def>

<%def name="render_personal_tab_template()">
  <script type="text/x-template" id="personal-tab-template">
    <div style="display: flex; justify-content: space-between;">

      <div style="flex-grow: 1; margin-right: 1rem;">
        ${self.render_personal_tab_cards()}
      </div>

      <div>
        % if request.has_perm('people.view'):
            <b-button tag="a" :href="person.view_url">
              View Person
            </b-button>
        % endif
      </div>
      % if request.use_oruga:
          <o-loading v-model:active="refreshingTab" :full-page="false"></o-loading>
      % else:
          <b-loading :active.sync="refreshingTab" :is-full-page="false"></b-loading>
      % endif
    </div>
  </script>
</%def>

<%def name="render_personal_tab()">
  <${b}-tab-item label="Personal"
                 value="personal"
                 % if not request.use_oruga:
                     icon-pack="fas"
                 % endif
                 :icon="tabchecks.personal ? 'check' : null">
    <personal-tab ref="tab_personal"
                  :person="person"
                  @profile-changed="profileChanged"
                  :phone-type-options="phoneTypeOptions"
                  :email-type-options="emailTypeOptions"
                  :max-lengths="maxLengths">
    </personal-tab>
  </${b}-tab-item>
</%def>

% if expose_members:
<%def name="render_member_tab_template()">
  <script type="text/x-template" id="member-tab-template">
    <div>
      % if max_one_member:
          <p class="block">
            TODO: UI not yet implemented for "max one member per person"
          </p

      % else:
          ## nb. multiple members allowed per person
          <div v-if="members.length">

            <div style="display: flex; justify-content: space-between;">
              <p>{{ person.display_name }} has <strong>{{ members.length }}</strong> member account{{ members.length == 1 ? '' : 's' }}</p>
            </div>

            <br />
            <${b}-collapse v-for="member in members"
                           :key="member.uuid"
                           class="panel"
                           :open="members.length == 1">

              <template #trigger="props">
                <div class="panel-heading"
                     role="button"
                     style="cursor: pointer;">

                  ## TODO: for some reason buefy will "reuse" the icon
                  ## element in such a way that its display does not
                  ## refresh.  so to work around that, we use different
                  ## structure for the two icons, so buefy is forced to
                  ## re-draw

                  <b-icon v-if="props.open"
                          pack="fas"
                          icon="caret-down" />

                  <span v-if="!props.open">
                    <b-icon pack="fas"
                            icon="caret-right" />
                  </span>

                  &nbsp;
                  <strong>{{ member._key }} - {{ member.display }}</strong>
                </div>
              </template>

              <div class="panel-block">
                <div style="display: flex; justify-content: space-between; width: 100%;">
                  <div style="flex-grow: 1;">

                    <b-field horizontal label="${member_key_label}">
                      {{ member._key }}
                    </b-field>

                    <b-field horizontal label="Account Holder">
                      <a v-if="member.person_uuid != person.uuid"
                         :href="member.view_profile_url">
                        {{ member.person_display_name }}
                      </a>
                      <span v-if="member.person_uuid == person.uuid">
                        {{ member.person_display_name }}
                      </span>
                    </b-field>

                    <b-field horizontal label="Membership Type">
                      <a v-if="member.view_membership_type_url"
                         :href="member.view_membership_type_url">
                        {{ member.membership_type_name }}
                      </a>
                      <span v-if="!member.view_membership_type_url">
                        {{ member.membership_type_name }}
                      </span>
                    </b-field>

                    <b-field horizontal label="Active">
                      {{ member.active ? "Yes" : "No" }}
                    </b-field>

                    <b-field horizontal label="Joined">
                      {{ member.joined }}
                    </b-field>

                    <b-field horizontal label="Withdrew"
                             v-if="member.withdrew">
                      {{ member.withdrew }}
                    </b-field>

                    <b-field horizontal label="Equity Total">
                      {{ member.equity_total_display }}
                    </b-field>

                  </div>
                  <div class="buttons" style="align-items: start;">

                    <b-button v-for="link in member.external_links"
                              :key="link.url"
                              type="is-primary"
                              tag="a" :href="link.url" target="_blank"
                              icon-pack="fas"
                              icon-left="external-link-alt">
                      {{ link.label }}
                    </b-button>

                    % if request.has_perm('members.view'):
                        <b-button tag="a" :href="member.view_url">
                          View Member
                        </b-button>
                    % endif

                  </div>
                </div>
              </div>
            </${b}-collapse>
          </div>

          <div v-if="!members.length">
            <p>{{ person.display_name }} does not have a member account.</p>
          </div>
      % endif

      % if request.use_oruga:
          <o-loading v-model:active="refreshingTab" :full-page="false"></o-loading>
      % else:
          <b-loading :active.sync="refreshingTab" :is-full-page="false"></b-loading>
      % endif
    </div>
  </script>
</%def>

<%def name="render_member_tab()">
  <${b}-tab-item label="Member"
              value="member"
              icon-pack="fas"
              :icon="tabchecks.member ? 'check' : null">
    <member-tab ref="tab_member"
                :person="person"
                @profile-changed="profileChanged"
                :phone-type-options="phoneTypeOptions">
    </member-tab>
  </${b}-tab-item>
</%def>
% endif

<%def name="render_customer_tab_template()">
  <script type="text/x-template" id="customer-tab-template">
    <div>
      <div v-if="customers.length">

        <div style="display: flex; justify-content: space-between;">
          <p>{{ person.display_name }} has <strong>{{ customers.length }}</strong> customer account{{ customers.length == 1 ? '' : 's' }}</p>
        </div>

        <br />
        <${b}-collapse v-for="customer in customers"
                       :key="customer.uuid"
                       class="panel"
                       :open="customers.length == 1">

          <template #trigger="props">
            <div class="panel-heading"
                 role="button"
                 style="cursor: pointer;">

              ## TODO: for some reason buefy will "reuse" the icon
              ## element in such a way that its display does not
              ## refresh.  so to work around that, we use different
              ## structure for the two icons, so buefy is forced to
              ## re-draw

              <b-icon v-if="props.open"
                      pack="fas"
                      icon="caret-down" />

              <span v-if="!props.open">
                <b-icon pack="fas"
                        icon="caret-right" />
              </span>

              &nbsp;
              <strong>{{ customer._key }} - {{ customer.name }}</strong>
            </div>
          </template>

          <div class="panel-block">
            <div style="display: flex; justify-content: space-between; width: 100%;">
              <div style="flex-grow: 1;">

                <b-field horizontal label="${customer_key_label or 'TODO: Customer Key'}">
                  {{ customer._key }}
                </b-field>

                <b-field horizontal label="Account Name">
                  {{ customer.name }}
                </b-field>

                % if expose_customer_shoppers:
                    <b-field horizontal label="Shoppers">
                      <ul>
                        <li v-for="shopper in customer.shoppers"
                            :key="shopper.uuid">
                          <a v-if="shopper.person_uuid != person.uuid"
                             :href="shopper.view_profile_url">
                            {{ shopper.display_name }}
                          </a>
                          <span v-if="shopper.person_uuid == person.uuid">
                            {{ shopper.display_name }}
                          </span>
                        </li>
                      </ul>
                    </b-field>
                % endif

                % if expose_customer_people:
                    <b-field horizontal label="People">
                      <ul>
                        <li v-for="p in customer.people"
                            :key="p.uuid">
                          <a v-if="p.uuid != person.uuid"
                             :href="p.view_profile_url">
                            {{ p.display_name }}
                          </a>
                          <span v-if="p.uuid == person.uuid">
                            {{ p.display_name }}
                          </span>
                        </li>
                      </ul>
                    </b-field>
                % endif

                <b-field horizontal label="Address"
                         v-for="address in customer.addresses"
                         :key="address.uuid">
                  {{ address.display }}
                </b-field>

              </div>
              <div class="buttons" style="align-items: start;">

                <b-button v-for="link in customer.external_links"
                          :key="link.url"
                          type="is-primary"
                          tag="a" :href="link.url" target="_blank"
                          icon-pack="fas"
                          icon-left="external-link-alt">
                  {{ link.label }}
                </b-button>

                % if request.has_perm('customers.view'):
                    <b-button tag="a" :href="customer.view_url">
                      View Customer
                    </b-button>
                % endif

              </div>
            </div>
          </div>
        </${b}-collapse>
      </div>

      <div v-if="!customers.length">
        <p>{{ person.display_name }} does not have a customer account.</p>
      </div>
      % if request.use_oruga:
          <o-loading v-model:active="refreshingTab" :full-page="false"></o-loading>
      % else:
          <b-loading :active.sync="refreshingTab" :is-full-page="false"></b-loading>
      % endif
    </div>
  </script>
</%def>

<%def name="render_customer_tab()">
  <${b}-tab-item label="Customer"
              value="customer"
              icon-pack="fas"
              :icon="tabchecks.customer ? 'check' : null">
    <customer-tab ref="tab_customer"
                  :person="person"
                  @profile-changed="profileChanged">
    </customer-tab>
  </${b}-tab-item>
</%def>

<%def name="render_shopper_tab_template()">
  <script type="text/x-template" id="shopper-tab-template">
    <div>
      <div v-if="shoppers.length">

        <div style="display: flex; justify-content: space-between;">
          <p>{{ person.display_name }} is shopper for <strong>{{ shoppers.length }}</strong> customer account{{ shoppers.length == 1 ? '' : 's' }}</p>
        </div>

        <br />
        <b-collapse v-for="shopper in shoppers"
                    :key="shopper.uuid"
                    class="panel"
                    :open="shoppers.length == 1">

          <div slot="trigger"
               slot-scope="props"
               class="panel-heading"
               role="button">
            <b-icon pack="fas"
                    icon="caret-right">
            </b-icon>
            <strong>{{ shopper.customer_key }} - {{ shopper.customer_name }}</strong>
          </div>

          <div class="panel-block">
            <div style="display: flex; justify-content: space-between; width: 100%;">
              <div style="flex-grow: 1;">

                <b-field horizontal label="${customer_key_label}">
                  {{ shopper.customer_key }}
                </b-field>

                <b-field horizontal label="Account Name">
                  {{ shopper.customer_name }}
                </b-field>

                <b-field horizontal label="Account Holder">
                  <span v-if="!shopper.account_holder_view_profile_url">
                    {{ shopper.account_holder_name }}
                  </span>
                  <a v-if="shopper.account_holder_view_profile_url"
                     :href="shopper.account_holder_view_profile_url">
                    {{ shopper.account_holder_name }}
                  </a>
                </b-field>

              </div>
  ##             <div class="buttons" style="align-items: start;">
  ##               ${self.render_shopper_panel_buttons(shopper)}
  ##             </div>
            </div>
          </div>
        </b-collapse>
      </div>

      <div v-if="!shoppers.length">
        <p>{{ person.display_name }} is not a shopper.</p>
      </div>
      % if request.use_oruga:
          <o-loading v-model:active="refreshingTab" :full-page="false"></o-loading>
      % else:
          <b-loading :active.sync="refreshingTab" :is-full-page="false"></b-loading>
      % endif
    </div>
  </script>
</%def>

<%def name="render_shopper_tab()">
  <${b}-tab-item label="Shopper"
              value="shopper"
              icon-pack="fas"
              :icon="tabchecks.shopper ? 'check' : null">
    <shopper-tab ref="tab_shopper"
                 :person="person"
                 @profile-changed="profileChanged">
    </shopper-tab>
  </${b}-tab-item>
</%def>

<%def name="render_employee_tab_template()">
  <script type="text/x-template" id="employee-tab-template">
    <div>
      <div style="display: flex; justify-content: space-between;">

        <div style="flex-grow: 1;">

          <div v-if="employee.uuid">

            <div :key="refreshEmployeeCard">
              <b-field horizontal label="Employee ID">
                <div class="level">
                  <div class="level-left">
                    <div class="level-item">
                      <span>{{ employee.id }}</span>
                    </div>
                    % if request.has_perm('employees.edit'):
                    <div class="level-item">
                      <b-button type="is-primary"
                                icon-pack="fas"
                                icon-left="edit"
                                @click="editEmployeeIdInit()">
                        Edit ID
                      </b-button>
                      <${b}-modal has-modal-card
                                  % if request.use_oruga:
                                  v-model:active="editEmployeeIdShowDialog"
                                  % else:
                                  :active.sync="editEmployeeIdShowDialog"
                                  % endif
                                  >
                        <div class="modal-card">

                          <header class="modal-card-head">
                            <p class="modal-card-title">Employee ID</p>
                          </header>

                          <section class="modal-card-body">
                            <b-field label="Employee ID">
                              <b-input v-model="editEmployeeIdValue"></b-input>
                            </b-field>
                          </section>

                          <footer class="modal-card-foot">
                            <b-button @click="editEmployeeIdShowDialog = false">
                              Cancel
                            </b-button>
                            <b-button type="is-primary"
                                      icon-pack="fas"
                                      icon-left="save"
                                      :disabled="editEmployeeIdSaving"
                                      @click="editEmployeeIdSave()">
                              {{ editEmployeeIdSaving ? "Working, please wait..." : "Save" }}
                            </b-button>
                          </footer>
                        </div>
                      </${b}-modal>
                    </div>
                    % endif
                  </div>
                </div>
              </b-field>

              <b-field horizontal label="Employee Status">
                <span>{{ employee.status_display }}</span>
              </b-field>

              <b-field horizontal label="Start Date">
                <span>{{ employee.start_date }}</span>
              </b-field>

              <b-field horizontal label="End Date">
                <span>{{ employee.end_date }}</span>
              </b-field>
            </div>

            <br />
            <p><strong>Employee History</strong></p>
            <br />

            <${b}-table :data="employeeHistory">

              <${b}-table-column field="start_date"
                              label="Start Date"
                              v-slot="props">
                {{ props.row.start_date }}
              </${b}-table-column>

              <${b}-table-column field="end_date"
                              label="End Date"
                              v-slot="props">
                {{ props.row.end_date }}
              </${b}-table-column>

              % if request.has_perm('people_profile.edit_employee_history'):
                  <${b}-table-column field="actions"
                                  label="Actions"
                                  v-slot="props">
                    <a href="#" @click.prevent="editEmployeeHistoryInit(props.row)">
                      % if request.use_oruga:
                          <span class="icon-text">
                            <o-icon icon="edit" />
                            <span>Edit</span>
                          </span>
                      % else:
                          <i class="fas fa-edit"></i>
                          Edit
                      % endif
                    </a>
                  </${b}-table-column>
              % endif

            </${b}-table>

          </div>

          <p v-if="!employee.uuid">
            ${person} is not an employee.
          </p>

        </div>

        <div style="display: flex; gap: 0.75rem;">

          % if request.has_perm('people_profile.toggle_employee'):

              <b-button v-if="!employee.current"
                        type="is-primary"
                        @click="startEmployeeInit()">
                ${person} is now an Employee
              </b-button>

              <b-button v-if="employee.current"
                        type="is-primary"
                        @click="stopEmployeeInit()">
                ${person} is no longer an Employee
              </b-button>

              <${b}-modal has-modal-card
                          % if request.use_oruga:
                              v-model:active="startEmployeeShowDialog"
                          % else:
                              :active.sync="startEmployeeShowDialog"
                          % endif
                          >
                <div class="modal-card">

                  <header class="modal-card-head">
                    <p class="modal-card-title">Employee Start</p>
                  </header>

                  <section class="modal-card-body">
                    <b-field label="Employee Number">
                      <b-input v-model="startEmployeeID"></b-input>
                    </b-field>
                    <b-field label="Start Date">
                      <tailbone-datepicker v-model="startEmployeeStartDate"
                                           ref="startEmployeeStartDate" />
                    </b-field>
                  </section>

                  <footer class="modal-card-foot">
                    <b-button @click="startEmployeeShowDialog = false">
                      Cancel
                    </b-button>
                    <b-button type="is-primary"
                              @click="startEmployeeSave()"
                              :disabled="startEmployeeSaveDisabled"
                              icon-pack="fas"
                              icon-left="save">
                      {{ startEmployeeSaving ? "Working, please wait..." : "Save" }}
                    </b-button>
                  </footer>
                </div>
              </${b}-modal>

              <${b}-modal has-modal-card
                          % if request.use_oruga:
                              v-model:active="stopEmployeeShowDialog"
                          % else:
                              :active.sync="stopEmployeeShowDialog"
                          % endif
                          >
                <div class="modal-card">

                  <header class="modal-card-head">
                    <p class="modal-card-title">Employee End</p>
                  </header>

                  <section class="modal-card-body">
                    <b-field label="End Date"
                             :type="stopEmployeeEndDate ? null : 'is-danger'">
                      <tailbone-datepicker v-model="stopEmployeeEndDate"></tailbone-datepicker>
                    </b-field>
                    <b-field label="Revoke Internal App Access">
                      <b-checkbox v-model="stopEmployeeRevokeAccess">
                      </b-checkbox>
                    </b-field>
                  </section>

                  <footer class="modal-card-foot">
                    <b-button @click="stopEmployeeShowDialog = false">
                      Cancel
                    </b-button>
                    <b-button type="is-primary"
                              @click="stopEmployeeSave()"
                              :disabled="stopEmployeeSaveDisabled"
                              icon-pack="fas"
                              icon-left="save">
                      {{ stopEmployeeSaving ? "Working, please wait..." : "Save" }}
                    </b-button>
                  </footer>
                </div>
              </${b}-modal>
          % endif

          % if request.has_perm('people_profile.edit_employee_history'):
              <${b}-modal has-modal-card
                          % if request.use_oruga:
                              v-model:active="editEmployeeHistoryShowDialog"
                          % else:
                              :active.sync="editEmployeeHistoryShowDialog"
                          % endif
                          >
                <div class="modal-card">

                  <header class="modal-card-head">
                    <p class="modal-card-title">Edit Employee History</p>
                  </header>

                  <section class="modal-card-body">
                    <b-field label="Start Date">
                      <tailbone-datepicker v-model="editEmployeeHistoryStartDate"></tailbone-datepicker>
                    </b-field>
                    <b-field label="End Date">
                      <tailbone-datepicker v-model="editEmployeeHistoryEndDate"
                                           :disabled="!editEmployeeHistoryEndDateRequired">
                      </tailbone-datepicker>
                    </b-field>
                  </section>

                  <footer class="modal-card-foot">
                    <b-button @click="editEmployeeHistoryShowDialog = false">
                      Cancel
                    </b-button>
                    <b-button type="is-primary"
                              @click="editEmployeeHistorySave()"
                              :disabled="editEmployeeHistorySaveDisabled"
                              icon-pack="fas"
                              icon-left="save">
                      {{ editEmployeeHistorySaving ? "Working, please wait..." : "Save" }}
                    </b-button>
                  </footer>
                </div>
              </${b}-modal>
          % endif

          <div style="display: flex; flex-direction: column; align-items: right; gap: 0.75rem;">

            <b-button v-for="link in employee.external_links"
                      :key="link.url"
                      type="is-primary"
                      tag="a" :href="link.url" target="_blank"
                      icon-pack="fas"
                      icon-left="external-link-alt">
              {{ link.label }}
            </b-button>

            % if request.has_perm('employees.view'):
                <b-button v-if="employee.view_url"
                          tag="a" :href="employee.view_url">
                  View Employee
                </b-button>
            % endif

          </div>
        </div>

      </div>
      % if request.use_oruga:
          <o-loading v-model:active="refreshingTab" :full-page="false"></o-loading>
      % else:
          <b-loading :active.sync="refreshingTab" :is-full-page="false"></b-loading>
      % endif
    </div>
  </script>
</%def>

<%def name="render_employee_tab()">
  <${b}-tab-item label="Employee"
              value="employee"
              icon-pack="fas"
              :icon="tabchecks.employee ? 'check' : null">
    <employee-tab ref="tab_employee"
                  :person="person"
                  @profile-changed="profileChanged">
    </employee-tab>
  </${b}-tab-item>
</%def>

<%def name="render_notes_tab_template()">
  <script type="text/x-template" id="notes-tab-template">
    <div>

      % if request.has_perm('people_profile.add_note'):
          <b-button type="is-primary"
                    class="control"
                    @click="addNoteInit()"
                    icon-pack="fas"
                    icon-left="plus">
            Add Note
          </b-button>
      % endif

      <${b}-table :data="notes">

        <${b}-table-column field="note_type"
                        label="Type"
                        v-slot="props">
          {{ props.row.note_type_display }}
        </${b}-table-column>

        <${b}-table-column field="subject"
                        label="Subject"
                        v-slot="props">
          {{ props.row.subject }}
        </${b}-table-column>

        <${b}-table-column field="text"
                        label="Text"
                        v-slot="props">
          {{ props.row.text }}
        </${b}-table-column>

        <${b}-table-column field="created"
                        label="Created"
                        v-slot="props">
          <span v-html="props.row.created_display"></span>
        </${b}-table-column>

        <${b}-table-column field="created_by"
                        label="Created By"
                        v-slot="props">
          {{ props.row.created_by_display }}
        </${b}-table-column>

        % if request.has_any_perm('people_profile.edit_note', 'people_profile.delete_note'):
            <${b}-table-column label="Actions"
                            v-slot="props">
              % if request.has_perm('people_profile.edit_note'):
                  <a href="#" @click.prevent="editNoteInit(props.row)">
                    % if request.use_oruga:
                        <span class="icon-text">
                          <o-icon icon="edit" />
                          <span>Edit</span>
                        </span>
                    % else:
                        <i class="fas fa-edit"></i>
                        Edit
                    % endif
                  </a>
              % endif
              % if request.has_perm('people_profile.delete_note'):
                  <a href="#" @click.prevent="deleteNoteInit(props.row)"
                     class="has-text-danger">
                    % if request.use_oruga:
                        <span class="icon-text">
                          <o-icon icon="trash" />
                          <span>Delete</span>
                        </span>
                    % else:
                        <i class="fas fa-trash"></i>
                        Delete
                    % endif

                  </a>
              % endif
            </${b}-table-column>
        % endif

      </${b}-table>

      % if request.has_any_perm('people_profile.add_note', 'people_profile.edit_note', 'people_profile.delete_note'):
          <${b}-modal has-modal-card
                      % if request.use_oruga:
                          v-model:active="editNoteShowDialog"
                      % else:
                          :active.sync="editNoteShowDialog"
                      % endif
                      >

            <div class="modal-card">

              <header class="modal-card-head">
                <p class="modal-card-title">
                  {{ editNoteUUID ? (editNoteDelete ? "Delete" : "Edit") : "New" }} Note
                </p>
              </header>

              <section class="modal-card-body">

                <b-field label="Type"
                         :type="!editNoteDelete && !editNoteType ? 'is-danger' : null">
                  <b-select v-model="editNoteType"
                            :disabled="editNoteUUID">
                    <option v-for="option in noteTypeOptions"
                            :key="option.value"
                            :value="option.value">
                      {{ option.label }}
                    </option>
                  </b-select>
                </b-field>

                <b-field label="Subject">
                  <b-input v-model.trim="editNoteSubject"
                           :disabled="editNoteDelete"
                           expanded>
                  </b-input>
                </b-field>

                <b-field label="Text">
                  <b-input v-model.trim="editNoteText"
                           type="textarea"
                           :disabled="editNoteDelete"
                           expanded>
                  </b-input>
                </b-field>

                <b-notification v-if="editNoteDelete"
                                type="is-danger"
                                :closable="false">
                  Are you sure you wish to delete this note?
                </b-notification>

              </section>

              <footer class="modal-card-foot">
                <b-button :type="editNoteDelete ? 'is-danger' : 'is-primary'"
                          @click="editNoteSave()"
                          :disabled="editNoteSaving || (!editNoteDelete && !editNoteType)"
                          icon-pack="fas"
                          icon-left="save">
                  {{ editNoteSaving ? "Working..." : (editNoteDelete ? "Delete" : "Save") }}
                </b-button>
                <b-button @click="editNoteShowDialog = false">
                  Cancel
                </b-button>
              </footer>

            </div>
          </${b}-modal>
      % endif

      % if request.use_oruga:
          <o-loading v-model:active="refreshingTab" :full-page="false"></o-loading>
      % else:
          <b-loading :active.sync="refreshingTab" :is-full-page="false"></b-loading>
      % endif
    </div>
  </script>
</%def>

<%def name="render_notes_tab()">
  <${b}-tab-item label="Notes"
              value="notes"
              icon-pack="fas"
              :icon="tabchecks.notes ? 'check' : null">
    <notes-tab ref="tab_notes"
               :person="person"
               @profile-changed="profileChanged">
    </notes-tab>
  </${b}-tab-item>
</%def>

% if expose_transactions:

    <%def name="render_transactions_tab_template()">
      <script type="text/x-template" id="transactions-tab-template">
        <div>
          <transactions-grid
            ref="transactionsGrid"
             />
        </div>
      </script>
    </%def>

    <%def name="render_transactions_tab()">
      <${b}-tab-item label="Transactions"
                     value="transactions"
                     % if not request.use_oruga:
                         icon-pack="fas"
                     % endif
                     icon="bars">
        <transactions-tab ref="tab_transactions"
                          :person="person"
                          @profile-changed="profileChanged" />
      </${b}-tab-item>
    </%def>

% endif


<%def name="render_user_tab_template()">
  <script type="text/x-template" id="user-tab-template">
    <div>
      <div v-if="users.length">

        <p>{{ person.display_name }} has <strong>{{ users.length }}</strong> user account{{ users.length == 1 ? '' : 's' }}</p>
        <br />
        <div id="users-accordion">

          <${b}-collapse v-for="user in users"
                      :key="user.uuid"
                      class="panel">

            <template #trigger="props">
              <div class="panel-heading"
                   role="button"
                   style="cursor: pointer;">

                ## TODO: for some reason buefy will "reuse" the icon
                ## element in such a way that its display does not
                ## refresh.  so to work around that, we use different
                ## structure for the two icons, so buefy is forced to
                ## re-draw

                <b-icon v-if="props.open"
                        pack="fas"
                        icon="caret-down" />

                <span v-if="!props.open">
                  <b-icon pack="fas"
                          icon="caret-right" />
                </span>

                &nbsp;
                <strong>{{ user.username }}</strong>
              </div>
            </template>

            <div class="panel-block">
              <div style="display: flex; justify-content: space-between; width: 100%;">

                <div style="flex-grow: 1;">
                  <b-field horizontal label="Username">
                    {{ user.username }}
                  </b-field>
                  <b-field horizontal label="Active">
                    {{ user.active ? "Yes" : "No" }}
                  </b-field>
                </div>

                <div>
                  % if request.has_perm('users.view'):
                      <b-button tag="a" :href="user.view_url">
                        View User
                      </b-button>
                  % endif
                </div>

              </div>
            </div>
          </${b}-collapse>
        </div>
      </div>

      <div v-if="!users.length"
           style="display: flex; justify-content: space-between;">

        <p>{{ person.display_name }} does not have a user account.</p>

        % if request.has_perm('users.create'):
            <b-button type="primary"
                      icon-pack="fas"
                      icon-left="plus"
                      @click="createUserInit()">
              Create User
            </b-button>

            <${b}-modal has-modal-card
                        % if request.use_oruga:
                            v-model:active="createUserShowDialog"
                        % else:
                            :active.sync="createUserShowDialog"
                        % endif
                        >
              <div class="modal-card">

                <header class="modal-card-head">
                  <p class="modal-card-title">Create User</p>
                </header>

                <section class="modal-card-body">
                  <b-field label="Person">
                    <span>{{ person.display_name }}</span>
                  </b-field>
                  <b-field label="Username">
                    <b-input v-model="createUserUsername"
                             ref="username" />
                  </b-field>
                  <b-field label="Active">
                    <b-checkbox v-model="createUserActive" />
                  </b-field>
                </section>

                <footer class="modal-card-foot">
                  <b-button @click="createUserShowDialog = false">
                    Cancel
                  </b-button>
                  <b-button type="is-primary"
                            @click="createUserSave()"
                            :disabled="createUserSaveDisabled"
                            icon-pack="fas"
                            icon-left="save">
                    {{ createUserSaving ? "Working, please wait..." : "Save" }}
                  </b-button>
                </footer>
              </div>
            </${b}-modal>
        % endif
      </div>

      % if request.use_oruga:
          <o-loading v-model:active="refreshingTab" :full-page="false"></o-loading>
      % else:
          <b-loading :active.sync="refreshingTab" :is-full-page="false"></b-loading>
      % endif
    </div>
  </script>
</%def>

<%def name="render_user_tab()">
  <${b}-tab-item label="User"
              value="user"
              icon-pack="fas"
              :icon="tabchecks.user ? 'check' : null">
    <user-tab ref="tab_user"
              :person="person"
              @profile-changed="profileChanged">
    </user-tab>
  </${b}-tab-item>
</%def>

<%def name="render_profile_tabs()">
  ${self.render_personal_tab()}

  % if expose_members:
      ${self.render_member_tab()}
  % endif

  ${self.render_customer_tab()}
  % if expose_customer_shoppers:
      ${self.render_shopper_tab()}
  % endif
  ${self.render_employee_tab()}
  ${self.render_notes_tab()}
  % if expose_transactions:
      ${self.render_transactions_tab()}
  % endif
  ${self.render_user_tab()}
</%def>

<%def name="render_profile_info_extra_buttons()"></%def>

<%def name="render_profile_info_template()">
  <script type="text/x-template" id="profile-info-template">
    <div>

      ${self.render_profile_info_extra_buttons()}

      <${b}-tabs v-model="activeTab"
                 % if request.has_perm('people_profile.view_versions'):
                     v-show="!viewingHistory"
                 % endif
                 % if request.use_oruga:
                     type="boxed"
                     @change="activeTabChanged"
                 % else:
                     type="is-boxed"
                     @input="activeTabChanged"
                 % endif
                 >
        ${self.render_profile_tabs()}
      </${b}-tabs>

      % if request.has_perm('people_profile.view_versions'):

          ${revisions_grid.render_table_element(data_prop='revisions',
                                                show_footer=True,
                                                vshow='viewingHistory',
                                                loading='gettingRevisions')|n}

          <${b}-modal
            % if request.use_oruga:
                v-model:active="showingRevisionDialog"
            % else:
                :active.sync="showingRevisionDialog"
            % endif
            >

            <div class="card">
              <div class="card-content">

                <div style="display: flex; justify-content: space-between;">

                  <div>
                    <b-field horizontal label="Changed">
                      <div v-html="revision.changed"></div>
                    </b-field>
                    <b-field horizontal label="Changed by">
                      <div v-html="revision.changed_by"></div>
                    </b-field>
                    <b-field horizontal label="IP Address">
                      <div v-html="revision.remote_addr"></div>
                    </b-field>
                    <b-field horizontal label="Comment">
                      <div v-html="revision.comment"></div>
                    </b-field>
                    <b-field horizontal label="TXN ID">
                      <div v-html="revision.txnid"></div>
                    </b-field>
                  </div>

                  <div>
                    <div>
                      <b-button @click="viewPrevRevision()"
                                :disabled="!revision.prev_txnid">
                        &laquo; Prev
                      </b-button>
                      <b-button @click="viewNextRevision()"
                                :disabled="!revision.next_txnid">
                        &raquo; Next
                      </b-button>
                    </div>
                    <br />
                    <b-button @click="toggleVersionFields()">
                      {{ revisionShowAllFields ? "Show Diffs Only" : "Show All Fields" }}
                    </b-button>
                  </div>

                </div>

                <br />

                <div v-for="version in revision.versions"
                     :key="version.key">

                  <p class="block has-text-weight-bold">
                    {{ version.model_title }}
                  </p>

                  <table class="diff monospace is-size-7"
                         :class="version.diff_class">
                    <thead>
                      <tr>
                        <th>field name</th>
                        <th>old value</th>
                        <th>new value</th>
                      </tr>
                    </thead>
                    <tbody>
                      <tr v-for="field in version.fields"
                          :key="field"
                          :class="{diff: version.values[field].after != version.values[field].before}"
                          v-show="revisionShowAllFields || version.values[field].after != version.values[field].before">
                        <td class="field">{{ field }}</td>
                        <td class="old-value" v-html="version.values[field].before"></td>
                        <td class="new-value" v-html="version.values[field].after"></td>
                      </tr>
                    </tbody>
                  </table>

                  <br />
                </div>

              </div>
            </div>
          </${b}-modal>
      % endif

    </div>
  </script>
  <script>

    let ProfileInfoData = {
        activeTab: location.hash ? location.hash.substring(1) : 'personal',
        tabchecks: ${json.dumps(tabchecks or {})|n},
        today: '${rattail_app.today()}',
        profileLastChanged: Date.now(),
        person: ${json.dumps(person_data or {})|n},
        phoneTypeOptions: ${json.dumps(phone_type_options or [])|n},
        emailTypeOptions: ${json.dumps(email_type_options or [])|n},
        maxLengths: ${json.dumps(max_lengths or {})|n},

        % if request.has_perm('people_profile.view_versions'):
            loadingRevisions: false,
            showingRevisionDialog: false,
            revision: {},
            revisionShowAllFields: false,
        % endif
    }

    let ProfileInfo = {
        template: '#profile-info-template',
        props: {
            % if request.has_perm('people_profile.view_versions'):
                viewingHistory: Boolean,
                gettingRevisions: Boolean,
                revisions: Array,
                revisionVersionMap: null,
            % endif
        },
        computed: {},
        mounted() {

            // auto-refresh whichever tab is shown first
            ## TODO: how to not assume 'personal' is the default tab?
            let tab = this.$refs['tab_' + (this.activeTab || 'personal')]
            if (tab && tab.refreshTab) {
                tab.refreshTab()
            }
        },
        methods: {

            profileChanged(data) {
                this.$emit('change-content-title', data.person.dynamic_content_title)
                this.person = data.person
                this.tabchecks = data.tabchecks
                this.profileLastChanged = Date.now()
            },

            activeTabChanged(value) {
                location.hash = value
                this.refreshTabIfNeeded(value)
                this.activeTabChangedExtra(value)
            },

            refreshTabIfNeeded(key) {
                // TODO: this is *always* refreshing, should be more selective (?)
                let tab = this.$refs['tab_' + key]
                if (tab && tab.refreshIfNeeded) {
                    tab.refreshIfNeeded(this.profileLastChanged)
                }
            },

            activeTabChangedExtra(value) {},

            % if request.has_perm('people_profile.view_versions'):

                viewRevision(row) {
                    this.revision = this.revisionVersionMap[row.txnid]
                    this.showingRevisionDialog = true
                },

                viewPrevRevision() {
                    let txnid = this.revision.prev_txnid
                    this.revision = this.revisionVersionMap[txnid]
                },

                viewNextRevision() {
                    let txnid = this.revision.next_txnid
                    this.revision = this.revisionVersionMap[txnid]
                },

                toggleVersionFields() {
                    this.revisionShowAllFields = !this.revisionShowAllFields
                },

            % endif
        },
    }

  </script>
</%def>

<%def name="declare_personal_tab_vars()">
  <script type="text/javascript">

    let PersonalTabData = {
        % if hasattr(master, 'profile_tab_personal'):
        refreshTabURL: '${url('people.profile_tab_personal', uuid=person.uuid)}',
        % endif

        // nb. hack to force refresh for vue3
        refreshPersonalCard: 1,
        refreshAddressCard: 1,

        % if request.has_perm('people_profile.edit_person'):
            editNameShowDialog: false,
            editNameFirst: null,
            % if use_preferred_first_name:
                editNameFirstPreferred: null,
            % endif
            editNameMiddle: null,
            editNameLast: null,
            editNameSaving: false,

            editAddressShowDialog: false,
            editAddressStreet1: null,
            editAddressStreet2: null,
            editAddressCity: null,
            editAddressState: null,
            editAddressZipcode: null,
            editAddressInvalid: false,

            editPhoneShowDialog: false,
            editPhoneUUID: null,
            editPhoneType: null,
            editPhoneNumber: null,
            editPhonePreferred: false,
            editPhoneSaving: false,

            deletePhoneShowDialog: false,
            deletePhoneUUID: null,
            deletePhoneNumber: null,
            deletePhoneSaving: false,

            preferPhoneShowDialog: false,
            preferPhoneUUID: null,
            preferPhoneNumber: null,
            preferPhoneSaving: false,

            editEmailShowDialog: false,
            editEmailUUID: null,
            editEmailType: null,
            editEmailAddress: null,
            editEmailPreferred: null,
            editEmailInvalid: false,
            editEmailSaving: false,

            deleteEmailShowDialog: false,
            deleteEmailUUID: null,
            deleteEmailAddress: null,
            deleteEmailSaving: false,

            preferEmailShowDialog: false,
            preferEmailUUID: null,
            preferEmailAddress: null,
            preferEmailSaving: false,

        % endif
    }

    let PersonalTab = {
        template: '#personal-tab-template',
        mixins: [TabMixin, SimpleRequestMixin],
        props: {
            person: Object,
            phoneTypeOptions: Array,
            emailTypeOptions: Array,
            maxLengths: Object,
        },
        computed: {

            % if request.has_perm('people_profile.edit_person'):

                editNameSaveDisabled: function() {
                    if (this.editNameSaving) {
                        return true
                    }
                    if (!this.editNameFirst || !this.editNameLast) {
                        return true
                    }
                    return false
                },

                editAddressSaveDisabled: function() {
                    // TODO: should require anything here?
                    return false
                },

                editPhoneSaveDisabled: function() {
                    if (this.editPhoneSaving) {
                        return true
                    }
                    if (!this.editPhoneType) {
                        return true
                    }
                    if (!this.editPhoneNumber) {
                        return true
                    }
                    return false
                },

                editEmailSaveDisabled: function() {
                    if (this.editEmailSaving) {
                        return true
                    }
                    if (!this.editEmailType) {
                        return true
                    }
                    if (!this.editEmailAddress) {
                        return true
                    }
                    return false
                },

            % endif
        },
        methods: {

            // refreshTabSuccess(response) {},

            % if request.has_perm('people_profile.edit_person'):

                editNameAllowed() {
                    return true
                },

                editNameInit() {
                    this.editNameFirst = this.person.first_name
                    % if use_preferred_first_name:
                        this.editNameFirstPreferred = this.person.preferred_first_name
                    % endif
                    this.editNameMiddle = this.person.middle_name
                    this.editNameLast = this.person.last_name
                    this.editNameShowDialog = true
                },

                editNameSave() {
                    this.editNameSaving = true
                    let url = '${url('people.profile_edit_name', uuid=person.uuid)}'
                    let params = {
                        first_name: this.editNameFirst,
                        % if use_preferred_first_name:
                            preferred_first_name: this.editNameFirstPreferred,
                        % endif
                        middle_name: this.editNameMiddle,
                        last_name: this.editNameLast,
                    }

                    this.simplePOST(url, params, response => {
                        this.$emit('profile-changed', response.data)
                        this.editNameShowDialog = false
                        this.refreshTab()
                        this.editNameSaving = false
                        // nb. hack to force refresh for vue3
                        this.refreshPersonalCard += 1
                    }, response => {
                        this.editNameSaving = false
                    })
                },

                editAddressInit() {
                    let address = this.person.address
                    this.editAddressStreet1 = address ? address.street : null
                    this.editAddressStreet2 = address ? address.street2 : null
                    this.editAddressCity = address ? address.city : null
                    this.editAddressState = address ? address.state : null
                    this.editAddressZipcode = address ? address.zipcode : null
                    this.editAddressInvalid = address ? address.invalid : false
                    this.editAddressShowDialog = true
                },

                editAddressSave() {
                    let url = '${url('people.profile_edit_address', uuid=person.uuid)}'
                    let params = {
                        street: this.editAddressStreet1,
                        street2: this.editAddressStreet2,
                        city: this.editAddressCity,
                        state: this.editAddressState,
                        zipcode: this.editAddressZipcode,
                        invalid: this.editAddressInvalid,
                    }

                    this.simplePOST(url, params, response => {
                        this.$emit('profile-changed', response.data)
                        this.editAddressShowDialog = false
                        this.refreshTab()
                        // nb. hack to force refresh for vue3
                        this.refreshAddressCard += 1
                    })
                },

                addPhoneInit() {
                    this.editPhoneInit({
                        uuid: null,
                        type: 'Home',
                        number: null,
                        preferred: false,
                    })
                },

                editPhoneInit(phone) {
                    this.editPhoneUUID = phone.uuid
                    this.editPhoneType = phone.type
                    this.editPhoneNumber = phone.number
                    this.editPhonePreferred = phone.preferred
                    this.editPhoneShowDialog = true
                    this.$nextTick(function() {
                        this.$refs.editPhoneInput.focus()
                    })
                },

                editPhoneSave() {
                    this.editPhoneSaving = true

                    let url
                    let params = {
                        phone_number: this.editPhoneNumber,
                        phone_type: this.editPhoneType,
                        phone_preferred: this.editPhonePreferred,
                    }

                    // nb. create or update
                    if (this.editPhoneUUID) {
                        url = '${url('people.profile_update_phone', uuid=person.uuid)}'
                        params.phone_uuid = this.editPhoneUUID
                    } else {
                        url = '${url('people.profile_add_phone', uuid=person.uuid)}'
                    }

                    this.simplePOST(url, params, response => {
                        this.$emit('profile-changed', response.data)
                        this.editPhoneShowDialog = false
                        this.editPhoneSaving = false
                        this.refreshTab()
                    }, response => {
                        this.editPhoneSaving = false
                    })
                },

                deletePhoneInit(phone) {
                    this.deletePhoneUUID = phone.uuid
                    this.deletePhoneNumber = phone.number
                    this.deletePhoneShowDialog = true
                },

                deletePhoneSave() {
                    this.deletePhoneSaving = true
                    let url = '${url('people.profile_delete_phone', uuid=person.uuid)}'
                    let params = {
                        phone_uuid: this.deletePhoneUUID,
                    }
                    this.simplePOST(url, params, response => {
                        this.$emit('profile-changed', response.data)
                        this.refreshTab()
                        this.deletePhoneShowDialog = false
                        this.deletePhoneSaving = false
                    }, response => {
                        this.deletePhoneSaving = false
                    })
                },

                preferPhoneInit(phone) {
                    this.preferPhoneUUID = phone.uuid
                    this.preferPhoneNumber = phone.number
                    this.preferPhoneShowDialog = true
                },

                preferPhoneSave() {
                    this.preferPhoneSaving = true
                    let url = '${url('people.profile_set_preferred_phone', uuid=person.uuid)}'
                    let params = {
                        phone_uuid: this.preferPhoneUUID,
                    }

                    this.simplePOST(url, params, response => {
                        this.$emit('profile-changed', response.data)
                        this.refreshTab()
                        this.preferPhoneShowDialog = false
                        this.preferPhoneSaving = false
                    }, response => {
                        this.preferPhoneSaving = false
                    })
                },

                addEmailInit() {
                    this.editEmailInit({
                        uuid: null,
                        type: 'Home',
                        address: null,
                        invalid: false,
                        preferred: false,
                    })
                },

                editEmailInit(email) {
                    this.editEmailUUID = email.uuid
                    this.editEmailType = email.type
                    this.editEmailAddress = email.address
                    this.editEmailInvalid = email.invalid
                    this.editEmailPreferred = email.preferred
                    this.editEmailShowDialog = true
                    this.$nextTick(function() {
                        this.$refs.editEmailInput.focus()
                    })
                },

                editEmailSave() {
                    this.editEmailSaving = true

                    let url = null
                    let params = {
                        email_address: this.editEmailAddress,
                        email_type: this.editEmailType,
                    }

                    if (this.editEmailUUID) {
                        url = '${url('people.profile_update_email', uuid=person.uuid)}'
                        params.email_uuid = this.editEmailUUID
                        params.email_invalid = this.editEmailInvalid
                    } else {
                        url = '${url('people.profile_add_email', uuid=person.uuid)}'
                        params.email_preferred = this.editEmailPreferred
                    }

                    this.simplePOST(url, params, response => {
                        this.$emit('profile-changed', response.data)
                        this.editEmailShowDialog = false
                        this.editEmailSaving = false
                        this.refreshTab()
                    }, response => {
                        this.editEmailSaving = false
                    })
                },

                deleteEmailInit(email) {
                    this.deleteEmailUUID = email.uuid
                    this.deleteEmailAddress = email.address
                    this.deleteEmailShowDialog = true
                },

                deleteEmailSave() {
                    this.deleteEmailSaving = true
                    let url = '${url('people.profile_delete_email', uuid=person.uuid)}'
                    let params = {
                        email_uuid: this.deleteEmailUUID,
                    }
                    this.simplePOST(url, params, response => {
                        this.$emit('profile-changed', response.data)
                        this.refreshTab()
                        this.deleteEmailShowDialog = false
                        this.deleteEmailSaving = false
                    }, response => {
                        this.deleteEmailSaving = false
                    })
                },

                preferEmailInit(email) {
                    this.preferEmailUUID = email.uuid
                    this.preferEmailAddress = email.address
                    this.preferEmailShowDialog = true
                },

                preferEmailSave() {
                    this.preferEmailSaving = true
                    let url = '${url('people.profile_set_preferred_email', uuid=person.uuid)}'
                    let params = {
                        email_uuid: this.preferEmailUUID,
                    }

                    this.simplePOST(url, params, response => {
                        this.$emit('profile-changed', response.data)
                        this.refreshTab()
                        this.preferEmailShowDialog = false
                        this.preferEmailSaving = false
                    }, response => {
                        this.preferEmailSaving = false
                    })
                },

            % endif
        },
    }

  </script>
</%def>

<%def name="make_personal_tab_component()">
  ${self.declare_personal_tab_vars()}
  <script type="text/javascript">

    PersonalTab.data = function() { return PersonalTabData }
    Vue.component('personal-tab', PersonalTab)
    <% request.register_component('personal-tab', 'PersonalTab') %>

  </script>
</%def>

% if expose_members:
<%def name="declare_member_tab_vars()">
  <script type="text/javascript">

    let MemberTabData = {
        refreshTabURL: '${url('people.profile_tab_member', uuid=person.uuid)}',
        % if max_one_member:
            member: {},
        % else:
            members: [],
        % endif
    }

    let MemberTab = {
        template: '#member-tab-template',
        mixins: [TabMixin, SimpleRequestMixin],
        props: {
            person: Object,
            phoneTypeOptions: Array,
        },
        computed: {},
        methods: {

            refreshTabSuccess(response) {
                % if max_one_member:
                    this.member = response.data.member
                % else:
                    this.members = response.data.members
                % endif
            },
        },
    }

  </script>
</%def>

<%def name="make_member_tab_component()">
  ${self.declare_member_tab_vars()}
  <script type="text/javascript">

    MemberTab.data = function() { return MemberTabData }
    Vue.component('member-tab', MemberTab)
    <% request.register_component('member-tab', 'MemberTab') %>

  </script>
</%def>
% endif

<%def name="declare_customer_tab_vars()">
  <script type="text/javascript">

    let CustomerTabData = {
        % if hasattr(master, 'profile_tab_customer'):
        refreshTabURL: '${url('people.profile_tab_customer', uuid=person.uuid)}',
        % endif
        customers: [],
    }

    let CustomerTab = {
        template: '#customer-tab-template',
        mixins: [TabMixin, SimpleRequestMixin],
        props: {
            person: Object,
        },
        computed: {},
        methods: {

            refreshTabSuccess(response) {
                this.customers = response.data.customers
            },
        },
    }

  </script>
</%def>

<%def name="make_customer_tab_component()">
  ${self.declare_customer_tab_vars()}
  <script type="text/javascript">

    CustomerTab.data = function() { return CustomerTabData }
    Vue.component('customer-tab', CustomerTab)
    <% request.register_component('customer-tab', 'CustomerTab') %>

  </script>
</%def>

<%def name="declare_shopper_tab_vars()">
  <script type="text/javascript">

    let ShopperTabData = {
        refreshTabURL: '${url('people.profile_tab_shopper', uuid=person.uuid)}',
        shoppers: [],
    }

    let ShopperTab = {
        template: '#shopper-tab-template',
        mixins: [TabMixin, SimpleRequestMixin],
        props: {
            person: Object,
        },
        computed: {},
        methods: {

            refreshTabSuccess(response) {
                this.shoppers = response.data.shoppers
            },
        },
    }

  </script>
</%def>

<%def name="make_shopper_tab_component()">
  ${self.declare_shopper_tab_vars()}
  <script type="text/javascript">

    ShopperTab.data = function() { return ShopperTabData }
    Vue.component('shopper-tab', ShopperTab)
    <% request.register_component('shopper-tab', 'ShopperTab') %>

  </script>
</%def>

<%def name="declare_employee_tab_vars()">
  <script type="text/javascript">

    let EmployeeTabData = {
        % if hasattr(master, 'profile_tab_employee'):
        refreshTabURL: '${url('people.profile_tab_employee', uuid=person.uuid)}',
        % endif
        employee: {},
        employeeHistory: [],

        // nb. hack to force refresh for vue3
        refreshEmployeeCard: 1,

        % if request.has_perm('employees.edit'):
            editEmployeeIdShowDialog: false,
            editEmployeeIdValue: null,
            editEmployeeIdSaving: false,
        % endif

        % if request.has_perm('people_profile.toggle_employee'):
            startEmployeeShowDialog: false,
            startEmployeeID: null,
            startEmployeeStartDate: null,
            startEmployeeSaving: false,

            stopEmployeeShowDialog: false,
            stopEmployeeEndDate: null,
            stopEmployeeRevokeAccess: false,
            stopEmployeeSaving: false,
        % endif

        % if request.has_perm('people_profile.edit_employee_history'):
            editEmployeeHistoryShowDialog: false,
            editEmployeeHistoryUUID: null,
            editEmployeeHistoryStartDate: null,
            editEmployeeHistoryEndDate: null,
            editEmployeeHistoryEndDateRequired: false,
            editEmployeeHistorySaving: false,
        % endif
    }

    let EmployeeTab = {
        template: '#employee-tab-template',
        mixins: [TabMixin, SimpleRequestMixin],
        props: {
            person: Object,
        },
        computed: {

            % if request.has_perm('people_profile.toggle_employee'):

                startEmployeeSaveDisabled() {
                    if (this.startEmployeeSaving) {
                        return true
                    }
                    if (!this.startEmployeeStartDate) {
                        return true
                    }
                    return false
                },

                stopEmployeeSaveDisabled() {
                    if (this.stopEmployeeSaving) {
                        return true
                    }
                    if (!this.stopEmployeeEndDate) {
                        return true
                    }
                    return false
                },

            % endif

            % if request.has_perm('people_profile.edit_employee_history'):

                editEmployeeHistorySaveDisabled() {
                    if (this.editEmployeeHistorySaving) {
                        return true
                    }
                    if (!this.editEmployeeHistoryStartDate) {
                        return true
                    }
                    if (this.editEmployeeHistoryEndDateRequired && !this.editEmployeeHistoryEndDate) {
                        return true
                    }
                    return false
                },

            % endif

        },
        methods: {

            refreshTabSuccess(response) {
                this.employee = response.data.employee
                // nb. hack to force refresh for vue3
                this.refreshEmployeeCard += 1
                this.employeeHistory = response.data.employee_history
            },

            % if request.has_perm('employees.edit'):

                editEmployeeIdInit() {
                    this.editEmployeeIdValue = this.employee.id
                    this.editEmployeeIdShowDialog = true
                },

                editEmployeeIdSave() {
                    this.editEmployeeIdSaving = true
                    let url = '${url('people.profile_update_employee_id', uuid=instance.uuid)}'
                    let params = {
                        'employee_id': this.editEmployeeIdValue || null,
                    }
                    this.simplePOST(url, params, response => {
                        this.$emit('profile-changed', response.data)
                        this.editEmployeeIdShowDialog = false
                        this.editEmployeeIdSaving = false
                        this.refreshTab()
                    }, response => {
                        this.editEmployeeIdSaving = false
                    })
                },

            % endif

            % if request.has_perm('people_profile.toggle_employee'):

                startEmployeeInit() {
                    this.startEmployeeID = this.employee.id || null
                    this.startEmployeeStartDate = null
                    this.startEmployeeShowDialog = true
                },

                startEmployeeSave() {
                    this.startEmployeeSaving = true
                    const url = '${url('people.profile_start_employee', uuid=person.uuid)}'
                    const params = {
                        id: this.startEmployeeID,
                        % if request.use_oruga:
                            start_date: this.$refs.startEmployeeStartDate.formatDate(this.startEmployeeStartDate),
                        % else:
                            start_date: this.startEmployeeStartDate,
                        % endif
                    }

                    this.simplePOST(url, params, response => {
                        this.$emit('profile-changed', response.data)
                        this.startEmployeeShowDialog = false
                        this.refreshTab()
                        this.startEmployeeSaving = false
                    }, response => {
                        this.startEmployeeSaving = false
                    })
                },

                stopEmployeeInit() {
                    this.stopEmployeeEndDate = null
                    this.stopEmployeeRevokeAccess = false
                    this.stopEmployeeShowDialog = true
                },

                stopEmployeeSave() {
                    this.stopEmployeeSaving = true
                    const url = '${url('people.profile_end_employee', uuid=person.uuid)}'
                    const params = {
                        % if request.use_oruga:
                            end_date: this.$refs.startEmployeeStartDate.formatDate(this.stopEmployeeEndDate),
                        % else:
                            end_date: this.stopEmployeeEndDate,
                        % endif
                        revoke_access: this.stopEmployeeRevokeAccess,
                    }

                    this.simplePOST(url, params, response => {
                        this.$emit('profile-changed', response.data)
                        this.stopEmployeeShowDialog = false
                        this.stopEmployeeSaving = false
                        this.refreshTab()
                    }, response => {
                        this.stopEmployeeSaving = false
                    })
                },

            % endif

            % if request.has_perm('people_profile.edit_employee_history'):

                editEmployeeHistoryInit(row) {
                    this.editEmployeeHistoryUUID = row.uuid
                    this.editEmployeeHistoryStartDate = row.start_date
                    this.editEmployeeHistoryEndDate = row.end_date
                    this.editEmployeeHistoryEndDateRequired = !!row.end_date
                    this.editEmployeeHistoryShowDialog = true
                },

                editEmployeeHistorySave() {
                    this.editEmployeeHistorySaving = true
                    let url = '${url('people.profile_edit_employee_history', uuid=person.uuid)}'
                    let params = {
                        uuid: this.editEmployeeHistoryUUID,
                        % if request.use_oruga:
                            start_date: this.$refs.startEmployeeStartDate.formatDate(this.editEmployeeHistoryStartDate),
                            end_date: this.$refs.startEmployeeStartDate.formatDate(this.editEmployeeHistoryEndDate),
                        % else:
                            start_date: this.editEmployeeHistoryStartDate,
                            end_date: this.editEmployeeHistoryEndDate,
                        % endif
                    }

                    this.simplePOST(url, params, response => {
                        this.$emit('profile-changed', response.data)
                        this.editEmployeeHistoryShowDialog = false
                        this.refreshTab()
                        this.editEmployeeHistorySaving = false
                    }, response => {
                        this.editEmployeeHistorySaving = false
                    })
                },

            % endif
        },
    }

  </script>
</%def>

<%def name="make_employee_tab_component()">
  ${self.declare_employee_tab_vars()}
  <script type="text/javascript">

    EmployeeTab.data = function() { return EmployeeTabData }
    Vue.component('employee-tab', EmployeeTab)
    <% request.register_component('employee-tab', 'EmployeeTab') %>

  </script>
</%def>

<%def name="declare_notes_tab_vars()">
  <script type="text/javascript">

    let NotesTabData = {
        % if hasattr(master, 'profile_tab_notes'):
        refreshTabURL: '${url('people.profile_tab_notes', uuid=person.uuid)}',
        % endif
        notes: [],
        noteTypeOptions: [],

        % if request.has_any_perm('people_profile.add_note', 'people_profile.edit_note', 'people_profile.delete_note'):
            editNoteShowDialog: false,
            editNoteUUID: null,
            editNoteDelete: false,
            editNoteType: null,
            editNoteSubject: null,
            editNoteText: null,
            editNoteSaving: false,
        % endif
    }

    let NotesTab = {
        template: '#notes-tab-template',
        mixins: [TabMixin, SimpleRequestMixin],
        props: {
            person: Object,
        },
        computed: {},
        methods: {

            refreshTabSuccess(response) {
                this.notes = response.data.notes
                this.noteTypeOptions = response.data.note_types
            },

            % if request.has_perm('people_profile.add_note'):

                addNoteInit() {
                    this.editNoteUUID = null
                    this.editNoteType = null
                    this.editNoteSubject = null
                    this.editNoteText = null
                    this.editNoteDelete = false
                    this.editNoteShowDialog = true
                },

            % endif

            % if request.has_perm('people_profile.edit_note'):

                editNoteInit(note) {
                    this.editNoteUUID = note.uuid
                    this.editNoteType = note.note_type
                    this.editNoteSubject = note.subject
                    this.editNoteText = note.text
                    this.editNoteDelete = false
                    this.editNoteShowDialog = true
                },

            % endif

            % if request.has_perm('people_profile.delete_note'):

                deleteNoteInit(note) {
                    this.editNoteUUID = note.uuid
                    this.editNoteType = note.note_type
                    this.editNoteSubject = note.subject
                    this.editNoteText = note.text
                    this.editNoteDelete = true
                    this.editNoteShowDialog = true
                },

            % endif

            % if request.has_any_perm('people_profile.add_note', 'people_profile.edit_note', 'people_profile.delete_note'):

                editNoteSave() {
                    this.editNoteSaving = true

                    let url = null
                    if (!this.editNoteUUID) {
                        url = '${master.get_action_url('profile_add_note', instance)}'
                    } else if (this.editNoteDelete) {
                        url = '${master.get_action_url('profile_delete_note', instance)}'
                    } else {
                        url = '${master.get_action_url('profile_edit_note', instance)}'
                    }

                    let params = {
                        uuid: this.editNoteUUID,
                        note_type: this.editNoteType,
                        note_subject: this.editNoteSubject,
                        note_text: this.editNoteText,
                    }

                    this.simplePOST(url, params, response => {
                        this.$emit('profile-changed', response.data)
                        this.editNoteSaving = false
                        this.editNoteShowDialog = false
                        this.refreshTab()
                    }, response => {
                        this.editNoteSaving = false
                    })
                },

            % endif
        },
    }

  </script>
</%def>

<%def name="make_notes_tab_component()">
  ${self.declare_notes_tab_vars()}
  <script type="text/javascript">

    NotesTab.data = function() { return NotesTabData }
    Vue.component('notes-tab', NotesTab)
    <% request.register_component('notes-tab', 'NotesTab') %>

  </script>
</%def>

% if expose_transactions:

    <%def name="declare_transactions_tab_vars()">
      <script type="text/javascript">

        let TransactionsTabData = {}

        let TransactionsTab = {
            template: '#transactions-tab-template',
            mixins: [TabMixin, SimpleRequestMixin],
            props: {
                person: Object,
            },
            computed: {},
            methods: {

                // nb. we override this completely, just tell the grid to refresh
                refreshTab() {
                    this.refreshingTab = true
                    this.$refs.transactionsGrid.loadAsyncData(null, () => {
                        this.refreshed = Date.now()
                        this.refreshingTab = false
                    })
                }
            },
        }

      </script>
    </%def>

    <%def name="make_transactions_tab_component()">
      ${self.declare_transactions_tab_vars()}
      <script type="text/javascript">

        TransactionsTab.data = function() { return TransactionsTabData }
        Vue.component('transactions-tab', TransactionsTab)
        <% request.register_component('transactions-tab', 'TransactionsTab') %>

      </script>
    </%def>

% endif

<%def name="declare_user_tab_vars()">
  <script type="text/javascript">

    let UserTabData = {
        % if hasattr(master, 'profile_tab_user'):
        refreshTabURL: '${url('people.profile_tab_user', uuid=person.uuid)}',
        % endif
        users: [],

        % if request.has_perm('users.create'):
            createUserShowDialog: false,
            createUserUsername: null,
            createUserActive: false,
            createUserSaving: false,
        % endif
    }

    let UserTab = {
        template: '#user-tab-template',
        mixins: [TabMixin, SimpleRequestMixin],
        props: {
            person: Object,
        },

        computed: {

            % if request.has_perm('users.create'):

                createUserSaveDisabled() {
                    if (this.createUserSaving) {
                        return true
                    }
                    if (!this.createUserUsername) {
                        return true
                    }
                    return false
                },

            % endif
        },

        methods: {

            refreshTabSuccess(response) {
                this.users = response.data.users
                this.createUserSuggestedUsername = response.data.suggested_username
            },

            % if request.has_perm('users.create'):

                createUserInit() {
                    this.createUserUsername = this.createUserSuggestedUsername
                    this.createUserActive = true
                    this.createUserShowDialog = true
                    this.$nextTick(() => {
                        this.$refs.username.focus()
                    })
                },

                createUserSave() {
                    this.createUserSaving = true

                    % if hasattr(master, 'profile_make_user'):
                    let url = '${master.get_action_url('profile_make_user', instance)}'
                    % endif
                    let params = {
                        username: this.createUserUsername,
                        active: this.createUserActive,
                    }

                    this.simplePOST(url, params, response => {
                        this.$emit('profile-changed', response.data)
                        this.createUserSaving = false
                        this.createUserShowDialog = false
                        this.refreshTab()
                    }, response => {
                        this.createUserSaving = false
                    })
                },

            % endif
        },
    }

  </script>
</%def>

<%def name="make_user_tab_component()">
  ${self.declare_user_tab_vars()}
  <script type="text/javascript">

    UserTab.data = function() { return UserTabData }
    Vue.component('user-tab', UserTab)
    <% request.register_component('user-tab', 'UserTab') %>

  </script>
</%def>

<%def name="make_profile_info_component()">

  ## DEPRECATED; called for back-compat
  ${self.declare_profile_info_vars()}

  <script>
    ProfileInfo.data = function() { return ProfileInfoData }
    Vue.component('profile-info', ProfileInfo)
    <% request.register_component('profile-info', 'ProfileInfo') %>
  </script>
</%def>

<%def name="render_vue_templates()">
  ${parent.render_vue_templates()}

  ${self.render_personal_tab_template()}

  % if expose_members:
      ${self.render_member_tab_template()}
  % endif

  ${self.render_customer_tab_template()}
  % if expose_customer_shoppers:
      ${self.render_shopper_tab_template()}
  % endif
  ${self.render_employee_tab_template()}
  ${self.render_notes_tab_template()}

  % if expose_transactions:
      ${transactions_grid.render_complete(allow_save_defaults=False)|n}
      ${self.render_transactions_tab_template()}
  % endif

  ${self.render_user_tab_template()}
  ${self.render_profile_info_template()}
</%def>

<%def name="modify_vue_vars()">
  ${parent.modify_vue_vars()}
  <script>

    % if request.has_perm('people_profile.view_versions'):
        ThisPage.props.viewingHistory = Boolean
        ThisPage.props.gettingRevisions = Boolean
        ThisPage.props.revisions = Array
        ThisPage.props.revisionVersionMap = null
    % endif

    let TabMixin = {

        data() {
            return {
                refreshed: null,
                refreshTabURL: null,
                refreshingTab: false,
            }
        },
        methods: {

            refreshIfNeeded(time) {
                if (this.refreshed && time && this.refreshed > time) {
                    return
                }
                this.refreshTab()
            },

            refreshTab() {

                if (this.refreshTabURL) {
                    this.refreshingTab = true
                    this.simpleGET(this.refreshTabURL, {}, response => {
                        this.refreshTabSuccess(response)
                        this.refreshTabSuccessExtra(response)
                        this.refreshed = Date.now()
                        this.refreshingTab = false
                    })
                }
            },

            // nb. subclass must define this as needed
            refreshTabSuccess(response) {},

            // nb. subclass may define this if needed
            refreshTabSuccessExtra(response) {},
        },
    }


    % if request.has_perm('people_profile.view_versions'):

        WholePageData.viewingHistory = false
        WholePageData.gettingRevisions = false
        WholePageData.gotRevisions = false
        WholePageData.revisions = []
        WholePageData.revisionVersionMap = null

        WholePage.methods.viewHistory = function() {
            this.viewingHistory = true

            if (!this.gotRevisions && !this.gettingRevisions) {
                this.getRevisions()
            }
        }

        WholePage.methods.refreshHistory = function() {
            if (!this.gettingRevisions) {
                this.getRevisions()
            }
        }

        WholePage.methods.getRevisions = function() {
            this.gettingRevisions = true

            let url = '${url('people.view_profile_revisions', uuid=person.uuid)}'
            this.simpleGET(url, {}, response => {
                this.revisions = response.data.data
                this.revisionVersionMap = response.data.vmap
                this.gotRevisions = true
                this.gettingRevisions = false
            }, response => {
                this.gettingRevisions = false
            })
        }

    % endif
  </script>
</%def>

<%def name="make_vue_components()">
  ${parent.make_vue_components()}

  ${self.make_personal_tab_component()}

  % if expose_members:
      ${self.make_member_tab_component()}
  % endif

  ${self.make_customer_tab_component()}
  % if expose_customer_shoppers:
      ${self.make_shopper_tab_component()}
  % endif
  ${self.make_employee_tab_component()}
  ${self.make_notes_tab_component()}

  % if expose_transactions:
      <script type="text/javascript">

        TransactionsGrid.data = function() { return TransactionsGridData }
        Vue.component('transactions-grid', TransactionsGrid)
        ## TODO: why is this line not needed?
        ## <% request.register_component('transactions-grid', 'TransactionsGrid') %>

      </script>
      ${self.make_transactions_tab_component()}
  % endif

  ${self.make_user_tab_component()}
  ${self.make_profile_info_component()}
</%def>

##############################
## DEPRECATED
##############################

<%def name="declare_profile_info_vars()"></%def>
