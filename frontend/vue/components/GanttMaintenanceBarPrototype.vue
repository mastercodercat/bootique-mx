<template>
    <div :class="{ 'bar status-bar maintenance status-prototype': true, 'drag-clone': dragged }" :style="componentStyle">
        <div class="text">
            <span>Maintenance</span>
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
