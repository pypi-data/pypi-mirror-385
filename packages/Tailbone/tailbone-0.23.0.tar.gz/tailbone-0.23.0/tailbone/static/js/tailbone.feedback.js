
let FeedbackForm = {
    props: ['action', 'message'],
    template: '#feedback-template',
    mixins: [FormPosterMixin],
    methods: {

        pleaseReplyChanged(value) {
            this.$nextTick(() => {
                this.$refs.userEmail.focus()
            })
        },

        showFeedback() {
            this.referrer = location.href
            this.showDialog = true
            this.$nextTick(function() {
                this.$refs.textarea.focus()
            })
        },

        sendFeedback() {

            let params = {
                referrer: this.referrer,
                user: this.userUUID,
                user_name: this.userName,
                please_reply_to: this.pleaseReply ? this.userEmail : null,
                message: this.message.trim(),
            }

            this.submitForm(this.action, params, response => {

                this.$buefy.toast.open({
                    message: "Message sent!  Thank you for your feedback.",
                    type: 'is-info',
                    duration: 4000, // 4 seconds
                })

                this.showDialog = false
                // clear out message, in case they need to send another
                this.message = ""
            })
        },
    }
}

let FeedbackFormData = {
    referrer: null,
    userUUID: null,
    userName: null,
    pleaseReply: false,
    userEmail: null,
    showDialog: false,
}
