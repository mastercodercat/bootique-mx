import Vue from 'vue';
import axios from 'axios';
import Cookies from 'js-cookie';

import TaskTable from '@frontend_components/TaskTable.vue';
import ComingDueListPage from '@frontend_components/ComingDueListPage.vue';


axios.interceptors.request.use((config) => {
    const csrfToken = Cookies.get('csrftoken');
    config.headers['X-CSRFToken'] = csrfToken;
    return config;
});

Vue.prototype.$http = axios;

window.initTaskTable = function(elemSelector, params) {
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

window.initComingDueListPage = function(elemSelector, params) {
    new Vue({
        el: elemSelector,
        template: `<ComingDueListPage
            tail-id="${params.tailId}"
            tail-number="${params.tailNumber}"
            revision="${params.revision}"
            coming-due-list-api="${params.comingDueListAPI}"
            delete-actual-hobbs-api="${params.deleteActualHobbsAPI}"
            url-to-redirect-after-save="${params.urlToRedirectAfterSave}"
            writable="${params.writable}" />`,
        components: { ComingDueListPage }
    });
}
