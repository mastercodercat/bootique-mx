<template>
    <div :class="componentClass" :style="componentStyle">
        <div class="text">
            <span>Maintenance</span>
        </div>
    </div>
</template>

<script>
import interact from 'interactjs';

export default {
    name: 'GanttMaintenanceBar',
    props: ['assignment', 'start-date', 'timezone', 'selected', 'dragging', 'drag-offset', 'unit', 'editing'],
    data() {
        return {
            resizing: false,
            orgWidth: 0,
            barWidth: 0,
            transform: '',
            deltaWidth: 0,
            pos: 0,
        }
    },
    computed: {
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
        handleCancelResize() {
            this.barWidth = 0;
            this.transform = '';
        },
    }
}
</script>
