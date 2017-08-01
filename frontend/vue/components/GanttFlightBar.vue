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
    </div>
</template>

<script>
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
}
</script>
