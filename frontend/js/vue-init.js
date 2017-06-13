import Vue from 'vue';
import axios from 'axios';
import Cookies from 'js-cookie';

import TaskTable from '@frontend_components/TaskTable.vue';
import ComingDueListPage from '@frontend_components/ComingDueListPage.vue';
import Gantt from '@frontend_components/Gantt.vue';


axios.interceptors.request.use((config) => {
    const csrfToken = Cookies.get('csrftoken');
    config.headers['X-CSRFToken'] = csrfToken;
    return config;
});

Vue.prototype.$http = axios;

function upperToHyphenLower(match, offset, string) {
    return (offset ? '-' : '') + match.toLowerCase();
}

function generateTemplate(component, params) {
    let template = `<${component} `;

    for (const field in params) {
        const prop = field.replace(/([A-Z]+)/g, upperToHyphenLower);
        const value = params[field];
        if (value.constructor === Array) {
            template += `:${prop}='${JSON.stringify(value)}' `;
        } else if (value.constructor === Number) {
            template += `:${prop}='${value}' `;
        } else {
            template += `${prop}='${value}' `;
        }
        
    }
    template += '/>';
    return template
}

window.initTaskTable = function(elemSelector, params) {
    new Vue({
        el: elemSelector,
        template: generateTemplate('TaskTable', params),
        components: { TaskTable }
    });
}

window.initComingDueListPage = function(elemSelector, params) {
    new Vue({
        el: elemSelector,
        template: generateTemplate('ComingDueListPage', params),
        components: { ComingDueListPage }
    });
}

window.initGantt = function(elemSelector, params) {
    new Vue({
        el: elemSelector,
        template: generateTemplate('Gantt', params),
        components: { Gantt }
    });
}
