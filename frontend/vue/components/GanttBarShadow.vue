<template>
    <div class="shadow prototype" :style="componentStyle">
    </div>
</template>

<script>
export default {
    name: 'GanttBarShadow',
    props: ['data', 'start-date'],
    computed: {
        startTime() {
            return this.data.start_time ? new Date(this.data.start_time) : new Date(this.data.departure_datetime);
        },
        endTime() {
            return this.data.end_time ? new Date(this.data.end_time) : new Date(this.data.arrival_datetime);
        },
        width() {
            var duration = (this.endTime - this.startTime) / 1000;
            return duration / (14 * 24 * 3600) * 100;
        },
        left() {
            var start = (this.startTime - new Date(this.startDate)) / 1000;
            return start / (14 * 24 * 3600) * 100;
        },
        componentStyle() {
            return {
                left: this.left + '%',
                width: this.width + '%'
            };
        },
    }
}
</script>