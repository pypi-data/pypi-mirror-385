## -*- coding: utf-8; -*-
<%inherit file="wuttaweb:templates/base.mako" />
<%namespace name="base_meta" file="/base_meta.mako" />
<%namespace file="/formposter.mako" import="declare_formposter_mixin" />
<%namespace file="/grids/filter-components.mako" import="make_grid_filter_components" />
<%namespace name="page_help" file="/page_help.mako" />

<%def name="base_styles()">
  ${parent.base_styles()}
  ${h.stylesheet_link(request.static_url('tailbone:static/css/diffs.css') + '?ver={}'.format(tailbone.__version__))}
  <style>

    .filters .filter-fieldname .field,
    .filters .filter-fieldname .field label {
        width: 100%;
    }

    .filters .filter-fieldname,
    .filters .filter-fieldname .field label,
    .filters .filter-fieldname .button {
        justify-content: left;
    }

    .filters .filter-verb .select,
    .filters .filter-verb .select select {
        width: 100%;
    }

    % if filter_fieldname_width is not Undefined:

        .filters .filter-fieldname,
        .filters .filter-fieldname .button {
            min-width: ${filter_fieldname_width};
        }

        .filters .filter-verb {
            min-width: ${filter_verb_width};
        }

    % endif

  </style>
</%def>

<%def name="before_content()">
  ## TODO: this must come before the self.body() call..but why?
  ${declare_formposter_mixin()}
</%def>

<%def name="render_navbar_brand()">
  <div class="navbar-brand">
    <a class="navbar-item" href="${url('home')}"
       v-show="!menuSearchActive">
      <div style="display: flex; align-items: center;">
        ${base_meta.header_logo()}
        <div id="navbar-brand-title">
          ${base_meta.global_title()}
        </div>
      </div>
    </a>
    <div v-show="menuSearchActive"
         class="navbar-item">
      <b-autocomplete ref="menuSearchAutocomplete"
                      v-model="menuSearchTerm"
                      :data="menuSearchFilteredData"
                      field="label"
                      open-on-focus
                      keep-first
                      icon-pack="fas"
                      clearable
                      @keydown.native="menuSearchKeydown"
                      @select="menuSearchSelect">
      </b-autocomplete>
    </div>
    <a role="button" class="navbar-burger" data-target="navbar-menu" aria-label="menu" aria-expanded="false">
      <span aria-hidden="true"></span>
      <span aria-hidden="true"></span>
      <span aria-hidden="true"></span>
    </a>
  </div>
</%def>

<%def name="render_navbar_start()">
  <div class="navbar-start">

    <div v-if="menuSearchData.length"
         class="navbar-item">
      <b-button type="is-primary"
                size="is-small"
                @click="menuSearchInit()">
        <span><i class="fa fa-search"></i></span>
      </b-button>
    </div>

    % for topitem in menus:
        % if topitem['is_link']:
            ${h.link_to(topitem['title'], topitem['url'], target=topitem['target'], class_='navbar-item')}
        % else:
            <div class="navbar-item has-dropdown is-hoverable">
              <a class="navbar-link">${topitem['title']}</a>
              <div class="navbar-dropdown">
                % for item in topitem['items']:
                    % if item['is_menu']:
                        <% item_hash = id(item) %>
                        <% toggle = 'menu_{}_shown'.format(item_hash) %>
                        <div>
                          <a class="navbar-link" @click.prevent="toggleNestedMenu('${item_hash}')">
                            ${item['title']}
                          </a>
                        </div>
                        % for subitem in item['items']:
                            % if subitem['is_sep']:
                                <hr class="navbar-divider" v-show="${toggle}">
                            % else:
                                ${h.link_to("{}".format(subitem['title']), subitem['url'], class_='navbar-item nested', target=subitem['target'], **{'v-show': toggle})}
                            % endif
                        % endfor
                    % else:
                        % if item['is_sep']:
                            <hr class="navbar-divider">
                        % else:
                            ${h.link_to(item['title'], item['url'], class_='navbar-item', target=item['target'])}
                        % endif
                    % endif
                % endfor
              </div>
            </div>
        % endif
    % endfor

  </div>
</%def>

<%def name="render_theme_picker()">
  % if expose_theme_picker and request.has_perm('common.change_app_theme'):
      <div class="level-item">
        ${h.form(url('change_theme'), method="post", ref='themePickerForm')}
          ${h.csrf_token(request)}
          <input type="hidden" name="referrer" :value="referrer" />
          <div style="display: flex; align-items: center; gap: 0.5rem;">
            <span>Theme:</span>
            <b-select name="theme"
                      v-model="globalTheme"
                      @input="changeTheme()">
              % for option in theme_picker_options:
                  <option value="${option.value}">
                    ${option.label}
                  </option>
              % endfor
            </b-select>
          </div>
        ${h.end_form()}
      </div>
  % endif
</%def>

<%def name="render_feedback_button()">

  <div class="level-item">
    <page-help
      % if can_edit_help:
      @configure-fields-help="configureFieldsHelp = true"
      % endif
      />
  </div>

  ${parent.render_feedback_button()}
</%def>

<%def name="render_crud_header_buttons()">
  % if master:
      % if master.viewing:
          % if instance_editable and master.has_perm('edit'):
              <wutta-button once
                            tag="a" href="${master.get_action_url('edit', instance)}"
                            icon-left="edit"
                            label="Edit This" />
          % endif
          % if getattr(master, 'cloneable', False) and not master.cloning and master.has_perm('clone'):
              <wutta-button once
                            tag="a" href="${master.get_action_url('clone', instance)}"
                            icon-left="object-ungroup"
                            label="Clone This" />
          % endif
          % if instance_deletable and master.has_perm('delete'):
              <wutta-button once type="is-danger"
                            tag="a" href="${master.get_action_url('delete', instance)}"
                            icon-left="trash"
                            label="Delete This" />
          % endif
      % elif master.editing:
          % if master.has_perm('view'):
              <wutta-button once
                            tag="a" href="${master.get_action_url('view', instance)}"
                            icon-left="eye"
                            label="View This" />
          % endif
          % if instance_deletable and master.has_perm('delete'):
              <wutta-button once type="is-danger"
                            tag="a" href="${master.get_action_url('delete', instance)}"
                            icon-left="trash"
                            label="Delete This" />
          % endif
      % elif master.deleting:
          % if master.has_perm('view'):
              <wutta-button once
                            tag="a" href="${master.get_action_url('view', instance)}"
                            icon-left="eye"
                            label="View This" />
          % endif
          % if instance_editable and master.has_perm('edit'):
              <wutta-button once
                            tag="a" href="${master.get_action_url('edit', instance)}"
                            icon-left="edit"
                            label="Edit This" />
          % endif
      % endif
  % endif
</%def>

<%def name="render_prevnext_header_buttons()">
  % if show_prev_next is not Undefined and show_prev_next:
      % if prev_url:
          <wutta-button once
                        tag="a" href="${prev_url}"
                        icon-left="arrow-left"
                        label="Older" />
      % else:
          <b-button tag="a" href="#"
                    disabled
                    icon-pack="fas"
                    icon-left="arrow-left">
            Older
          </b-button>
      % endif
      % if next_url:
          <wutta-button once
                        tag="a" href="${next_url}"
                        icon-left="arrow-right"
                        label="Newer" />
      % else:
          <b-button tag="a" href="#"
                    disabled
                    icon-pack="fas"
                    icon-left="arrow-right">
            Newer
          </b-button>
      % endif
  % endif
</%def>

<%def name="render_this_page_component()">
  <this-page @change-content-title="changeContentTitle"
             % if can_edit_help:
                 :configure-fields-help="configureFieldsHelp"
             % endif
             />
</%def>

<%def name="render_vue_template_feedback()">
  <script type="text/x-template" id="feedback-template">
    <div>

      <div class="level-item">
        <b-button type="is-primary"
                  @click="showFeedback()"
                  icon-pack="fas"
                  icon-left="comment">
          Feedback
        </b-button>
      </div>

      <b-modal has-modal-card
               :active.sync="showDialog">
        <div class="modal-card">

          <header class="modal-card-head">
            <p class="modal-card-title">User Feedback</p>
          </header>

          <section class="modal-card-body">
            <p class="block">
              Questions, suggestions, comments, complaints, etc.
              <span class="red">regarding this website</span> are
              welcome and may be submitted below.
            </p>

            <b-field label="User Name">
              <b-input v-model="userName"
                       % if request.user:
                           disabled
                       % endif
                       >
              </b-input>
            </b-field>

            <b-field label="Referring URL">
              <b-input
                 v-model="referrer"
                 disabled="true">
              </b-input>
            </b-field>

            <b-field label="Message">
              <b-input type="textarea"
                       v-model="message"
                       ref="textarea">
              </b-input>
            </b-field>

            % if config.get_bool('tailbone.feedback_allows_reply'):
                <div class="level">
                  <div class="level-left">
                    <div class="level-item">
                      <b-checkbox v-model="pleaseReply"
                                  @input="pleaseReplyChanged">
                        Please email me back{{ pleaseReply ? " at: " : "" }}
                      </b-checkbox>
                    </div>
                    <div class="level-item" v-show="pleaseReply">
                      <b-input v-model="userEmail"
                               ref="userEmail">
                      </b-input>
                    </div>
                  </div>
                </div>
            % endif

          </section>

          <footer class="modal-card-foot">
            <b-button @click="showDialog = false">
              Cancel
            </b-button>
            <b-button type="is-primary"
                      icon-pack="fas"
                      icon-left="paper-plane"
                      @click="sendFeedback()"
                      :disabled="sendingFeedback || !message || !message.trim()">
              {{ sendingFeedback ? "Working, please wait..." : "Send Message" }}
            </b-button>
          </footer>
        </div>
      </b-modal>

    </div>
  </script>
</%def>

<%def name="render_vue_script_feedback()">
  ${parent.render_vue_script_feedback()}
  <script>

    WuttaFeedbackForm.template = '#feedback-template'
    WuttaFeedbackForm.props.message = String

    % if config.get_bool('tailbone.feedback_allows_reply'):

        WuttaFeedbackFormData.pleaseReply = false
        WuttaFeedbackFormData.userEmail = null

        WuttaFeedbackForm.methods.pleaseReplyChanged = function(value) {
            this.$nextTick(() => {
                this.$refs.userEmail.focus()
            })
        }

        WuttaFeedbackForm.methods.getExtraParams = function() {
            return {
                please_reply_to: this.pleaseReply ? this.userEmail : null,
            }
        }

    % endif

    // TODO: deprecate / remove these
    const FeedbackForm = WuttaFeedbackForm
    const FeedbackFormData = WuttaFeedbackFormData

  </script>
</%def>

<%def name="render_vue_templates()">
  ${parent.render_vue_templates()}
  ${page_help.render_template()}
  ${page_help.declare_vars()}
</%def>

<%def name="modify_vue_vars()">
  ${parent.modify_vue_vars()}
  <script>

    ##############################
    ## menu search
    ##############################

    WholePageData.menuSearchActive = false
    WholePageData.menuSearchTerm = ''
    WholePageData.menuSearchData = ${json.dumps(global_search_data or [])|n}

    WholePage.computed.menuSearchFilteredData = function() {
        if (!this.menuSearchTerm.length) {
            return this.menuSearchData
        }

        const terms = []
        for (let term of this.menuSearchTerm.toLowerCase().split(' ')) {
            term = term.trim()
            if (term) {
                terms.push(term)
            }
        }
        if (!terms.length) {
            return this.menuSearchData
        }

        // all terms must match
        return this.menuSearchData.filter((option) => {
            const label = option.label.toLowerCase()
            for (const term of terms) {
                if (label.indexOf(term) < 0) {
                    return false
                }
            }
            return true
        })
    }

    WholePage.methods.globalKey = function(event) {

        // Ctrl+8 opens menu search
        if (event.target.tagName == 'BODY') {
            if (event.ctrlKey && event.key == '8') {
                this.menuSearchInit()
            }
        }
    }

    WholePage.mounted = function() {
        window.addEventListener('keydown', this.globalKey)
        for (let hook of this.mountedHooks) {
            hook(this)
        }
    }

    WholePage.beforeDestroy = function() {
        window.removeEventListener('keydown', this.globalKey)
    }

    WholePage.methods.menuSearchInit = function() {
        this.menuSearchTerm = ''
        this.menuSearchActive = true
        this.$nextTick(() => {
            this.$refs.menuSearchAutocomplete.focus()
        })
    }

    WholePage.methods.menuSearchKeydown = function(event) {

        // ESC will dismiss searchbox
        if (event.which == 27) {
            this.menuSearchActive = false
        }
    }

    WholePage.methods.menuSearchSelect = function(option) {
        location.href = option.url
    }

    ##############################
    ## theme picker
    ##############################

    % if expose_theme_picker and request.has_perm('common.change_app_theme'):

        WholePageData.globalTheme = ${json.dumps(theme or None)|n}
        ## WholePageData.referrer = location.href

        WholePage.methods.changeTheme = function() {
            this.$refs.themePickerForm.submit()
        }

    % endif

    ##############################
    ## edit fields help
    ##############################

    % if can_edit_help:
        WholePageData.configureFieldsHelp = false
    % endif

  </script>
</%def>

<%def name="make_vue_components()">
  ${parent.make_vue_components()}
  ${h.javascript_link(request.static_url('tailbone:static/js/tailbone.buefy.datepicker.js') + f'?ver={tailbone.__version__}')}
  ${h.javascript_link(request.static_url('tailbone:static/js/tailbone.buefy.numericinput.js') + f'?ver={tailbone.__version__}')}
  ${h.javascript_link(request.static_url('tailbone:static/js/tailbone.buefy.oncebutton.js') + f'?ver={tailbone.__version__}')}
  ${h.javascript_link(request.static_url('tailbone:static/js/tailbone.buefy.timepicker.js') + f'?ver={tailbone.__version__}')}
  ${make_grid_filter_components()}
  ${page_help.make_component()}
</%def>
