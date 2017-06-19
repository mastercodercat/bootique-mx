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
        <gantt-bar-shadow
            :key="object.id"
            :data="object"
            :start-date="startDate"
            v-for="object in shadows">
        </gantt-bar-shadow>
    </div>
</template>

<script>
import interact from 'interactjs';

import GanttBar from '@frontend_components/GanttBar.vue';
import GanttBarShadow from '@frontend_components/GanttBarShadow.vue';

export default {
    name: 'GanttRow',
    props: ['row-object', 'start-date', 'timezone', 'objects', 'shadows',
        'selected-ids', 'dragging', 'drag-offset', 'dragging-ids', 'assigned-ids'],
    components: {
        'gantt-bar': GanttBar,
        'gantt-bar-shadow': GanttBarShadow,
    },
    mounted() {
        interact(this.$el).dropzone({
            accept: '.bar',
            ondragenter: (event) => {
                const vm = this.getVueInstanceFromBar(event.relatedTarget);
                this.$emit('drag-enter', this.rowObject, vm.data, vm.status);
            },
            ondragleave: (event) => {
                const vm = this.getVueInstanceFromBar(event.relatedTarget);
                this.$emit('drag-leave', this.rowObject, vm.data, vm.status);
            },
            ondrop: (event) => {
                const vm = this.getVueInstanceFromBar(event.relatedTarget);
                this.$emit('drop-on', this.rowObject, vm.data, vm.status);
            },
        });
    },
    methods: {
        isAssigned(flight) {
            return this.assignedIds && !!this.assignedIds[flight.id];
        },
        getVueInstanceFromBar(barElement) {
            const $ganttBar = $(barElement).closest('.gantt-bar');
            if ($ganttBar.length) {
                return $ganttBar[0].__vue__;
            } else {
                const $statusPrototype = $(barElement);
                return $statusPrototype[0].__vue__;
            }
        },
    }
}
</script>
