<template>
    <div :class="{ 'drop-to-remove-area': true, 'dragging-over': draggingOver }">
        <i class="fa fa-trash-o"></i> Drag and drop here to remove assignment
    </div>
</template>

<script>
import interact from 'interactjs';

export default {
    name: 'GanttRemoveDropzone',
    props: ['acceptable-selector'],
    data() {
        return {
            draggingOver: false,
        };
    },
    mounted() {
        interact('.drop-to-remove-area').dropzone({
            accept: this.acceptableSelector,
            ondragenter: (event) => {
                this.draggingOver = true;
            },
            ondragleave: (event) => {
                this.draggingOver = false;
            },
            ondrop: (event) => {
                this.draggingOver = false;
                this.$emit('drop-on', event);    // didn't use 'drop' as event message because it is HTML5 drag and drop event
            },
        });
    }
}
</script>
