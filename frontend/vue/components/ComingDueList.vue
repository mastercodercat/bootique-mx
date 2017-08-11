<template>
    <div>
        <div class="row">
            <div class="col-sm-8 m-b">
                <div class="input-group date anchor-date">
                    <span class="input-group-addon"><i class="fa fa-calendar"></i></span>
                    <input type="text" ref="anchorDateInput" class="form-control" />
                </div>
                <button class="btn btn-primary btn-change-anchor-date" @click="handleChangeAnchorDate">Show Hobbs</button>
            </div>
        </div>
        <table id="coming-due-list" style="width: 100%;">
            <thead>
                <th><strong>Date</strong></th>
                <th><strong>Flight</strong></th>
                <th><strong>Hobbs<br>EOD</strong></th>
                <th><strong>Next Due<br>Hobbs</strong></th>
                <th><strong>Hobbs<br>Left</strong></th>
                <th v-if="writable"></th>
            </thead>
            <tbody>
                <tr v-for="hobbs in hobbsList">
                    <td>{{ formatHobbsDate(hobbs.day) }}</td>
                    <td>{{ hobbs.flight }}</td>
                    <td>{{ roundTo2(hobbs.projected) }}</td>
                    <td>{{ roundTo2(hobbs.next_due) }}</td>
                    <td>{{ roundTo2(hobbs.next_due - hobbs.projected) }}</td>
                    <td v-if="writable && hobbs.flight" style="padding-bottom: 3px;">
                        <button class="btn btn-primary btn-xs btn-edit-hobbs" @click="handleEditHobbs(hobbs)">
                            <i class="fa fa-fw fa-edit"></i>
                        </button>
                        <button class="btn-delete-flight btn btn-danger btn-xs btn-delete-hobbs">
                            <i class="fa fa-fw fa-trash"></i>
                        </button>
                    </td>
                </tr>
            </tbody>
        </table>
    </div>
</template>

<script>
import Vue from 'vue';

export default {
    name: 'ComingDueList',
    props: ['tail-id', 'revision', 'writable', 'coming-due-list-api'],
    data() {
        return {
            hobbsList: [],
            anchorDate: new Date(),
            anchorDateInput: '',
        }
    },
    mounted() {
        this.$on('refresh-coming-due-list', this.refresh);
        this.refresh();
    },
    methods: {
        roundTo2(n) {
            return +(Math.round(n + 'e+2') + 'e-2');
        },
        formatHobbsDate(dateString) {
            if (!dateString) {
                return '';
            }
            var date = new Date(dateString);
            var dateString = '';
            var weekdays = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday'];
            dateString += (date.getMonth() + 1) + '/'
            dateString += date.getDate() + '/';
            dateString += date.getFullYear() + ' ';
            dateString += weekdays[date.getDay()];
            return dateString;
        },
        firstWeekDay() {
            var date = new Date(this.anchorDate.getTime());
            date.setDate(date.getDate() - date.getDay());
            return date;
        },
        refresh() {
            this.$http.post(this.comingDueListApi, {
                tail_id: this.tailId,
                // start: this.firstWeekDay().toISOString(),
                start: this.anchorDate.toISOString(),
                days: 1,
                revision: this.revision,
            })
            .then((response) => {
                const { success, hobbs_list } = response.data;
                if (success) {
                    this.hobbsList = hobbs_list;
                }
            });
        },
        handleChangeAnchorDate() {
            Vue.nextTick(() => {
                this.anchorDate = new Date(this.$refs.anchorDateInput.value);
                this.refresh();
            });
        },
        handleEditHobbs(hobbs) {
            this.$emit('load-actual-hobbs', {
                date: new Date(hobbs.start_time_tmstmp * 1000),
                projected: hobbs.projected,
            });
            this.$emit('load-next-due-hobbs', hobbs.next_due_hobbs_id);
        }
    }
}
</script>

<style>
.anchor-date {
    float: left;
    width: calc(100% - 130px);
    max-width: 300px;
    margin-right: 10px;
}
.btn-change-anchor-date {
    float: left;
}
</style>