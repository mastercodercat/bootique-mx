<template>
    <div :class="componentClass" :style="componentStyle">
        <div class="text">
            <span>Unscheduled Flight</span>
        </div>
        <div class="bar-popover" v-if="!dragging">
            <div class="field">Unscheduled Flight</div>
            <div class="field">Origin: <span class="org">{{ assignment.origin }}</span></div>
            <div class="field">Destination: <span class="dest">{{ assignment.destination }}</span></div>
            <div class="field">Sched. Depature Time: <span class="departure">{{ departureTime }}</span></div>
            <div class="field">Sched. Arrival Time: <span class="arrival">{{ arrivalTime }}</span></div>
            <div class="assignment-only">
                <hr />
                <div class="field">
                    Projected Hobbs: <span class="projected-hobbs">{{ assignment.actual_hobbs.toFixed(1) }}</span>
                </div>
                <div class="field">
                    Next Due Hobbs: <span class="next-due-hobbs"></span>{{ assignment.next_due_hobbs.toFixed(1) }}
                </div>
                <div :class="fieldHobbsLeftClass">
                    Hobbs Left: <span class="hobbs-left">{{ (assignment.next_due_hobbs - assignment.actual_hobbs).toFixed(1) }}</span>
                </div>
            </div>
        </div>
    </div>
</template>

<script>
import moment from 'moment-timezone';
import interact from 'interactjs';

export default {
    name: 'GanttUnscheduledFlightBar',
    props: ['assignment', 'start-date', 'timezone', 'selected', 'dragging', 'drag-offset', 'unit'],
    data() {
        return {
            resizing: false,
            orgWidth: 0,
            barWidth: 0,
            transform: '',
            deltaWidth: 0,
            pos: 0,
        };
    },
    computed: {
        departureTime() {
            const date = new Date(this.assignment.departure_datetime);
            return this.formatDate(date);
        },
        arrivalTime() {
            const date = new Date(this.assignment.arrival_datetime);
            return this.formatDate(date);
        },
        width() {
            var duration = (new Date(this.assignment.arrival_datetime) - new Date(this.assignment.departure_datetime)) / 1000;
            return duration / (14 * 24 * 3600) * 100;
        },
        left() {
            var start = (new Date(this.assignment.departure_datetime) - new Date(this.startDate)) / 1000;
            return start / (14 * 24 * 3600) * 100;
        },
        hobbs() {
            return this.assignment.next_due_hobbs - this.assignment.actual_hobbs;
        },
        componentClass() {
            return {
                'bar status-bar unscheduled-flight': true,
                'selected': this.selected,
                'hobbs-green': this.hobbs < 15 && this.hobbs >= 8,
                'hobbs-yellow': this.hobbs < 8 && this.hobbs >= 0,
                'hobbs-red': this.hobbs < 0,
                'drag-clone': this.dragging,
                'resizing': this.resizing,
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
            if (this.barWidth) {
                style.width = this.barWidth + 'px';
                style.transform = this.transform;
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
        }
    },
    mounted() {
        interact(this.$el).resizable({
            edges: { left: true, right: true }
        })
        .on('resizestart', (event) => {
            this.resizing = true;
            this.orgWidth = $(this.$el).width();
        })
        .on('resizemove', (event) => {
            const $bar = $(this.$el);
            const $row = $bar.closest('.row-line');
            const unitWidth = $row.width() / (14 * 24 * 3600) * this.unit;
            const resizeUnit = parseFloat(unitWidth * 300 / this.unit);  // Resize unit will be per 5 mins

            var w = Math.round(parseFloat(event.rect.width) / resizeUnit) * resizeUnit;
            var dw = w - this.orgWidth;
            var tx = event.deltaRect.left != 0 ? this.orgWidth - w : 0;
            var pos = event.deltaRect.left != 0 ? 'start' : 'end';

            this.barWidth = w;
            this.transform = `translateX(${tx}px)`;
            this.deltaWidth = dw;
            this.pos = pos;
        })
        .on('resizeend', (event) => {
            this.resizing = false;

            const $bar = $(this.$el);
            const $row = $bar.closest('.row-line');
            const unitWidth = $row.width() / (14 * 24 * 3600) * this.unit;
            var dt = parseFloat(this.deltaWidth) / unitWidth * this.unit;

            this.$emit('resized', this.assignment.id, this.pos, dt, this);
        });

        this.$on('cancel-resize', this.handleCancelResize);
    },
    watch: {
        'assignment.start_time': function() {
            this.barWidth = 0;
            this.transform = '';
        },
        'assignment.end_time': function() {
            this.barWidth = 0;
            this.transform = '';
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
        handleCancelResize() {
            this.barWidth = 0;
            this.transform = '';
        },
    }
}
</script>
