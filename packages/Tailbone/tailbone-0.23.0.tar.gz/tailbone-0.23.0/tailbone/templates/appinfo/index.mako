## -*- coding: utf-8; -*-
<%inherit file="wuttaweb:templates/appinfo/index.mako" />

<%def name="page_content()">
  <div class="buttons">

    <once-button type="is-primary"
                 tag="a" href="${url('tables')}"
                 icon-pack="fas"
                 icon-left="eye"
                 text="Tables">
    </once-button>

    <once-button type="is-primary"
                 tag="a" href="${url('model_views')}"
                 icon-pack="fas"
                 icon-left="eye"
                 text="Model Views">
    </once-button>

    <once-button type="is-primary"
                 tag="a" href="${url('configure_menus')}"
                 icon-pack="fas"
                 icon-left="cog"
                 text="Configure Menus">
    </once-button>

  </div>

  ${parent.page_content()}
</%def>
