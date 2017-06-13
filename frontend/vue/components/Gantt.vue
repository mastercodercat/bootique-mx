<template>
    <div>
        <div :class="{ 'gantt': true, 'loading': true, 'small-cells': days > 1, 'no-flight-number': days > 3 }" ref="gantt">
            <div class="m-b-md" v-if="writable">
                <label>Revision:</label>
                <div class="revision-controls">
                    <select id="revisions" class="form-control" style="max-width: 350px;">
                        <option value="0" selected>(New Draft)</option>
                        <option v-for="revision in revisions" :value="revision.id">
                            {{ revision.published_datetime }}
                        </option>
                    </select>
                    <button id="delete-revision" class="btn btn-danger">Delete This Version</button>
                    <button id="clear-revision" class="btn btn-default">Clear Changes</button>
                    <button id="publish-revision" class="btn btn-primary">Publish Current Revision</button>
                </div>
            </div>
            <label>Date/Time controls:</label>
            <div class="clearfix m-b-md"><!-- Top controls -->
                <div class="unit-control btn-group">
                    <a :class="{ 'btn btn-white': true, 'active': mode == 1 }"
                        :href="ganttUrl + '?mode=1&start=' + startTmstmp">3 Hours</a>
                    <a :class="{ 'btn btn-white': true, 'active': mode == 2 }"
                        :href="ganttUrl + '?mode=1&start=' + startTmstmp">6 Hours</a>
                    <a :class="{ 'btn btn-white': true, 'active': mode == 3 }"
                        :href="ganttUrl + '?mode=1&start=' + startTmstmp">12 Hours</a>
                    <a :class="{ 'btn btn-white': true, 'active': mode == 4 }"
                        :href="ganttUrl + '?mode=1&start=' + startTmstmp">24 Hours</a>
                    <a :class="{ 'btn btn-white': true, 'active': mode == 5 }"
                        :href="ganttUrl + '?mode=1&start=' + startTmstmp">3 Days</a>
                    <a :class="{ 'btn btn-white': true, 'active': mode == 6 }"
                        :href="ganttUrl + '?mode=1&start=' + startTmstmp">7 Days</a>
                </div>
                <div class="page-control">
                    <a href="javascript:;" id="btn-prev-time-window" class="btn btn-white"
                        :data-prev-period-href="`${ganttUrl}?mode=${mode}&start=${prevStartTmstmp}&window_at_end=1`">
                        <i class="fa fa-chevron-left"></i>
                    </a>
                    <a href="javascript:;" id="btn-next-time-window" class="btn btn-white"
                        :data-prev-period-href="`${ganttUrl}?mode=${mode}&start=${nextStartTmstmp}`">
                        <i class="fa fa-chevron-right"></i>
                    </a>
                </div>
                <div class="current-datetime-button-container">
                    <a href="javascript:;" id="btn-now" class="btn btn-primary">
                        <i class="fa fa-clock-o"></i>
                    </a>
                </div>
                <div class="date-range-control date-range-picker-group">
                    <div class="component-wrapper">
                        <div class="input-group date">
                            <span class="input-group-addon"><i class="fa fa-calendar"></i></span>
                            <input type="text" id="start_date" class="form-control">
                        </div>
                    </div>
                    <div class="component-wrapper">
                        <div class="input-group date">
                            <span class="input-group-addon"><i class="fa fa-calendar"></i></span>
                            <input type="text" id="end_date" class="form-control">
                        </div>
                    </div>
                    <div class="component-wrapper">
                        <form id="date-form" :action="ganttUrl" method="GET">
                            <input type="hidden" name="mode" :value="mode" />
                            <input type="hidden" id="startTmstmp" name="start" />
                            <input type="hidden" id="endTmstmp" name="end" />
                            <input type="submit" class="btn btn-primary" value="Search" />
                        </form>
                    </div>
                </div>
                <div class="timezone-control">
                    <select id="gantt-timezone" class="form-control" v-model="timezone">
                        <option value="0" selected>UTC</option>
                        <option value="-4">EDT</option>
                        <option value="-5">EST</option>
                        <option value="-5">CDT</option>
                        <option value="-6">CST</option>
                        <option value="-6">MDT</option>
                        <option value="-7">MST</option>
                        <option value="-7">PDT</option>
                        <option value="-8">PST</option>
                    </select>
                </div>
            </div>
            <!-- Status bar sources, remove area -->
            <div class="status-bars disabled clearfix" v-if="writable">
                <div class="clearfix">
                    <label>Drag and drop: </label>
                </div>
                <div class="bar-container">
                    <div class="bar status-bar maintenance status-prototype" draggable="true" data-status="2">
                        <span>Maintenance</span>
                        <div class="info bar-popover">
                            <div class="field">Status: Maintenance</div>
                            <div class="field">Sched. Start Time: <span class="start"></span></div>
                            <div class="field">Sched. End Time: <span class="end"></span></div>
                        </div>
                    </div>
                </div>
                <div class="bar-container">
                    <div class="bar status-bar unscheduled-flight status-prototype" draggable="true" data-status="3">
                        <span>Unscheduled Flight</span>
                        <div class="bar-popover">
                            <div class="field">Unscheduled Flight</div>
                            <div class="field">Origin: <span class="org"></span></div>
                            <div class="field">Destination: <span class="dest"></span></div>
                            <div class="field">Sched. Depature Time: <span class="departure"></span></div>
                            <div class="field">Sched. Arrival Time: <span class="arrival"></span></div>
                            <div class="assignment-only">
                                <hr />
                                <div class="field">Projected Hobbs: <span class="projected-hobbs"></span></div>
                                <div class="field">Next Due Hobbs: <span class="next-due-hobbs"></span></div>
                                <div class="field field-hobbs-left">Hobbs Left: <span class="hobbs-left"></span></div>
                            </div>
                        </div>
                    </div>
                </div>
                <div class="drop-to-remove-area" id="drop-to-remove-area">
                    <i class="fa fa-trash-o"></i> Drag and drop here to remove assignment
                </div>
            </div>

            <div class="cover-wrapper">
                <div class="gantt-labels">
                    <div class="label-cell">
                        <a :href="addTailUrl" class="btn btn-primary btn-circle-xs" type="button" v-if="writable">
                            <i class="fa fa-plus"></i>
                        </a>
                        Tails
                    </div>
                    <div class="axis-cell tail" v-for="tail in tails">
                        <a class="coming-due-page-link" href="#" :data-tail-id="tail.id">{{ tail.number }}</a>
                    </div>
                    <div class="label-cell">
                        <a :href="addLineUrl" class="btn btn-primary btn-circle-xs" type="button" v-if="writable">
                            <i class="fa fa-plus"></i>
                        </a>
                        Lines
                    </div>
                    <div class="axis-cell line" v-for="line in lines">
                        <a :href="editLineUrl.replace(0, line.id)">{{ line.name }}</a>
                    </div>
                </div>
                <div :class="{ 'cover': true, 'loading': loading }">
                    <div class="cover-inner" ref="scrollWrapper" :style="{ width: ganttWidth + 'px' }">
                        <!-- Tails table -->
                        <div class="table-wrapper">
                            <div class="now-indicator hidden"></div>
                            <div id="flight-assignment-table" class="gantt-table m-b-none">
                                <div class="head">
                                    <div class="row-line units big-units">
                                        <div class="unit border-right" v-for="n in bigUnits">
                                            {{ bigUnitText(n - 1) }}
                                        </div>
                                    </div>
                                    <div class="row-line units small-units">
                                        <div :class="{ 'unit': true, 'border-right': days > 1 && n % hours == 0 }" v-for="n in smallUnits">
                                            {{ smallUnitText(n - 1) }}
                                        </div>
                                    </div>
                                </div>
                                <gantt-drag-select item-selector=".bar" v-model="selectedAssignmentIds">
                                    <div class="row-line" :data-tail-number="tail.number" v-for="tail in tails">
                                        <gantt-bar
                                            :key="assignment.id"
                                            :data="assignment"
                                            :start-date="startDate"
                                            :timezone="timezone"
                                            :selected="!!selectedAssignmentIds[assignment.id]"
                                            v-for="assignment in getTailAssignments(tail)">
                                        </gantt-bar>
                                    </div>
                                </gantt-drag-select>
                                <div id="reserves" class="hidden"></div>
                            </div>
                        </div>
                        <!-- Lines table -->
                        <div class="table-wrapper">
                            <div class="now-indicator hidden"></div>
                            <div class="selection-area-indicator"></div>
                            <div id="flight-template-table" class="gantt-table m-b-none">
                                <div class="head">
                                    <div class="row-line units big-units">
                                        <div class="unit border-right" v-for="n in bigUnits">
                                            {{ bigUnitText(n - 1) }}
                                        </div>
                                    </div>
                                    <div class="row-line units small-units">
                                        <div :class="{ 'unit': true, 'border-right': days > 1 && n % hours == 0 }" v-for="n in smallUnits">
                                            {{ smallUnitText(n - 1) }}
                                        </div>
                                    </div>
                                </div>
                                <gantt-drag-select item-selector=".bar" v-model="selectedTemplateIds">
                                    <div class="row-line" :data-line="line.id" v-for="line in lines">
                                        <gantt-bar
                                            :key="template.id"
                                            :data="template"
                                            :start-date="startDate"
                                            :timezone="timezone"
                                            :selected="!!selectedTemplateIds[template.id]"
                                            :assigned="isAssigned(template)"
                                            v-for="template in getLineTemplates(line)">
                                        </gantt-bar>
                                    </div>
                                </gantt-drag-select>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
        <!-- Unscheduled Flight modal -->
        <div class="modal inmodal fade" id="unscheduled-flight-modal" tabindex="-1" role="dialog" aria-hidden="true">
            <div class="modal-dialog modal-md">
                <div class="modal-content">
                    <div class="modal-header">
                        <button type="button" class="close" data-dismiss="modal"><span aria-hidden="true">&times;</span><span class="sr-only">Close</span></button>
                        <h5 class="modal-title">Create Unscheduled Flight</h5>
                    </div>
                    <div class="modal-body">
                        <form class="form-horizontal">
                            <div class="form-group">
                                <label class="col-lg-2 control-label">Origin</label>
                                <div class="col-lg-10">
                                    <input type="origin" class="form-control unscheduled-flight-origin" placeholder="Origin">
                                </div>
                            </div>
                            <div class="form-group">
                                <label class="col-lg-2 control-label">Destination</label>
                                <div class="col-lg-10">
                                    <input type="destination" class="form-control unscheduled-flight-destination" placeholder="Destination">
                                </div>
                            </div>
                        </form>
                    </div>
                    <div class="modal-footer">
                        <button type="button" class="btn btn-white" data-dismiss="modal">Cancel</button>
                        <button type="button" class="btn btn-primary btn-save-unscheduled-flight">Save</button>
                    </div>
                </div>
            </div>
        </div>
    </div>
</template>

<script>
import Utils from '@frontend/js/utils.js';
import Cookies from 'js-cookie';
import moment from 'moment-timezone';

import GanttBar from '@frontend_components/GanttBar.vue';
import GanttDragSelect from '@frontend_components/GanttDragSelect.vue';

export default {
    name: 'Gantt',
    props: [
        'lines', 'tails',
        'gantt-url', 'add-tail-url', 'add-line-url', 'edit-line-url', 'load-data-api-url',
        'assign-flight-api-url', 'assign-status-api-url', 'move-assignment-api-url', 'remove-assignment-api-url',
        'resize-assignment-api-url', 'publish-revision-api-url', 'clear-revision-api-url', 'delete-revision-api-url',
        'days', 'hours', 'unit', 'writable', 'mode',
        'start-tmstmp', 'prev-start-tmstmp', 'next-start-tmstmp', 'big-units', 'small-units'
    ],
    components: {
        'gantt-bar': GanttBar,
        'gantt-drag-select': GanttDragSelect,
    },
    data() {
        const timezoneOffset = Cookies.get('gantt-timezone-offset');

        var ganttContainer = document.getElementById('gantt-container');
        var timeWindowCount = this.days > 1 ? 14 / this.days : 14 * (24 / this.hours);
        var timeWindowWidth = ganttContainer.clientWidth - 90;
        var ganttWidth = 90 + timeWindowWidth * timeWindowCount;
        var scrollLeft = 0;
        if (this.windowAtEnd) {
            scrollLeft = (timeWindowCount - 1) * timeWindowWidth;
        }

        return {
            ganttLengthSeconds: 14 * 24 * 3600,
            revisions: [],
            templates: {},
            assignments: {},
            assignedFlightIds: {},
            revision: 0,
            loading: true,
            // values to use in templates
            ganttWidth,
            // 2-way bound models
            timezone: timezoneOffset ? timezoneOffset : 0,
            selectedAssignmentIds: {},
            selectedTemplateIds: {},
        }
    },
    computed: {
        startDate() {
            return new Date(this.startTmstmp * 1000);
        },
        endDate() {
            const endDate = new Date(this.startDate.getTime() - 1000);
            endDate.setDate(endDate.getDate() + 14);
            return endDate;
        }
    },
    mounted() {
        this.init();
    },
    methods: {
        init() {
            this.setScrollPosition();
            this.loadData();
        },
        setScrollPosition() {
            var timeWindowCount = this.days > 1 ? 14 / this.days : 14 * (24 / this.hours);
            var timeWindowWidth = this.$refs.gantt.clientWidth - 90;
            var scrollLeft = 0;
            if (this.windowAtEnd) {
                scrollLeft = (timeWindowCount - 1) * timeWindowWidth;
            }
            this.$refs.scrollWrapper.scrollLeft = scrollLeft;
        },
        formatDate(date, dateFormat = 'MM/DD/YYYY HH:mm:ss') {
            if (typeof date === 'string') {
                var _date = new Date(date);
            } else {
                var _date = new Date(date.getTime());
            }
            _date.setHours(parseInt(_date.getHours()) + parseInt(this.timezone));
            return moment(_date).tz('UTC').format(dateFormat);
        },
        bigUnitText(n) {
            const oneUnit = this.days > 1 ? 24 : this.hours;
            const date = new Date(this.startDate.getTime());
            date.setSeconds(date.getSeconds() + n * oneUnit * 3600);
            return this.formatDate(date, 'ddd MM/DD/YYYY');
        },
        smallUnitText(n) {
            const date = new Date(this.startDate.getTime());
            date.setSeconds(date.getSeconds() + n * this.unit);
            if (this.days > 1 || this.hours >= 12) {
                return this.formatDate(date, 'HH');
            } else {
                return this.formatDate(date, 'HH:mm');
            }
        },
        getLineTemplates(line) {
            return this.templates[line.id] ? this.templates[line.id] : {};
        },
        getTailAssignments(tail) {
            return this.assignments[tail.number] ? this.assignments[tail.number] : {};
        },
        isAssigned(flight) {
            return !!this.assignedFlightIds[flight.id];
        },
        loadData(assignmentsOnly = false) {
            this.loading = true;

            this.$http.get(this.loadDataApiUrl, {
                params: {
                    startdate: this.startDate.getTime() / 1000,
                    enddate: this.endDate.getTime() / 1000,
                    assignments_only: assignmentsOnly,
                    revision: this.revision,
                },
            })
            .then((response) => {
                const { data } = response;

                /*
                 NOTE: assignedFlightIds, assignments and templates properties are not initialized as reactive,
                 so consider this when updating later
                 */

                this.assignedFlightIds = {};
                this.assignments = {};
                data.assignments.forEach((assignment) => {
                    if (!(assignment.tail in this.assignments)) {
                        this.assignments[assignment.tail] = {};
                    }
                    this.assignments[assignment.tail][assignment.id] = assignment;
                    if (assignment.flight_id) {
                        this.assignedFlightIds[assignment.flight_id] = true;
                    }
                });

                if (!assignmentsOnly) {
                    this.templates = {};
                    data.templates.forEach((template) => {
                        if (!(template.line_id in this.templates)) {
                            this.templates[template.line_id] = {}
                        }
                        this.templates[template.line_id][template.id] = template;
                    });
                }

                this.loading = false;
            });
        },
    }
}
</script>

<style>
#gantt-timezone {
    display: inline-block;
}
</style>