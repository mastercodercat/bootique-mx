<template>
    <table class="table table-bordered">
        <thead>
            <tr>
                <th>PN & SN</th>
                <th>Unit</th>
                <th>Interval</th>
                <th>C/W</th>
                <th>TSX/Adj.</th>
                <th>Next Due</th>
                <th>Max. Limit</th>
                <th>Remaining</th>
                <th>Est.Due</th>
                <th>Time Accrued</th>
                <th style="width: 1%;"><i class="fa fa-paperclip"></i></th>
            </tr>
        </thead>
        <tbody>
            <template v-for="taskItem in taskItems">
                <tr>
                    <td colspan="10">
                        <strong class="uppercase">
                            {{ taskItem.pn }}/{{ taskItem.sn }}
                            {{ taskItem.name }}
                        </strong>
                        <div class="pull-right">Service ATA:{{ task.number }}</div>
                    </td>
                    <td>
                        <a href="#">
                            <i class="fa fa-paperclip"></i>
                        </a>
                    </td>
                </tr>
                <tr v-for="subItem in taskItem.inspectioncomponentsubitem_set">
                    <td></td>
                    <td>{{ subItem.type }}</td>
                    <td class="edit-cell">
                        <input type="text" :value="subItem.interval" />
                    </td>
                    <td class="edit-cell">
                        <input type="text" :value="subItem.CW" />
                    </td>
                    <td class="edit-cell">
                        <input type="text" :value="subItem.TSX_adj" />
                    </td>
                    <td></td>
                    <td class="edit-cell">
                        <input type="text" :value="subItem.max_limit" />
                    </td>
                    <td></td>
                    <td></td>
                    <td>1.7</td>
                    <td></td>
                </tr>
            </template>
        </tbody>
    </table>
</template>

<script>
export default {
    name: 'TaskTable',
    props: ['aircraftReg', 'inspectionTaskId', 'loadApiUrl', 'updateCellApiUrl'],
    data() {
        return {
            task: {},
            taskItems: [],
        }
    },
    mounted() {
        this.$http.get(this.loadApiUrl, {})
        .then((response) => {
            this.task = response.body.task;
            this.taskItems = response.body.components;
        });
    },
}
</script>

<style>
.edit-cell {
    padding: 0 !important;
}
.edit-cell input[type="text"] {
    display: block;
    width: 100%;
    padding: 8px;
    border: 0;
}
</style>