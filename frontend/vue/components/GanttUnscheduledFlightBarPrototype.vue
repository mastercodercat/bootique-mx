<template>
    <div :class="{ 'bar status-bar unscheduled-flight status-prototype': true, 'drag-clone': dragged }" :style="componentStyle">
        <div class="text">
            <span>Unscheduled Flight</span>
        </div>
    </div>
</template>

<script>
export default {
    name: 'GanttUnscheduledFlightBarPrototype',
    props: ['status', 'dragged', 'drag-offset'],
    computed: {
        componentStyle() {
            if (this.dragOffset) {
                return {
                    'transform': `translate(${this.dragOffset.x}px, ${this.dragOffset.y}px)`,
                };
            } else {
                return {};
            }
        },
    },
}
</script>
