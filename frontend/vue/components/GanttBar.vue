<template>
    <div :class="{ 'gantt-bar': true, 'dragging': dragging }">
        <template v-if="data.status == 2">
            <gantt-maintenance-bar
                :assignment="data"
                :start-date="startDate"
                :timezone="timezone"
                :unit="unit"
                :selected="selected"
                :dragging="dragging"
                :drag-offset="internalDragOffset"
                @resized="handleResizeBar">
            </gantt-maintenance-bar>
        </template>
        <template v-else-if="data.status == 3">
            <gantt-unscheduled-flight-bar
                :assignment="data"
                :start-date="startDate"
                :timezone="timezone"
                :unit="unit"
                :selected="selected"
                :dragging="dragging"
                :drag-offset="internalDragOffset"
                @resized="handleResizeBar">
            </gantt-unscheduled-flight-bar>
        </template>
        <template v-else>
            <gantt-flight-bar
                :flight="data"
                :start-date="startDate"
                :timezone="timezone"
                :selected="selected"
                :assigned="assigned"
                :dragging="dragging"
                :drag-offset="internalDragOffset">
            </gantt-flight-bar>
        </template>
    </div>
</template>

<script>
import GanttFlightBar from '@frontend_components/GanttFlightBar.vue';
import GanttMaintenanceBar from '@frontend_components/GanttMaintenanceBar.vue';
import GanttUnscheduledFlightBar from '@frontend_components/GanttUnscheduledFlightBar.vue';

export default {
    name: 'GanttBar',
    props: ['data', 'start-date', 'timezone', 'unit', 'selected', 'assigned', 'dragging', 'drag-offset'],
    components: {
        'gantt-flight-bar': GanttFlightBar,
        'gantt-maintenance-bar': GanttMaintenanceBar,
        'gantt-unscheduled-flight-bar': GanttUnscheduledFlightBar,
    },
    data() {
        return {
            internalDragOffset: this.dragOffset,
        };
    },
    mounted() {
        this.$on('drag-offset-update', (offset) => {
            this.internalDragOffset = offset;
        });
    },
    methods: {
        handleResizeBar(assignment_id, position, diff_seconds) {
            this.$emit('resized', assignment_id, position, diff_seconds);
        },
    },
}
</script>
