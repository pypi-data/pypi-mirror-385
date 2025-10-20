## -*- coding: utf-8; -*-
<%namespace name="base_meta" file="/base_meta.mako" />
<%namespace name="page_help" file="/page_help.mako" />
<%namespace file="/field-components.mako" import="make_field_components" />
<%namespace file="/formposter.mako" import="declare_formposter_mixin" />
<%namespace file="/grids/filter-components.mako" import="make_grid_filter_components" />
<%namespace file="/buefy-components.mako" import="make_buefy_components" />
<%namespace file="/buefy-plugin.mako" import="make_buefy_plugin" />
<%namespace file="/http-plugin.mako" import="make_http_plugin" />
## <%namespace file="/grids/nav.mako" import="grid_index_nav" />
## <%namespace name="multi_file_upload" file="/multi_file_upload.mako" />
<!DOCTYPE html>
<html lang="en">
  <head>
    <meta http-equiv="content-type" content="text/html; charset=UTF-8" />
    <title>${base_meta.global_title()} &raquo; ${capture(self.title)|n}</title>
    ${base_meta.favicon()}
    ${self.header_core()}
    ${self.head_tags()}
  </head>

  <body>
    <div id="app" style="height: 100%;">
      <whole-page></whole-page>
    </div>

    ## TODO: this must come before the self.body() call..but why?
    ${declare_formposter_mixin()}

    ## content body from derived/child template
    ${self.body()}

    ## Vue app
    ${self.render_vue_templates()}
    ${self.modify_vue_vars()}
    ${self.make_vue_components()}
    ${self.make_vue_app()}
  </body>
</html>

<%def name="title()"></%def>

<%def name="content_title()">
  ${self.title()}
</%def>

<%def name="header_core()">
  ${self.core_javascript()}
  ${self.core_styles()}
</%def>

<%def name="core_javascript()">
  <script type="importmap">
    {
        ## TODO: eventually version / url should be configurable
        "imports": {
            "vue": "${h.get_liburl(request, 'bb_vue', prefix='tailbone')}",
            "@oruga-ui/oruga-next": "${h.get_liburl(request, 'bb_oruga', prefix='tailbone')}",
            "@oruga-ui/theme-bulma": "${h.get_liburl(request, 'bb_oruga_bulma', prefix='tailbone')}",
            "@fortawesome/fontawesome-svg-core": "${h.get_liburl(request, 'bb_fontawesome_svg_core', prefix='tailbone')}",
            "@fortawesome/free-solid-svg-icons": "${h.get_liburl(request, 'bb_free_solid_svg_icons', prefix='tailbone')}",
            "@fortawesome/vue-fontawesome": "${h.get_liburl(request, 'bb_vue_fontawesome', prefix='tailbone')}"
        }
    }
  </script>
  <script>
    // empty stub to avoid errors for older buefy templates
    const Vue = {
        component(tagname, classname) {},
    }
  </script>
</%def>

<%def name="core_styles()">
  % if user_css:
      ${h.stylesheet_link(user_css)}
  % else:
      ${h.stylesheet_link(h.get_liburl(request, 'bb_oruga_bulma_css', prefix='tailbone'))}
  % endif
</%def>

<%def name="head_tags()">
  ${self.extra_javascript()}
  ${self.extra_styles()}
</%def>

<%def name="extra_javascript()">
##   ## some commonly-useful logic for detecting (non-)numeric input
##   ${h.javascript_link(request.static_url('tailbone:static/js/numeric.js') + '?ver={}'.format(tailbone.__version__))}
## 
##   ## debounce, for better autocomplete performance
##   ${h.javascript_link(request.static_url('tailbone:static/js/debounce.js') + '?ver={}'.format(tailbone.__version__))}

##   ## Tailbone / Buefy stuff
##   ${h.javascript_link(request.static_url('tailbone:static/js/tailbone.buefy.numericinput.js') + '?ver={}'.format(tailbone.__version__))}
##   ${h.javascript_link(request.static_url('tailbone:static/js/tailbone.buefy.timepicker.js') + '?ver={}'.format(tailbone.__version__))}

##   <script type="text/javascript">
## 
##     ## NOTE: this code was copied from
##     ## https://bulma.io/documentation/components/navbar/#navbar-menu
## 
##     document.addEventListener('DOMContentLoaded', () => {
## 
##         // Get all "navbar-burger" elements
##         const $navbarBurgers = Array.prototype.slice.call(document.querySelectorAll('.navbar-burger'), 0)
## 
##         // Add a click event on each of them
##         $navbarBurgers.forEach( el => {
##             el.addEventListener('click', () => {
## 
##                 // Get the target from the "data-target" attribute
##                 const target = el.dataset.target
##                 const $target = document.getElementById(target)
## 
##                 // Toggle the "is-active" class on both the "navbar-burger" and the "navbar-menu"
##                 el.classList.toggle('is-active')
##                 $target.classList.toggle('is-active')
## 
##             })
##         })
##     })
## 
##   </script>
</%def>

<%def name="extra_styles()">

##   ${h.stylesheet_link(request.static_url('tailbone:static/css/base.css') + '?ver={}'.format(tailbone.__version__))}
##   ${h.stylesheet_link(request.static_url('tailbone:static/css/layout.css') + '?ver={}'.format(tailbone.__version__))}
##   ${h.stylesheet_link(request.static_url('tailbone:static/css/grids.css') + '?ver={}'.format(tailbone.__version__))}
##   ${h.stylesheet_link(request.static_url('tailbone:static/css/filters.css') + '?ver={}'.format(tailbone.__version__))}
##   ${h.stylesheet_link(request.static_url('tailbone:static/css/forms.css') + '?ver={}'.format(tailbone.__version__))}

  ${h.stylesheet_link(request.static_url('tailbone:static/css/grids.rowstatus.css') + '?ver={}'.format(tailbone.__version__))}
  ${h.stylesheet_link(request.static_url('tailbone:static/css/diffs.css') + '?ver={}'.format(tailbone.__version__))}

  ## nb. this is used (only?) in /generate-feature page
  ${h.stylesheet_link(request.static_url('tailbone:static/css/codehilite.css') + '?ver={}'.format(tailbone.__version__))}

  <style>

    /* ****************************** */
    /* page */
    /* ****************************** */

    /* nb. helps force footer to bottom of screen */
    html, body {
        height: 100%;
    }

    ## maybe add testing watermark
    % if not request.rattail_config.production():
        html, .navbar, .footer {
          background-image: url(${request.static_url('tailbone:static/img/testing.png')});
        }
    % endif

    ## maybe force global background color
    % if background_color:
        body, .navbar, .footer {
            background-color: ${background_color};
        }
    % endif

    #content-title h1 {
        max-width: 50%;
        overflow: hidden;
        text-overflow: ellipsis;
        white-space: nowrap;
    }

    ## TODO: is this a good idea?
    h1.title {
        font-size: 2rem;
        font-weight: bold;
        margin-bottom: 0 !important;
    }

    #context-menu {
        margin-bottom: 1em;
        /* margin-left: 1em; */
        text-align: right;
        /* white-space: nowrap; */
    }

    ## TODO: ugh why is this needed to center modal on screen?
    .modal .modal-content .modal-card {
        margin: auto;
    }

    .object-helpers .panel {
        margin: 1rem;
        margin-bottom: 1.5rem;
    }

    /* ****************************** */
    /* grids */
    /* ****************************** */

    .filters .filter-fieldname .button {
        min-width: ${filter_fieldname_width};
        justify-content: left;
    }
    .filters .filter-verb {
        min-width: ${filter_verb_width};
    }

    .grid-tools {
        display: flex;
        gap: 0.5rem;
        justify-content: end;
    }

    a.grid-action {
        align-items: center;
        display: inline-flex;
        gap: 0.1rem;
        white-space: nowrap;
    }

    /**************************************************
     * grid rows which are "checked" (selected)
     **************************************************/

    /* TODO: this references some color values, whereas it would be preferable
     * to refer to some sort of "state" instead, color of which was
     * configurable.  b/c these are just the default Buefy theme colors. */

    tr.is-checked {
        background-color: #7957d5;
        color: white;
    }

    tr.is-checked:hover {
        color: #363636;
    }

    tr.is-checked a {
        color: white;
    }

    tr.is-checked:hover a {
        color: #7957d5;
    }

    /* ****************************** */
    /* forms */
    /* ****************************** */

    /* note that these should only apply to "normal" primary forms */

    .form {
        padding-left: 5em;
    }

    /* .form-wrapper .form .field.is-horizontal .field-label .label, */
    .form-wrapper .field.is-horizontal .field-label {
        text-align: left;
        white-space: nowrap;
        min-width: 18em;
    }

    .form-wrapper .form .field.is-horizontal .field-body {
        min-width: 30em;
    }

    .form-wrapper .form .field.is-horizontal .field-body .autocomplete,
    .form-wrapper .form .field.is-horizontal .field-body .autocomplete .dropdown-trigger,
    .form-wrapper .form .field.is-horizontal .field-body .select,
    .form-wrapper .form .field.is-horizontal .field-body .select select {
        width: 100%;
    }

    .form-wrapper .form .buttons {
        padding-left: 10rem;
    }

    /******************************
     * fix datepicker within modals
     * TODO: someday this may not be necessary? cf.
     * https://github.com/buefy/buefy/issues/292#issuecomment-347365637
     ******************************/

    /* TODO: this does change some things, but does not actually work 100% */
    /* right for oruga 0.8.7 or 0.8.9 */

    .modal .animation-content .modal-card {
        overflow: visible !important;
    }

    .modal-card-body {
        overflow: visible !important;
    }

    /* TODO: a simpler option we might try sometime instead?  */
    /* cf. https://github.com/buefy/buefy/issues/292#issuecomment-1073851313 */

    /* .dropdown-content{ */
    /*     position: fixed; */
    /* } */

  </style>
  ${base_meta.extra_styles()}
</%def>

<%def name="make_feedback_component()">
  <% request.register_component('feedback-form', 'FeedbackForm') %>
  <script type="text/x-template" id="feedback-form-template">
    <div>

      <o-button variant="primary"
                @click="showFeedback()"
                icon-left="comment">
        Feedback
      </o-button>

      <o-modal v-model:active="showDialog">
        <div class="modal-card">

          <header class="modal-card-head">
            <p class="modal-card-title">
              User Feedback
            </p>
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
                       expanded>
              </b-input>
            </b-field>

            <b-field label="Referring URL">
              <b-input
                 v-model="referrer"
                 disabled expanded>
              </b-input>
            </b-field>

            <o-field label="Message">
              <o-input type="textarea"
                       v-model="message"
                       ref="message"
                       expanded>
              </o-input>
            </o-field>

            % if request.rattail_config.getbool('tailbone', 'feedback_allows_reply'):
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
            <o-button @click="showDialog = false">
              Cancel
            </o-button>
            <o-button variant="primary"
                      @click="sendFeedback()"
                      :disabled="sending || !message?.trim()">
              {{ sending ? "Working, please wait..." : "Send Message" }}
            </o-button>
          </footer>
        </div>
      </o-modal>
    </div>
  </script>
  <script>

    const FeedbackForm = {
        template: '#feedback-form-template',
        mixins: [SimpleRequestMixin],

        props: {
            action: String,
        },

        data() {
            return {
                referrer: null,
                % if request.user:
                    userUUID: ${json.dumps(request.user.uuid)|n},
                    userName: ${json.dumps(str(request.user))|n},
                % else:
                    userUUID: null,
                    userName: null,
                % endif
                message: null,
                pleaseReply: false,
                userEmail: null,
                showDialog: false,
                sending: false,
            }
        },

        methods: {

            pleaseReplyChanged(value) {
                this.$nextTick(() => {
                    this.$refs.userEmail.focus()
                })
            },

            showFeedback() {
                this.referrer = location.href
                this.message = null
                this.showDialog = true
                this.$nextTick(function() {
                    this.$refs.message.focus()
                })
            },

            sendFeedback() {
                this.sending = true

                const params = {
                    referrer: this.referrer,
                    user: this.userUUID,
                    user_name: this.userName,
                    please_reply_to: this.pleaseReply ? this.userEmail : '',
                    message: this.message?.trim(),
                }

                this.simplePOST(this.action, params, response => {

                    this.$buefy.toast.open({
                        message: "Message sent!  Thank you for your feedback.",
                        type: 'is-info',
                        duration: 4000, // 4 seconds
                    })

                    this.sending = false
                    this.showDialog = false

                }, response => {
                    this.sending = false
                })
            },
        }
    }

  </script>
</%def>

<%def name="make_menu_search_component()">
  <% request.register_component('menu-search', 'MenuSearch') %>
  <script type="text/x-template" id="menu-search-template">
    <div style="display: flex;">

      <a v-show="!searchActive"
         href="${url('home')}"
         class="navbar-item"
         style="display: flex; gap: 0.5rem;">
        ${base_meta.header_logo()}
        <div id="global-header-title">
          ${base_meta.global_title()}
        </div>
      </a>

      <div v-show="searchActive"
           class="navbar-item">
        <o-autocomplete ref="searchAutocomplete"
                        v-model="searchTerm"
                        :data="searchFilteredData"
                        field="label"
                        open-on-focus
                        keep-first
                        icon-pack="fas"
                        clearable
                        @select="searchSelect">
        </o-autocomplete>
      </div>
    </div>
  </script>
  <script>

    const MenuSearch = {
        template: '#menu-search-template',

        props: {
            searchData: Array,
        },

        data() {
            return {
                searchActive: false,
                searchTerm: null,
                searchInput: null,
            }
        },

        computed: {

            searchFilteredData() {
                if (!this.searchTerm || !this.searchTerm.length) {
                    return this.searchData
                }

                let terms = []
                for (let term of this.searchTerm.toLowerCase().split(' ')) {
                    term = term.trim()
                    if (term) {
                        terms.push(term)
                    }
                }
                if (!terms.length) {
                    return this.searchData
                }

                // all terms must match
                return this.searchData.filter((option) => {
                    let label = option.label.toLowerCase()
                    for (let term of terms) {
                        if (label.indexOf(term) < 0) {
                            return false
                        }
                    }
                    return true
                })
            },
        },

        mounted() {
            this.searchInput = this.$refs.searchAutocomplete.$el.querySelector('input')
            this.searchInput.addEventListener('keydown', this.searchKeydown)
        },

        beforeDestroy() {
            this.searchInput.removeEventListener('keydown', this.searchKeydown)
        },

        methods: {

            searchInit() {
                this.searchTerm = ''
                this.searchActive = true
                this.$nextTick(() => {
                    this.$refs.searchAutocomplete.focus()
                })
            },

            searchKeydown(event) {
                // ESC will dismiss searchbox
                if (event.which == 27) {
                    this.searchActive = false
                }
            },

            searchSelect(option) {
                location.href = option.url
            },
        },
    }

  </script>
</%def>

<%def name="render_vue_template_whole_page()">
  <script type="text/x-template" id="whole-page-template">
    <div id="whole-page" style="height: 100%; display: flex; flex-direction: column; justify-content: space-between;">

      <div class="header-wrapper">

        <header>

          <!-- this main menu, with search -->
          <nav class="navbar" role="navigation" aria-label="main navigation"
               style="display: flex; align-items: center;">

            <div class="navbar-brand">
              <menu-search :search-data="globalSearchData"
                           ref="menuSearch" />
              <a role="button" class="navbar-burger" data-target="navbarMenu" aria-label="menu" aria-expanded="false">
                <span aria-hidden="true"></span>
                <span aria-hidden="true"></span>
                <span aria-hidden="true"></span>
                <span aria-hidden="true"></span>
              </a>
            </div>

            <div class="navbar-menu" id="navbarMenu"
                 style="display: flex; align-items: center;"
                 >
              <div class="navbar-start">

                ## global search button
                <div v-if="globalSearchData.length"
                     class="navbar-item">
                  <o-button variant="primary"
                            size="small"
                            @click="globalSearchInit()">
                    <o-icon icon="search" size="small" />
                  </o-button>
                </div>

                ## main menu
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
                                    <% toggle = f'menu_{item_hash}_shown' %>
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

              </div><!-- navbar-start -->
              ${self.render_navbar_end()}
            </div>
          </nav>

          <!-- nb. this has index title, help button etc. -->
          <nav style="display: flex; justify-content: space-between; align-items: center; padding: 0.5rem;">

            ## Current Context
            <div style="display: flex; gap: 0.5rem; align-items: center;">
              % if master:
                  % if master.listing:
                      <h1 class="title">
                        ${index_title}
                      </h1>
                      % if master.creatable and getattr(master, 'show_create_link', True) and master.has_perm('create'):
                          <once-button type="is-primary"
                                       tag="a" href="${url('{}.create'.format(route_prefix))}"
                                       icon-left="plus"
                                       style="margin-left: 1rem;"
                                       text="Create New">
                          </once-button>
                      % endif
                  % elif index_url:
                      <h1 class="title">
                        ${h.link_to(index_title, index_url)}
                      </h1>
                      % if parent_url is not Undefined:
                          <h1 class="title">
                            &nbsp;&raquo;
                          </h1>
                          <h1 class="title">
                            ${h.link_to(parent_title, parent_url)}
                          </h1>
                      % elif instance_url is not Undefined:
                          <h1 class="title">
                            &nbsp;&raquo;
                          </h1>
                          <h1 class="title">
                            ${h.link_to(instance_title, instance_url)}
                          </h1>
                      % elif master.creatable and getattr(master, 'show_create_link', True) and master.has_perm('create'):
                          % if not request.matched_route.name.endswith('.create'):
                              <once-button type="is-primary"
                                           tag="a" href="${url('{}.create'.format(route_prefix))}"
                                           icon-left="plus"
                                           style="margin-left: 1rem;"
                                           text="Create New">
                              </once-button>
                          % endif
                      % endif
##                         % if master.viewing and grid_index:
##                             ${grid_index_nav()}
##                         % endif
                  % else:
                      <h1 class="title">
                        ${index_title}
                      </h1>
                  % endif
              % elif index_title:
                  % if index_url:
                      <h1 class="title">
                        ${h.link_to(index_title, index_url)}
                      </h1>
                  % else:
                      <h1 class="title">
                        ${index_title}
                      </h1>
                  % endif
              % endif

              % if expose_db_picker is not Undefined and expose_db_picker:
                  <span>DB:</span>
                  ${h.form(url('change_db_engine'), ref='dbPickerForm')}
                  ${h.csrf_token(request)}
                  ${h.hidden('engine_type', value=master.engine_type_key)}
                  <input type="hidden" name="referrer" :value="referrer" />
                  <b-select name="dbkey"
                            v-model="dbSelected"
                            @input="changeDB()">
                    % for option in db_picker_options:
                        <option value="${option.value}">
                          ${option.label}
                        </option>
                    % endfor
                  </b-select>
                  ${h.end_form()}
              % endif

            </div>

            <div style="display: flex; gap: 0.5rem;">

              ## Quickie Lookup
              % if quickie is not Undefined and quickie and request.has_perm(quickie.perm):
                  ${h.form(quickie.url, method='get', style='display: flex; gap: 0.5rem; margin-right: 1rem;')}
                    <b-input name="entry"
                             placeholder="${quickie.placeholder}"
                             autocomplete="off">
                    </b-input>
                    <o-button variant="primary"
                              native-type="submit"
                              icon-left="search">
                      Lookup
                    </o-button>
                  ${h.end_form()}
              % endif

              % if master and master.configurable and master.has_perm('configure'):
                  % if not request.matched_route.name.endswith('.configure'):
                      <once-button type="is-primary"
                                   tag="a"
                                   href="${url('{}.configure'.format(route_prefix))}"
                                   icon-left="cog"
                                   text="${(configure_button_title or "Configure") if configure_button_title is not Undefined else "Configure"}">
                      </once-button>
                  % endif
              % endif

              ## Theme Picker
              % if expose_theme_picker and request.has_perm('common.change_app_theme'):
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
              % endif

              % if help_url or help_markdown or can_edit_help:
                  <page-help
                    % if can_edit_help:
                    @configure-fields-help="configureFieldsHelp = true"
                    % endif
                    >
                  </page-help>
              % endif

              ## Feedback Button / Dialog
              % if request.has_perm('common.feedback'):
                  <feedback-form action="${url('feedback')}" />
              % endif
            </div>
          </nav>
        </header>

        ## Page Title
        % if capture(self.content_title):
            <section class="has-background-primary"
                     ## TODO: id is only for css, do we need it?
                     id="content-title"
                     style="padding: 0.5rem; padding-left: 1rem;">
              <div style="display: flex; align-items: center; gap: 1rem;">

                <h1 class="title has-text-white" v-html="contentTitleHTML" />

                <div style="flex-grow: 1; display: flex; gap: 0.5rem;">
                  ${self.render_instance_header_title_extras()}
                </div>

                <div style="display: flex; gap: 0.5rem;">
                  ${self.render_instance_header_buttons()}
                </div>

              </div>
            </section>
        % endif

      </div> <!-- header-wrapper -->

      <div class="content-wrapper"
           style="flex-grow: 1; padding: 0.5rem;">

        ## Page Body
        <section id="page-body">

          % if request.session.peek_flash('error'):
              % for error in request.session.pop_flash('error'):
                  <b-notification type="is-warning">
                    ${error}
                  </b-notification>
              % endfor
          % endif

          % if request.session.peek_flash('warning'):
              % for msg in request.session.pop_flash('warning'):
                  <b-notification type="is-warning">
                    ${msg}
                  </b-notification>
              % endfor
          % endif

          % if request.session.peek_flash():
              % for msg in request.session.pop_flash():
                  <b-notification type="is-info">
                    ${msg}
                  </b-notification>
              % endfor
          % endif

          ## true page content
          <div>
            ${self.render_this_page_component()}
          </div>
        </section>
      </div><!-- content-wrapper -->

      ## Footer
      <footer class="footer">
        <div class="content">
          ${base_meta.footer()}
        </div>
      </footer>
    </div>
  </script>
</%def>

<%def name="render_this_page_component()">
  <this-page @change-content-title="changeContentTitle"
             % if can_edit_help:
             :configure-fields-help="configureFieldsHelp"
             % endif
             >
  </this-page>
</%def>

<%def name="render_navbar_end()">
  <div class="navbar-end">
    ${self.render_user_menu()}
  </div>
</%def>

<%def name="render_user_menu()">
  % if request.user:
      <div class="navbar-item has-dropdown is-hoverable">
        % if messaging_enabled:
            <a class="navbar-link ${'has-background-danger has-text-white' if request.is_root else ''}">${request.user}${" ({})".format(inbox_count) if inbox_count else ''}</a>
        % else:
            <a class="navbar-link ${'has-background-danger has-text-white' if request.is_root else ''}">${request.user}</a>
        % endif
        <div class="navbar-dropdown">
          % if request.is_root:
              ${h.form(url('stop_root'), ref='stopBeingRootForm')}
              ${h.csrf_token(request)}
              <input type="hidden" name="referrer" value="${request.current_route_url()}" />
              <a @click="$refs.stopBeingRootForm.submit()"
                 class="navbar-item has-background-danger has-text-white">
                Stop being root
              </a>
              ${h.end_form()}
          % elif request.is_admin:
              ${h.form(url('become_root'), ref='startBeingRootForm')}
              ${h.csrf_token(request)}
              <input type="hidden" name="referrer" value="${request.current_route_url()}" />
              <a @click="$refs.startBeingRootForm.submit()"
                 class="navbar-item has-background-danger has-text-white">
                Become root
              </a>
              ${h.end_form()}
          % endif
          % if messaging_enabled:
              ${h.link_to("Messages{}".format(" ({})".format(inbox_count) if inbox_count else ''), url('messages.inbox'), class_='navbar-item')}
          % endif
          % if request.is_root or not request.user.prevent_password_change:
              ${h.link_to("Change Password", url('change_password'), class_='navbar-item')}
          % endif
          ${h.link_to("Edit Preferences", url('my.preferences'), class_='navbar-item')}
          ${h.link_to("Logout", url('logout'), class_='navbar-item')}
        </div>
      </div>
  % else:
      ${h.link_to("Login", url('login'), class_='navbar-item')}
  % endif
</%def>

<%def name="render_instance_header_title_extras()"></%def>

<%def name="render_instance_header_buttons()">
  ${self.render_crud_header_buttons()}
  ${self.render_prevnext_header_buttons()}
</%def>

<%def name="render_crud_header_buttons()">
% if master and master.viewing and not getattr(master, 'cloning', False):
      ## TODO: is there a better way to check if viewing parent?
      % if parent_instance is Undefined:
          % if master.editable and instance_editable and master.has_perm('edit'):
              <once-button tag="a" href="${master.get_action_url('edit', instance)}"
                           icon-left="edit"
                           text="Edit This">
              </once-button>
          % endif
          % if not getattr(master, 'cloning', False) and getattr(master, 'cloneable', False) and master.has_perm('clone'):
              <once-button tag="a" href="${master.get_action_url('clone', instance)}"
                           icon-left="object-ungroup"
                           text="Clone This">
              </once-button>
          % endif
          % if master.deletable and instance_deletable and master.has_perm('delete'):
              <once-button tag="a" href="${master.get_action_url('delete', instance)}"
                           type="is-danger"
                           icon-left="trash"
                           text="Delete This">
              </once-button>
          % endif
      % else:
          ## viewing row
          % if instance_deletable and master.has_perm('delete_row'):
              <once-button tag="a" href="${master.get_action_url('delete', instance)}"
                           type="is-danger"
                           icon-left="trash"
                           text="Delete This">
              </once-button>
          % endif
      % endif
  % elif master and master.editing:
      % if master.viewable and master.has_perm('view'):
          <once-button tag="a" href="${master.get_action_url('view', instance)}"
                       icon-left="eye"
                       text="View This">
          </once-button>
      % endif
      % if master.deletable and instance_deletable and master.has_perm('delete'):
          <once-button tag="a" href="${master.get_action_url('delete', instance)}"
                       type="is-danger"
                       icon-left="trash"
                       text="Delete This">
          </once-button>
      % endif
  % elif master and master.deleting:
      % if master.viewable and master.has_perm('view'):
          <once-button tag="a" href="${master.get_action_url('view', instance)}"
                       icon-left="eye"
                       text="View This">
          </once-button>
      % endif
      % if master.editable and instance_editable and master.has_perm('edit'):
          <once-button tag="a" href="${master.get_action_url('edit', instance)}"
                       icon-left="edit"
                       text="Edit This">
          </once-button>
      % endif
  % elif master and getattr(master, 'cloning', False):
      % if master.viewable and master.has_perm('view'):
          <once-button tag="a" href="${master.get_action_url('view', instance)}"
                       icon-left="eye"
                       text="View This">
          </once-button>
      % endif
  % endif
</%def>

<%def name="render_prevnext_header_buttons()">
  % if show_prev_next is not Undefined and show_prev_next:
      % if prev_url:
          <b-button tag="a" href="${prev_url}"
                    icon-pack="fas"
                    icon-left="arrow-left">
            Older
          </b-button>
      % else:
          <b-button tag="a" href="#"
                    disabled
                    icon-pack="fas"
                    icon-left="arrow-left">
            Older
          </b-button>
      % endif
      % if next_url:
          <b-button tag="a" href="${next_url}"
                    icon-pack="fas"
                    icon-left="arrow-right">
            Newer
          </b-button>
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

<%def name="render_vue_script_whole_page()">
  <script>

    const WholePage = {
        template: '#whole-page-template',
        mixins: [SimpleRequestMixin],
        computed: {},

        mounted() {
            window.addEventListener('keydown', this.globalKey)
            for (let hook of this.mountedHooks) {
                hook(this)
            }
        },
        beforeDestroy() {
            window.removeEventListener('keydown', this.globalKey)
        },

        methods: {

            changeContentTitle(newTitle) {
                this.contentTitleHTML = newTitle
            },

            % if expose_db_picker is not Undefined and expose_db_picker:
                changeDB() {
                    this.$refs.dbPickerForm.submit()
                },
            % endif

            % if expose_theme_picker and request.has_perm('common.change_app_theme'):
                changeTheme() {
                    this.$refs.themePickerForm.submit()
                },
            % endif

            globalKey(event) {

                // Ctrl+8 opens global search
                if (event.target.tagName == 'BODY') {
                    if (event.ctrlKey && event.key == '8') {
                        this.globalSearchInit()
                    }
                }
            },

            globalSearchInit() {
                this.$refs.menuSearch.searchInit()
            },

            toggleNestedMenu(hash) {
                const key = 'menu_' + hash + '_shown'
                this[key] = !this[key]
            },
        },
    }

    const WholePageData = {
        contentTitleHTML: ${json.dumps(capture(self.content_title))|n},
        globalSearchData: ${json.dumps(global_search_data)|n},
        mountedHooks: [],

        % if expose_db_picker is not Undefined and expose_db_picker:
            dbSelected: ${json.dumps(db_picker_selected)|n},
        % endif

        % if expose_theme_picker and request.has_perm('common.change_app_theme'):
            globalTheme: ${json.dumps(theme)|n},
            referrer: location.href,
        % endif

        % if can_edit_help:
            configureFieldsHelp: false,
        % endif
    }

    ## declare nested menu visibility toggle flags
    % for topitem in menus:
        % if topitem['is_menu']:
            % for item in topitem['items']:
                % if item['is_menu']:
                    WholePageData.menu_${id(item)}_shown = false
                % endif
            % endfor
        % endif
    % endfor

  </script>
</%def>

##############################
## vue components + app
##############################

<%def name="render_vue_templates()">
##   ${multi_file_upload.render_template()}
##   ${multi_file_upload.declare_vars()}

  ## global components used by various (but not all) pages
  ${make_field_components()}
  ${make_grid_filter_components()}

  ## global components for buefy-based template compatibility
  ${make_http_plugin()}
  ${make_buefy_plugin()}
  ${make_buefy_components()}

  ## special global components, used by WholePage
  ${self.make_menu_search_component()}
  ${page_help.render_template()}
  ${page_help.declare_vars()}
  % if request.has_perm('common.feedback'):
      ${self.make_feedback_component()}
  % endif

  ## DEPRECATED; called for back-compat
  ${self.render_whole_page_template()}

  ## DEPRECATED; called for back-compat
  ${self.declare_whole_page_vars()}
</%def>

## DEPRECATED; remains for back-compat
<%def name="render_whole_page_template()">
  ${self.render_vue_template_whole_page()}
  ${self.render_vue_script_whole_page()}
</%def>

<%def name="modify_vue_vars()">
  ## DEPRECATED; called for back-compat
  ${self.modify_whole_page_vars()}
</%def>

<%def name="make_vue_components()">
  ${page_help.make_component()}
  ## ${multi_file_upload.make_component()}

  ## DEPRECATED; called for back-compat (?)
  ${self.make_whole_page_component()}
</%def>

## DEPRECATED; remains for back-compat
<%def name="make_whole_page_component()">
  <script>
    WholePage.data = () => { return WholePageData }
  </script>
  <% request.register_component('whole-page', 'WholePage') %>
</%def>

<%def name="make_vue_app()">
  ## DEPRECATED; called for back-compat
  ${self.make_whole_page_app()}
</%def>

## DEPRECATED; remains for back-compat
<%def name="make_whole_page_app()">
  <script type="module">
    import {createApp} from 'vue'
    import {Oruga} from '@oruga-ui/oruga-next'
    import {bulmaConfig} from '@oruga-ui/theme-bulma'
    import { library } from "@fortawesome/fontawesome-svg-core"
    import { fas } from "@fortawesome/free-solid-svg-icons"
    import { FontAwesomeIcon } from "@fortawesome/vue-fontawesome"
    library.add(fas)

    const app = createApp()
    app.component('vue-fontawesome', FontAwesomeIcon)

    % if hasattr(request, '_tailbone_registered_components'):
        % for tagname, classname in request._tailbone_registered_components.items():
            app.component('${tagname}', ${classname})
        % endfor
    % endif

    app.use(Oruga, {
        ...bulmaConfig,
        iconComponent: 'vue-fontawesome',
        iconPack: 'fas',
    })

    app.use(HttpPlugin)
    app.use(BuefyPlugin)

    app.mount('#app')
  </script>
</%def>

##############################
## DEPRECATED
##############################

<%def name="declare_whole_page_vars()"></%def>

<%def name="modify_whole_page_vars()"></%def>
