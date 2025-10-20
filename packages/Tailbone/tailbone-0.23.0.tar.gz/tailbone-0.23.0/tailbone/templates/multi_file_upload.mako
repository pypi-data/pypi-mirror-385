## -*- coding: utf-8; -*-

<%def name="render_template()">
  <script type="text/x-template" id="multi-file-upload-template">
    <section>
      <b-field class="file">
        <b-upload name="upload" multiple drag-drop expanded
                  v-model="files">
          <section class="section">
            <div class="content has-text-centered">
              <p>
                <b-icon pack="fas" icon="upload" size="is-large"></b-icon>
              </p>
              <p>Drop your files here or click to upload</p>
            </div>
          </section>
        </b-upload>
      </b-field>

      <div class="tags" style="max-width: 40rem;">
        <span v-for="(file, index) in files" :key="index" class="tag is-primary">
          {{file.name}}
          <button class="delete is-small" type="button"
                  @click="deleteFile(index)">
          </button>
        </span>
      </div>
    </section>
  </script>
</%def>

<%def name="declare_vars()">
  <script type="text/javascript">

    let MultiFileUpload = {
        template: '#multi-file-upload-template',
        methods: {

            deleteFile(index) {
                this.files.splice(index, 1);
            },
        },
    }

    let MultiFileUploadData = {
        files: [],
    }

  </script>
</%def>

<%def name="make_component()">
  <script type="text/javascript">

    MultiFileUpload.data = function() { return MultiFileUploadData }

    Vue.component('multi-file-upload', MultiFileUpload)

  </script>
</%def>
