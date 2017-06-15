<template>
    <div :class="componentClass" :style="componentStyle">
        <span>Maintenance</span>
        <div class="info bar-popover" v-if="!dragging">
            <div class="field">Status: Maintenance</div>
            <div class="field">Sched. Start Time: <span class="start"></span>{{ startTime }}</div>
            <div class="field">Sched. End Time: <span class="end"></span>{{ endTime }}</div>
        </div>
    </div>
</template>

<script>
import moment from 'moment-timezone';

export default {
    name: 'GanttMaintenanceBar',
    props: ['assignment', 'start-date', 'timezone', 'selected', 'dragging', 'drag-offset'],
    data() {
        return {
        }
    },
    computed: {
        startTime() {
            const date = new Date(this.assignment.start_time);
            return this.formatDate(date);
        },
        endTime() {
            const date = new Date(this.assignment.end_time);
            return this.formatDate(date);
        },
        width() {
            var duration = (new Date(this.assignment.end_time) - new Date(this.assignment.start_time)) / 1000;
            return duration / (14 * 24 * 3600) * 100;
        },
        left() {
            var start = (new Date(this.assignment.start_time) - new Date(this.startDate)) / 1000;
            return start / (14 * 24 * 3600) * 100;
        },
        componentClass() {
            return {
                'bar status-bar maintenance': true,
                'selected': this.selected,
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
