## -*- coding: utf-8; -*-
<%inherit file="/form.mako" />

<%def name="title()">New ${model_title_plural if getattr(master, 'creates_multiple', False) else model_title}</%def>

${parent.body()}
