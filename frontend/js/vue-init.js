import Vue from 'vue';
import VueResource from 'vue-resource';
import TaskTable from '@frontend_components/TaskTable.vue';

window.initTaskTable = function(elemSelector, params) {
    Vue.use(VueResource);

    new Vue({
        el: elemSelector,
        template: `<TaskTable
            aircraft-reg="${params.aircraftReg}"
            inspectionTaskId=${params.inspectionTaskId}
            load-api-url="${params.loadApiUrl}"
            update-cell-api-url="${params.updateCellApiUrl}" />`,
        components: { TaskTable }
    });
}
