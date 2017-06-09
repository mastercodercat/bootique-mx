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
            <template v-for="taskComponent in taskComponents">
                <tr>
                    <td colspan="10">
                        <strong class="uppercase">
                            {{ taskComponent.pn }}/{{ taskComponent.sn }}
                            {{ taskComponent.name }}
                        </strong>
                        <div class="pull-right">Service ATA:{{ task.number }}</div>
                    </td>
                    <td>
                        <a href="#">
                            <i class="fa fa-paperclip"></i>
                        </a>
                    </td>
                </tr>
                <tr class="edit-row" v-for="subItem in taskComponent.sub_items">
                    <td></td>
                    <td>{{ subItem.type }}</td>
                    <td class="edit-cell">
                        <input type="text" v-model="subItem.interval" @change="changeValue(taskComponent, subItem, 'interval')" />
                    </td>
                    <td class="edit-cell">
                        <input type="text" v-model="subItem.CW" @change="changeValue(taskComponent, subItem, 'CW')" />
                    </td>
                    <td class="edit-cell">
                        <input type="text" v-model="subItem.TSX_adj" @change="changeValue(taskComponent, subItem, 'TSX_adj')" />
                    </td>
                    <td></td>
                    <td></td>
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
            taskComponents: [],
        }
    },
    mounted() {
        this.$http.get(this.loadApiUrl, {})
        .then((response) => {
            this.task = response.data.task;
            this.taskComponents = response.data.components;
        });
    },
    methods: {
        changeValue(taskComponent, subItem, field) {
            const value = subItem[field];

            this.$http.post(this.updateCellApiUrl, {
                component_id: taskComponent.id,
                sub_item_id: subItem.id,
                field,
                value: subItem[field],
            })
            .then((response) => {
                const { data } = response;
                if (!data.success) {
                    alert(data.message);
                }
            });
        }
    }
}
</script>

<style>
.edit-row td {
    background-color: #fbfbfc;
}
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