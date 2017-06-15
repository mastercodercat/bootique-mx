<template>
    <div class="row-line">
        <gantt-bar
            :key="object.id"
            :data="object"
            :start-date="startDate"
            :timezone="timezone"
            :selected="!!selectedIds[object.id]"
            :assigned="isAssigned(object)"
            v-for="object in objects">
        </gantt-bar>
        <gantt-bar
            :key="object.id"
            :data="object"
            :start-date="startDate"
            :timezone="timezone"
            :selected="!!selectedIds[object.id]"
            :dragging="true"
            :drag-offset="dragOffset"
            v-for="object in objects"
            v-if="dragging && draggingIds[object.id]">
        </gantt-bar>
    </div>
</template>

<script>
import GanttBar from '@frontend_components/GanttBar.vue';

export default {
    name: 'GanttRow',
    props: ['row-object', 'start-date', 'timezone', 'objects',
        'selected-ids', 'dragging', 'drag-offset', 'dragging-ids', 'assigned-ids'],
    components: {
        'gantt-bar': GanttBar,
    },
    methods: {
        isAssigned(flight) {
            return this.assignedIds && !!this.assignedIds[flight.id];
        },
    }
}
</script>
