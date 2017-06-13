<template>
    <div :class="componentClass" :style="{ left: left + '%', width: width + '%' }">
        <div class="flight-info-table-wrapper">
            <table class="flight-info">
                <tr>
                    <td class="org">{{ flight.origin }}</td>
                    <td class="number">{{ flight.number }}</td>
                    <td class="dest">{{ flight.destination }}</td>
                </tr>
            </table>
        </div>
        <div class="bar-popover">
            <div class="field">Flight <span class="number">{{ flight.number }}</span></div>
            <div class="field">Origin: <span class="org">{{ flight.origin }}</span></div>
            <div class="field">Destination: <span class="dest">{{ flight.destination }}</span></div>
            <div class="field">Sched. Depature Time: <span class="departure">{{ departureTime }}</span></div>
            <div class="field">Sched. Arrival Time: <span class="arrival">{{ arrivalTime }}</span></div>
            <div class="assignment-only" v-if="flight.actual_hobbs">
                <hr />
                <div class="field">
                    Projected Hobbs: <span class="projected-hobbs">{{ flight.actual_hobbs.toFixed(1) }}</span>
                </div>
                <div class="field">
                    Next Due Hobbs: <span class="next-due-hobbs"></span>{{ flight.next_due_hobbs.toFixed(1) }}
                </div>
                <div :class="fieldHobbsLeftClass">
                    Hobbs Left: <span class="hobbs-left">{{ (flight.next_due_hobbs - flight.actual_hobbs).toFixed(1) }}</span>
                </div>
            </div>
        </div>
    </div>
</template>

<script>
import moment from 'moment-timezone';

export default {
    name: 'GanttFlightBar',
    props: ['flight', 'start-date', 'timezone', 'selected', 'assigned'],
    data() {
        return {
        };
    },
    computed: {
        departureTime() {
            const date = new Date(this.flight.departure_datetime);
            return this.formatDate(date);
        },
        arrivalTime() {
            const date = new Date(this.flight.arrival_datetime);
            return this.formatDate(date);
        },
        width() {
            var duration = (new Date(this.flight.arrival_datetime) - new Date(this.flight.departure_datetime)) / 1000;
            return duration / (14 * 24 * 3600) * 100;
        },
        left() {
            var start = (new Date(this.flight.departure_datetime) - new Date(this.startDate)) / 1000;
            return start / (14 * 24 * 3600) * 100;
        },
        hobbs() {
            return this.flight.next_due_hobbs - this.flight.actual_hobbs;
        },
        componentClass() {
            return {
                'bar': true,
                'selected': this.selected,
                'assigned': this.assigned,
                'hobbs-green': this.hobbs < 15 && this.hobbs >= 8,
                'hobbs-yellow': this.hobbs < 8 && this.hobbs >= 0,
                'hobbs-red': this.hobbs < 0,
            };
        },
        fieldHobbsLeftClass() {
            return {
                'field field-hobbs-left': true,
                'hobbs-green': this.hobbs < 15 && this.hobbs >= 8,
                'hobbs-yellow': this.hobbs < 8 && this.hobbs >= 0,
                'hobbs-red': this.hobbs < 0,
            };
        }
    },
    methods: {
        formatDate(date, dateFormat = 'MM/DD/YYYY HH:mm:ss') {
            if (typeof date === 'string') {
                var _date = new Date(date);
            } else {
                var _date = new Date(date.getTime());
            }
            _date.setHours(parseInt(_date.getHours()) + parseInt(this.timezone));
            return moment(_date).tz('UTC').format(dateFormat);
        },
    }
}
</script>
