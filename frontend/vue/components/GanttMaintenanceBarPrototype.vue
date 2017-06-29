<template>
    <div :class="{ 'bar status-bar maintenance status-prototype': true, 'drag-clone': dragged }" :style="componentStyle">
        <div class="text">
            <span>Maintenance</span>
        </div>
        <div class="info bar-popover">
            <div class="field">Status: Maintenance</div>
            <div class="field">Sched. Start Time: <span class="start"></span></div>
            <div class="field">Sched. End Time: <span class="end"></span></div>
        </div>
    </div>
</template>

<script>
export default {
    name: 'GanttMaintenanceBarPrototype',
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
