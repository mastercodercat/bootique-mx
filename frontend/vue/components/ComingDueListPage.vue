<template>
    <div class="row">
        <div class="col-lg-6 col-md-12 col-sm-12 col-xs-12">
            <div class="ibox">
                <div class="ibox-title">
                    <h3>Actual Hobbs</h3>
                </div>
                <div class="ibox-content">
                    <hobbs-form
                        type="1"
                        :tail-id="tailId"
                        :writable="writable"
                        :save-hobbs-api="saveHobbsApi"
                        :url-to-redirect-after-save="urlToRedirectAfterSave"
                        @refresh-coming-due-list="refreshComingDueList"
                        ref="actualHobbsForm" />
                </div>
            </div>
            <div class="ibox">
                <div class="ibox-title">
                    <h3>Next Due Hobbs</h3>
                </div>
                <div class="ibox-content">
                    <hobbs-form
                        type="2"
                        :tail-id="tailId"
                        :writable="writable"
                        :load-hobbs-api-base="loadHobbsApiBase"
                        :save-hobbs-api="saveHobbsApi"
                        :url-to-redirect-after-save="urlToRedirectAfterSave"
                        @refresh-coming-due-list="refreshComingDueList"
                        ref="nextDueHobbsForm" />
                </div>
            </div>
        </div>
        <div class="col-lg-5 col-md-12 col-sm-12 col-xs-12">
            <div class="ibox">
                <div class="ibox-title">
                    <h3>Coming Due List for {{ tailNumber }}</h3>
                </div>
                <div class="ibox-content">
                    <coming-due-list
                        :tail-id="tailId"
                        :revision="revision"
                        :writable="writable"
                        :coming-due-list-api="comingDueListApi"
                        @load-actual-hobbs="loadActualHobbs"
                        @load-next-due-hobbs="loadNextDueHobbs"
                        ref="comingDueList" />
                </div>
            </div>
        </div>
    </div>
</template>

<script>
import ComingDueList from '@frontend_components/ComingDueList.vue';
import HobbsForm from '@frontend_components/HobbsForm.vue';

export default {
    name: 'ComingDueListPage',
    props: ['tail-id', 'tail-number', 'revision', 'coming-due-list-api', 'save-hobbs-api',
        'load-hobbs-api-base', 'url-to-redirect-after-save', 'writable'],
    components: {
        'coming-due-list': ComingDueList,
        'hobbs-form': HobbsForm,
    },
    data() {
        return {
        }
    },
    methods: {
        loadActualHobbs(data) {
            this.$refs.actualHobbsForm.$emit('set-values', data);
        },
        loadNextDueHobbs(hobbsId) {
            this.$refs.nextDueHobbsForm.$emit('load-hobbs', hobbsId);
        },
        refreshComingDueList() {
            this.$refs.comingDueList.$emit('refresh-coming-due-list');
        }
    }
}
</script>
