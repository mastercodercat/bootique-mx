<template>
    <form class="form-horizontal">
        <input type="hidden" class="action-after-save" name="action_after_save" v-model="actionAfterSave"/>
        <input type="hidden" name="tail_id" :value="tailId" />
        <input type="hidden" name="type" :value="type" />
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
            <button class="btn btn-default save-and-add-another" type="button" @click="saveAndAddAnother">
                Save and add another
            </button>
            <button class="btn btn-default save-and-continue" type="button" @click="saveAndContinue">
                Save and continue editing
            </button>
            <button class="btn btn-primary save" type="button" @click="save">
                Save
            </button>
        </div>
    </form>
</template>

<script>
export default {
    name: 'HobbsForm',
    props: ['type', 'tail-id', 'writable', 'load-hobbs-api-base', 'save-hobbs-api', 'url-to-redirect-after-save'],
    data() {
        return {
            actionAfterSave: 'save',
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
        roundTo2(n) {
            return +(Math.round(n + 'e+2') + 'e-2');
        },
        setValues(data) {
            this.$refs.hobbsId.value = '';
            this.$refs.hobbsDate.value = this.to2Digits(data.date.getMonth() + 1) + '/' +
                this.to2Digits(data.date.getDate()) + '/' + 
                data.date.getFullYear();
            this.$refs.hobbsTime.value = this.to2Digits(data.date.getHours()) + ':' + this.to2Digits(data.date.getMinutes());
            this.$refs.hobbsValue.value = this.roundTo2(data.projected);
        },
        loadHobbs(hobbsId) {
            var apiUrl = this.loadHobbsApiBase.replace('0', hobbsId);

            this.$http.get(apiUrl)
            .then((response) => {
                const { success } = response.data;
                if (!success) {
                    return;
                }
                var hobbsArray = JSON.parse(response.data.hobbs);
                if (!hobbsArray.length) {
                    return;
                }
                var hobbs = hobbsArray[0];
                var hobbsDate = new Date(hobbs.fields.hobbs_time);
                this.$refs.hobbsId.value = hobbs.pk;
                this.$refs.hobbsDate.value = this.to2Digits(hobbsDate.getMonth() + 1) + '/' +
                    this.to2Digits(hobbsDate.getDate()) + '/' + 
                    hobbsDate.getFullYear();
                this.$refs.hobbsTime.value = this.to2Digits(hobbsDate.getHours()) + ':' +
                    this.to2Digits(hobbsDate.getMinutes());
                this.$refs.hobbsValue.value = hobbs.fields.hobbs;
            });
        },
        saveAndAddAnother() {
            this.submitForm()
            .then((response) => {
                const { success } = response.data;
                if (success) {
                    this.$refs.hobbsId.value = '';
                    this.$refs.hobbsDate.value = '';
                    this.$refs.hobbsTime.value = '';
                    this.$refs.hobbsValue.value = '';
                }
            })
        },
        saveAndContinue() {
            this.submitForm()
            .then((response) => {
                const { success, hobbs_id } = response.data;
                if (success) {
                    this.$refs.hobbsId.value = hobbs_id;
                }
            })
        },
        save() {
            this.submitForm()
            .then((response) => {
                const { success } = response.data;
                if (success) {
                    window.location.href = this.urlToRedirectAfterSave;
                }
            })
        },
        submitForm() {
            var value = this.$refs.hobbsValue.value;
            var date = this.$refs.hobbsDate.value;
            var time = this.$refs.hobbsTime.value;
            if (!value || !date || !time) {
                alert('Please enter all fields in the form.');
            }

            var datetime = new Date(date);
            var timeparts = time.split(':');
            datetime.setHours(parseInt(timeparts[0]));
            datetime.setMinutes(parseInt(timeparts[1]));

            var data = {
                id: this.$refs.hobbsId.value,
                tail_id: this.tailId,
                type: this.type,
                hobbs: value,
                datetime: datetime.toISOString(),
            };

            return this.$http.post(this.saveHobbsApi, data)
            .then((response) => {
                const { success } = response.data;
                if (success) {
                    this.$emit('refresh-coming-due-list')
                }
                return response;
            });
        }
    }
}
</script>
