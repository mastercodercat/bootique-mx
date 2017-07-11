<template>
    <div :class="componentClass" :style="componentStyle">
        <div class="flight-info-table-wrapper">
            <table class="flight-info">
                <tr>
                    <td class="org">{{ flight.origin }}</td>
                    <td class="number">{{ flight.number }}</td>
                    <td class="dest">{{ flight.destination }}</td>
                </tr>
            </table>
        </div>
        <div class="bar-popover" v-if="!dragging">
            <div class="field">Flight <span class="number">{{ flight.number }}</span></div>
            <div class="field">Origin: <span class="org">{{ flight.origin }}</span></div>
            <div class="field">Destination: <span class="dest">{{ flight.destination }}</span></div>
            <div class="field">Sched. OUT Time: <span class="departure">{{ scheduledOutDateTimeFormatted }}</span></div>
            <div class="field">Sched. IN Time: <span class="arrival">{{ scheduledInDateTimeFormatted }}</span></div>
            <template v-if="isEstimated">
                <div class="field">Estimated OUT Time: <span class="departure">{{ estimatedOutDateTimeFormatted }}</span></div>
                <div class="field">Estimated IN Time: <span class="arrival">{{ estimatedInDateTimeFormatted }}</span></div>
            </template>
            <template v-if="isActual">
                <div class="field">Actual OUT Time: <span class="departure">{{ actualOutDateTimeFormatted }}</span></div>
                <div class="field">Actual IN Time: <span class="arrival">{{ actualInDateTimeFormatted }}</span></div>
            </template>
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
            <a class="edit-flight-link"
                :href="`/routeplanning/flights/${flight.flight_id}`"
                v-if="writable">
                <i class="fa fa-pencil-square-o"></i>
            </a>
        </div>
    </div>
</template>

<script>
import moment from 'moment-timezone';

export default {
    name: 'GanttFlightBar',
    props: [
        'flight', 'start-date', 'timezone', 'selected', 'assigned',
        'dragging', 'drag-offset', 'writable',
    ],
    data() {
        return {
        };
    },
    computed: {
        scheduledOutDateTimeFormatted() {
            const date = new Date(this.flight.scheduled_out_datetime);
            return this.formatDate(date);
        },
        scheduledInDateTimeFormatted() {
            const date = new Date(this.flight.scheduled_in_datetime);
            return this.formatDate(date);
        },
        estimatedOutDateTimeFormatted() {
            const date = new Date(this.flight.estimated_out_datetime);
            return this.formatDate(date);
        },
        estimatedInDateTimeFormatted() {
            const date = new Date(this.flight.estimated_in_datetime);
            return this.formatDate(date);
        },
        actualOutDateTimeFormatted() {
            const date = new Date(this.flight.actual_out_datetime);
            return this.formatDate(date);
        },
        actualInDateTimeFormatted() {
            const date = new Date(this.flight.actual_in_datetime);
            return this.formatDate(date);
        },
        width() {
            var duration = (this.endTime - this.startTime) / 1000;
            return duration / (14 * 24 * 3600) * 100;
        },
        left() {
            var start = (this.startTime - new Date(this.startDate)) / 1000;
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
                'drag-clone': this.dragging,
            };
        },
        componentStyle() {
            const style = {
                left: this.left + '%',
                width: this.width + '%'
            };
            if (this.dragging && this.dragOffset) {
                style.transform = `translate(${this.dragOffset.x}px, ${this.dragOffset.y}px)`;
            }
            return style;
        },
        fieldHobbsLeftClass() {
            return {
                'field field-hobbs-left': true,
                'hobbs-green': this.hobbs < 15 && this.hobbs >= 8,
                'hobbs-yellow': this.hobbs < 8 && this.hobbs >= 0,
                'hobbs-red': this.hobbs < 0,
            };
        },
        isEstimated() {
            return this.flight.estimated_in_datetime && this.flight.estimated_out_datetime;
        },
        isActual() {
            return this.flight.actual_in_datetime && this.flight.actual_out_datetime;
        },
        startTime() {
            if (this.isActual) {
                return new Date(this.flight.actual_out_datetime);
            }
            else if (this.isEstimated) {
                return new Date(this.flight.estimated_out_datetime);
            }
            else {
                return new Date(this.flight.scheduled_out_datetime)
            }
        },
        endTime() {
            if (this.isActual) {
                return new Date(this.flight.actual_in_datetime);
            }
            else if (this.isEstimated) {
                return new Date(this.flight.estimated_in_datetime);
            }
            else {
                return new Date(this.flight.scheduled_in_datetime)
            }
        },
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
