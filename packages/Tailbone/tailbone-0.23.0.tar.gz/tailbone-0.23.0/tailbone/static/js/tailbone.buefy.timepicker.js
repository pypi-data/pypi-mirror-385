
const TailboneTimepicker = {

    template: [
        '<b-timepicker',
        ':name="name"',
        ':id="id"',
        'editable',
        'placeholder="Click to select ..."',
        'icon-pack="fas"',
        'icon="clock"',
        ':value="value ? parseTime(value) : null"',
        'hour-format="12"',
        '@input="timeChanged"',
        ':time-formatter="formatTime"',
        '>',
        '</b-timepicker>'
    ].join(' '),

    props: {
        name: String,
        id: String,
        value: String,
    },

    methods: {

        formatTime(time) {
            if (time === null) {
                return null
            }

            let h = time.getHours()
            let m = time.getMinutes()
            let s = time.getSeconds()

            h = h < 10 ? '0' + h : h
            m = m < 10 ? '0' + m : m
            s = s < 10 ? '0' + s : s

            return h + ':' + m + ':' + s
        },

        parseTime(time) {

            if (time.getHours) {
                return time
            }

            let found = time.match(/^(\d\d):(\d\d):\d\d$/)
            if (found) {
                return new Date(null, null, null,
                                parseInt(found[1]), parseInt(found[2]))
            }
        },

        timeChanged(time) {
            this.$emit('input', time)
        },
    },
}

Vue.component('tailbone-timepicker', TailboneTimepicker)
