<template>
    <div class="modal inmodal fade">
        <div class="modal-dialog modal-md">
            <div class="modal-content">
                <div class="modal-header">
                    <button type="button" class="close" data-dismiss="modal"><span aria-hidden="true">&times;</span><span class="sr-only">Close</span></button>
                    <h5 class="modal-title">Create Unscheduled Flight</h5>
                </div>
                <div class="modal-body">
                    <form class="form-horizontal" @submit.prevent="handleSubmit">
                        <div class="form-group">
                            <label class="col-lg-2 control-label">Origin</label>
                            <div class="col-lg-10">
                                <input type="origin" class="form-control unscheduled-flight-origin" placeholder="Origin" v-model="origin">
                            </div>
                        </div>
                        <div class="form-group">
                            <label class="col-lg-2 control-label">Destination</label>
                            <div class="col-lg-10">
                                <input type="destination" class="form-control unscheduled-flight-destination" placeholder="Destination" v-model="destination">
                            </div>
                        </div>
                    </form>
                </div>
                <div class="modal-footer">
                    <button type="button" class="btn btn-white" data-dismiss="modal">Cancel</button>
                    <button type="button" class="btn btn-primary btn-save-unscheduled-flight"
                        :disabled="disabledSubmit"
                        @click="handleSubmit">
                        Save
                    </button>
                </div>
            </div>
        </div>
    </div>
</template>

<script>
export default {
    name: 'GanttUnscheduledFlightModal',
    data() {
        return {
            origin: '',
            destination: '',
            disabledSubmit: false,
        };
    },
    methods: {
        showModal() {
            $(this.$el).modal();
        },
        hideModal() {
            $(this.$el).modal('hide');
        },
        disableSubmit() {
            this.disabledSubmit = true;
        },
        enableSubmit() {
            this.disabledSubmit = false;
        },
        handleSubmit() {
            if (!this.origin || !this.destination) {
                alert('Please enter origin and destination');
                return;
            }
            this.$emit('submit', this.origin, this.destination);
        },
    }
}
</script>
