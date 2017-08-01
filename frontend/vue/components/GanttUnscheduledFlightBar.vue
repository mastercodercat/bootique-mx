<template>
    <div :class="componentClass" :style="componentStyle">
        <div class="text">
            <span>Unscheduled Flight</span>
        </div>
    </div>
</template>

<script>
import interact from 'interactjs';

export default {
    name: 'GanttUnscheduledFlightBar',
    props: [
        'flight', 'start-date', 'timezone', 'selected',
        'dragging', 'drag-offset', 'unit', 'editing', 'writable',
    ],
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
    mounted() {
        interact(this.$el).resizable({
            edges: { left: true, right: true }
        })
        .on('resizestart', (event) => {
            if (!this.editing) {
                return false;
            }

            this.resizing = true;
            this.orgWidth = $(this.$el).width();
        })
        .on('resizemove', (event) => {
            if (!this.editing) {
                return false;
            }

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
            if (!this.editing) {
                return false;
            }

            this.resizing = false;

            const $bar = $(this.$el);
            const $row = $bar.closest('.row-line');
            const unitWidth = $row.width() / (14 * 24 * 3600) * this.unit;
            var dt = parseFloat(this.deltaWidth) / unitWidth * this.unit;

            this.$emit('resized', this.flight.id, this.pos, dt, this);
        });

        this.$on('cancel-resize', this.handleCancelResize);
    },
    watch: {
        'flight.start_time': function() {
            this.barWidth = 0;
            this.transform = '';
        },
        'flight.end_time': function() {
            this.barWidth = 0;
            this.transform = '';
        },
    },
    methods: {
        handleCancelResize() {
            this.barWidth = 0;
            this.transform = '';
        },
    }
}
</script>
