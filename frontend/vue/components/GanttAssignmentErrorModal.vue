<template>
    <div class="modal inmodal fade">
        <div class="modal-dialog modal-lg">
            <div class="modal-content">
                <div class="modal-header">
                    <button type="button" class="close" data-dismiss="modal">
                        <span aria-hidden="true">&times;</span>
                        <span class="sr-only">Close</span>
                    </button>
                    <h5 class="modal-title">Assignment Errors</h5>
                </div>
                <div class="modal-body">
                    <div v-for="conflict in conflictData">
                        <span>{{ conflict.subject }}</span>:
                        <strong>{{ conflict.conflictType }}</strong>
                        <span>{{ conflict.object }}</span>
                    </div>
                </div>
                <div class="modal-footer">
                    <button type="button" class="btn btn-white" data-dismiss="modal">OK</button>
                </div>
            </div>
        </div>
    </div>
</template>

<script>
export default {
    name: 'GanttAssignmentErrorModal',
    props: ['conflict-data'],
    methods: {
        showModal() {
            $(this.$el).modal();
        },
        hideModal() {
            $(this.$el).modal('hide');
        },
    }
}
</script>
