<template>
    <form class="form-horizontal">
        <input type="hidden" class="action-after-save" name="action_after_save" value="save" />
        <input type="hidden" name="tail_id" :value="tailId" />
        <input type="hidden" name="type" value="1" />
        <input type="hidden" class="hobbs-id" name="hobbs_id" ref="hobbsId" value="" />
        <div class="row">
            <div class="col-md-6 col-sm-12">
                <div class="form-group">
                    <label class="col-sm-3 control-label">Date</label>
                    <div class="col-sm-9">
                        <div class="input-group date">
                            <span class="input-group-addon"><i class="fa fa-calendar"></i></span>
                            <input type="text" class="form-control hobbs-date" name="date" ref="hobbsDate" />
                        </div>
                    </div>
                </div>
            </div>
            <div class="col-md-6 col-sm-12">
                <div class="form-group">
                    <label class="col-sm-3 control-label">Time</label>
                    <div class="col-sm-9">
                        <div class="input-group clockpicker" data-autoclose="true">
                            <input type="text" class="form-control hobbs-time" name="time" ref="hobbsTime" />
                            <span class="input-group-addon">
                                <span class="fa fa-clock-o"></span>
                            </span>
                        </div>
                    </div>
                </div>
            </div>
            <div class="col-md-6 col-sm-12">
                <div class="form-group">
                    <label class="col-sm-3 control-label">Hobbs</label>
                    <div class="col-sm-9">
                        <input type="text" class="form-control hobbs-value" name="value" ref="hobbsValue" />
                    </div>
                </div>
            </div>
        </div>
        <div class="text-right m-t-lg" v-if="writable">
            <button class="btn btn-default save-and-add-another" type="button">Save and add another</button>
            <button class="btn btn-default save-and-continue" type="button">Save and continue editing</button>
            <button class="btn btn-primary save" type="submit">Save</button>
        </div>
    </form>
</template>

<script>
export default {
    name: 'HobbsForm',
    props: [],
    data() {
        return {
            tailId: 1,
            writable: true,
        }
    },
    mounted() {
        this.$on('set-values', this.setValues);
        this.$on('load-hobbs', this.loadHobbs);
    },
    methods: {
        to2Digits(n) {
            return n < 10 ? '0' + n : '' + n
        },
        setValues(data) {
            this.$refs.hobbsId.value = '';
            this.$refs.hobbsDate.value = this.to2Digits(data.date.getMonth() + 1) + '/' +
                this.to2Digits(data.date.getDate()) + '/' + 
                data.date.getFullYear()
            this.$refs.hobbsTime.value = this.to2Digits(data.date.getHours()) + ':' + this.to2Digits(data.date.getMinutes())
            this.$refs.hobbsValue = data.projected;
        },
        loadHobbs(hobbsId) {
            console.log(hobbsId);
        }
    }
}
</script>
