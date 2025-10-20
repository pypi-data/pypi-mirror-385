## -*- coding: utf-8; -*-

<%def name="declare_formposter_mixin()">
  <script type="text/javascript">

    let SimpleRequestMixin = {
        methods: {

            simpleGET(url, params, success, failure) {

                this.$http.get(url, {params: params}).then(response => {

                    if (response.data.error) {
                        this.$buefy.toast.open({
                            message: `Request failed:  ${'$'}{response.data.error}`,
                            type: 'is-danger',
                            duration: 4000, // 4 seconds
                        })
                        if (failure) {
                            failure(response)
                        }

                    } else {
                        success(response)
                    }

                }, response => {
                    this.$buefy.toast.open({
                        message: "Request failed:  (unknown server error)",
                        type: 'is-danger',
                        duration: 4000, // 4 seconds
                    })
                    if (failure) {
                        failure(response)
                    }
                })

            },

            simplePOST(action, params, success, failure) {

                let csrftoken = ${json.dumps(h.get_csrf_token(request))|n}

                let headers = {
                    '${csrf_header_name}': csrftoken,
                }

                this.$http.post(action, params, {headers: headers}).then(response => {

                    if (response.data.error) {
                        this.$buefy.toast.open({
                            message: "Submit failed:  " + (response.data.error ||
                                                           "(unknown error)"),
                            type: 'is-danger',
                            duration: 4000, // 4 seconds
                        })
                        if (failure) {
                            failure(response)
                        }

                    } else {
                        success(response)
                    }

                }, response => {
                    this.$buefy.toast.open({
                        message: "Submit failed!  (unknown server error)",
                        type: 'is-danger',
                        duration: 4000, // 4 seconds
                    })
                    if (failure) {
                        failure(response)
                    }
                })
            },
        },
    }

    // TODO: deprecate / remove
    SimpleRequestMixin.methods.submitForm = SimpleRequestMixin.methods.simplePOST
    let FormPosterMixin = SimpleRequestMixin

  </script>
</%def>
