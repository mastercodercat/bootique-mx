<template>
    <div class="row-line">
        <div class="last-assignment" v-if="startingTailPosition && firstAssignmentFarEnough">
            {{ startingTailPosition }}
        </div>
        <gantt-bar
            :key="object.id"
            :data="object"
            :start-date="startDate"
            :timezone="timezone"
            :unit="unit"
            :selected="!!selectedIds[object.id]"
            :assigned="isAssigned(object)"
            :editing="editing"
            @resized="handleResizeBar"
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
            v-for="object in shadows"
            v-if="dragging">
        </gantt-bar-shadow>
    </div>
</template>

<script>
import interact from 'interactjs';

import GanttBar from '@frontend_components/GanttBar.vue';
import GanttBarShadow from '@frontend_components/GanttBarShadow.vue';

export default {
    name: 'GanttRow',
    props: ['row-object', 'start-date', 'timezone', 'objects', 'shadows', 'unit',
        'selected-ids', 'dragging', 'drag-offset', 'dragging-ids', 'assigned-ids',
        'starting-tail-position', 'editing'],
    components: {
        'gantt-bar': GanttBar,
        'gantt-bar-shadow': GanttBarShadow,
    },
    computed: {
        firstAssignmentFarEnough() {
            if (!this.objects.length) {
                return true;
            }
            let firstAssignment = this.objects[0];
            if (this.startDate >= new Date(firstAssignment.end_time)) {
                if (this.objects.length > 1) {
                    firstAssignment = this.objects[1];
                } else {
                    return true;
                }
            }
            const date = new Date(firstAssignment.start_time);
            date.setSeconds(date.getSeconds() - this.unit);
            return this.startDate <= date;
        },
    },
    mounted() {
        interact(this.$el).dropzone({
            accept: '.bar',
            ondragenter: (event) => {
                if (!this.editing) {
                    return false;
                }

                const vm = this.getVueInstanceFromBar(event.relatedTarget);
                this.$emit('drag-enter', this.rowObject, vm.data, vm.status);
            },
            ondragleave: (event) => {
                if (!this.editing) {
                    return false;
                }

                const vm = this.getVueInstanceFromBar(event.relatedTarget);
                this.$emit('drag-leave', this.rowObject, vm.data, vm.status);
            },
            ondrop: (event) => {
                if (!this.editing) {
                    return false;
                }

                const vm = this.getVueInstanceFromBar(event.relatedTarget);
                this.$emit('drop-on', this.rowObject, vm.data, vm.status, event, this.$el);
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
        handleResizeBar(assignment_id, position, diff_seconds, vm) {
            this.$emit('resized', assignment_id, position, diff_seconds, vm);
        },
    }
}
</script>
