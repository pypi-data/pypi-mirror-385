## -*- coding: utf-8; -*-

<%def name="view_profile_button(person)">
  <div class="buttons">
    <b-button type="is-primary"
              tag="a" href="${url('people.view_profile', uuid=person.uuid)}"
              icon-pack="fas"
              icon-left="user">
      ${person}
    </b-button>
  </div>
</%def>

<%def name="view_profiles_helper(people)">
  % if request.has_perm('people.view_profile'):
      <nav class="panel">
        <p class="panel-heading">Profiles</p>
        <div class="panel-block">
          <div style="display: flex; flex-direction: column;">
            <p class="block">View full profile for:</p>
            % for person in people:
                ${view_profile_button(person)}
            % endfor
          </div>
        </div>
      </nav>
  % endif
</%def>
