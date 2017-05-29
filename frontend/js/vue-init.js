import Vue from 'vue';
import axios from 'axios';
import Cookies from 'js-cookie';

import TaskTable from '@frontend_components/TaskTable.vue';


window.initTaskTable = function(elemSelector, params) {
    axios.interceptors.request.use((config) => {
        const csrfToken = Cookies.get('csrftoken');
        config.headers['X-CSRFToken'] = csrfToken;
        return config;
    });

    Vue.prototype.$http = axios;

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
