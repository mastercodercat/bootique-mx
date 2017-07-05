<template>
    <div :class="{ 'drop-to-remove-area': true, 'dragging-over': draggingOver }">
        <i class="fa fa-trash-o"></i> Drag and drop here to remove assignment
    </div>
</template>

<script>
import interact from 'interactjs';

export default {
    name: 'GanttRemoveDropzone',
    props: ['acceptable-selector', 'editing'],
    data() {
        return {
            draggingOver: false,
        };
    },
    mounted() {
        interact(this.$el).dropzone({
            accept: this.acceptableSelector,
            ondragenter: (event) => {
                if (!this.editing) {
                    return false;
                }

                this.draggingOver = true;
            },
            ondragleave: (event) => {
                if (!this.editing) {
                    return false;
                }

                this.draggingOver = false;
            },
            ondrop: (event) => {
                if (!this.editing) {
                    return false;
                }

                this.draggingOver = false;
                this.$emit('drop-on', event);    // didn't use 'drop' as event message because it is HTML5 drag and drop event
            },
        });
    }
}
</script>
