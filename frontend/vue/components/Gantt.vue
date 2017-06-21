<template>
    <div>
        <div :class="{ 'gantt': true, 'loading': true, 'small-cells': days > 1, 'no-flight-number': days > 3 }" ref="gantt">
            <div class="m-b-md" v-if="writable">
                <label>Revision:</label>
                <div class="revision-controls">
                    <select class="form-control" style="max-width: 350px;" v-model="revision">
                        <option value="0" selected>(New Draft)</option>
                        <option v-for="revision in revisions" :value="revision.id">
                            {{ formatDate(revision.published) }}
                        </option>
                    </select>
                    <button id="delete-revision" class="btn btn-danger" @click="handleDeleteRevision">Delete This Version</button>
                    <button id="clear-revision" class="btn btn-default" @click="handleClearRevision">Clear Changes</button>
                    <button id="publish-revision" class="btn btn-primary" @click="handlePublishRevision">Publish Current Revision</button>
                </div>
            </div>
            <label>Date/Time controls:</label>
            <div class="clearfix m-b-md"><!-- Top controls -->
                <div class="unit-control btn-group">
                    <a :class="{ 'btn btn-white': true, 'active': mode == 1 }"
                        :href="ganttUrl + '?mode=1&start=' + startTmstmp">3 Hours</a>
                    <a :class="{ 'btn btn-white': true, 'active': mode == 2 }"
                        :href="ganttUrl + '?mode=2&start=' + startTmstmp">6 Hours</a>
                    <a :class="{ 'btn btn-white': true, 'active': mode == 3 }"
                        :href="ganttUrl + '?mode=3&start=' + startTmstmp">12 Hours</a>
                    <a :class="{ 'btn btn-white': true, 'active': mode == 4 }"
                        :href="ganttUrl + '?mode=4&start=' + startTmstmp">24 Hours</a>
                    <a :class="{ 'btn btn-white': true, 'active': mode == 5 }"
                        :href="ganttUrl + '?mode=5&start=' + startTmstmp">3 Days</a>
                    <a :class="{ 'btn btn-white': true, 'active': mode == 6 }"
                        :href="ganttUrl + '?mode=6&start=' + startTmstmp">7 Days</a>
                </div>
                <div class="page-control">
                    <a href="javascript:;" id="btn-prev-time-window" class="btn btn-white"
                        @click.prevent="handleClickPrevTimeWindow">
                        <i class="fa fa-chevron-left"></i>
                    </a>
                    <a href="javascript:;" id="btn-next-time-window" class="btn btn-white"
                        @click.prevent="handleClickNextTimeWindow">
                        <i class="fa fa-chevron-right"></i>
                    </a>
                </div>
                <div class="current-datetime-button-container">
                    <a href="javascript:;" id="btn-now" class="btn btn-primary"
                        @click.prevent="handleClickNow">
                        <i class="fa fa-clock-o"></i>
                    </a>
                </div>
                <div class="date-range-control date-range-picker-group">
                    <div class="component-wrapper">
                        <div class="input-group date">
                            <span class="input-group-addon"><i class="fa fa-calendar"></i></span>
                            <input type="text" id="start_date" class="form-control" ref="startDateInput">
                        </div>
                    </div>
                    <div class="component-wrapper">
                        <div class="input-group date">
                            <span class="input-group-addon"><i class="fa fa-calendar"></i></span>
                            <input type="text" id="end_date" class="form-control" ref="endDateInput">
                        </div>
                    </div>
                    <div class="component-wrapper">
                        <button
                            class="btn btn-primary"
                            @click="handleSubmitDateForm">
                            Search
                        </button>
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
            <div class="status-bars clearfix" v-if="writable">
                <div class="clearfix">
                    <label>Drag and drop: </label>
                </div>
                <div class="bar-container">
                    <gantt-maintenance-bar-prototype
                        :status="2">
                    </gantt-maintenance-bar-prototype>
                    <gantt-maintenance-bar-prototype
                        :status="2"
                        :dragged="true"
                        :drag-offset="dragOffset"
                        v-if="draggingStatusPrototype && draggingStatus == 2">
                    </gantt-maintenance-bar-prototype>
                </div>
                <div class="bar-container">
                    <gantt-unscheduled-flight-bar-prototype
                        :status="3">
                    </gantt-unscheduled-flight-bar-prototype>
                    <gantt-unscheduled-flight-bar-prototype
                        :status="3"
                        :dragged="true"
                        :drag-offset="dragOffset"
                        v-if="draggingStatusPrototype && draggingStatus == 3">
                    </gantt-unscheduled-flight-bar-prototype>
                </div>
                <gantt-remove-dropzone
                    acceptable-selector="#flight-assignment-table .bar"
                    @drop-on="handleDropOnRemoveZone">
                </gantt-remove-dropzone>
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
                        <a class="coming-due-page-link"
                            :href="'/routeplanning/tail/' + tail.id + '/revision/' + revision + '/comingdue/'">{{ tail.number }}</a>
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
                <div :class="{ 'cover': true, 'loading': loading }" ref="scrollWrapper">
                    <div class="cover-inner" :style="{ width: ganttWidth + 'px' }">
                        <!-- Tails table -->
                        <div class="table-wrapper">
                            <div :class="{ 'now-indicator': true, 'hidden': !currentTimeIndicatorVisible }"
                                :style="{ left: currentTimeIndicatorLeft + '%' }">
                            </div>
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
                                    <gantt-row
                                        :key="tail.id"
                                        :row-object="tail"
                                        :start-date="startDate"
                                        :timezone="timezone"
                                        :objects="getTailAssignments(tail)"
                                        :shadows="getTailShadows(tail)"
                                        :unit="unit"
                                        :selected-ids="selectedAssignmentIds"
                                        :dragging="dragging"
                                        :drag-offset="dragOffset"
                                        :dragging-ids="draggingAssignmentIds"
                                        @drag-enter="handleDragEnterAssignmentRow"
                                        @drag-leave="handleDragLeaveAssignmentRow"
                                        @drop-on="handleDropOnAssignmentRow"
                                        @resized="handleResizeBar"
                                        v-for="tail in tails">
                                    </gantt-row>
                                </gantt-drag-select>
                                <div id="reserves" class="hidden"></div>
                            </div>
                        </div>
                        <!-- Lines table -->
                        <div class="table-wrapper">
                            <div :class="{ 'now-indicator': true, 'hidden': !currentTimeIndicatorVisible }"
                                :style="{ left: currentTimeIndicatorLeft + '%' }">
                            </div>
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
                                    <gantt-row
                                        :key="line.id"
                                        :row-object="line"
                                        :start-date="startDate"
                                        :timezone="timezone"
                                        :objects="getLineTemplates(line)"
                                        :unit="unit"
                                        :selected-ids="selectedTemplateIds"
                                        :dragging="dragging"
                                        :drag-offset="dragOffset"
                                        :dragging-ids="draggingTemplateIds"
                                        :assigned-ids="assignedFlightIds"
                                        v-for="line in lines">
                                    </gantt-row>
                                </gantt-drag-select>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
        <!-- Unscheduled Flight modal -->
        <gantt-unscheduled-flight-modal
            ref="unscheduledFlightModal"
            @submit="createUnscheduledFlight"
            @cancel="cancelUnscheduledFlightCreate">
        </gantt-unscheduled-flight-modal>
    </div>
</template>

<script>
import interact from 'interactjs';
import Utils from '@frontend/js/utils.js';
import Cookies from 'js-cookie';
import moment from 'moment-timezone';

import GanttRow from '@frontend_components/GanttRow.vue';
import GanttDragSelect from '@frontend_components/GanttDragSelect.vue';
import GanttMaintenanceBarPrototype from '@frontend_components/GanttMaintenanceBarPrototype.vue';
import GanttUnscheduledFlightBarPrototype from '@frontend_components/GanttUnscheduledFlightBarPrototype.vue';
import GanttRemoveDropzone from '@frontend_components/GanttRemoveDropzone.vue';
import GanttUnscheduledFlightModal from '@frontend_components/GanttUnscheduledFlightModal.vue';

export default {
    name: 'Gantt',
    props: [
        'lines', 'tails', 'initial-revisions', 
        'gantt-url', 'add-tail-url', 'add-line-url', 'edit-line-url',
        'load-data-api-url', 'assign-flight-api-url', 'assign-status-api-url', 'move-assignment-api-url',
        'remove-assignment-api-url', 'resize-assignment-api-url', 'publish-revision-api-url',
        'clear-revision-api-url', 'delete-revision-api-url',
        'days', 'hours', 'unit', 'writable', 'mode',
        'start-tmstmp', 'prev-start-tmstmp', 'next-start-tmstmp', 'big-units', 'small-units',
        'window-at-end', 'start-param-exists', 'end-param-exists', 
    ],
    components: {
        'gantt-row': GanttRow,
        'gantt-drag-select': GanttDragSelect,
        'gantt-maintenance-bar-prototype': GanttMaintenanceBarPrototype,
        'gantt-unscheduled-flight-bar-prototype': GanttUnscheduledFlightBarPrototype,
        'gantt-remove-dropzone': GanttRemoveDropzone,
        'gantt-unscheduled-flight-modal': GanttUnscheduledFlightModal,
    },
    data() {
        const timezoneOffset = Cookies.get('gantt-timezone-offset');

        const ganttContainer = document.getElementById('gantt-container');
        const timeWindowCount = this.days > 1 ? 14 / this.days : 14 * (24 / this.hours);
        const timeWindowWidth = ganttContainer.clientWidth - 90;
        const ganttWidth = 90 + timeWindowWidth * timeWindowCount;
        let scrollLeft = 0;
        if (this.windowAtEnd) {
            scrollLeft = (timeWindowCount - 1) * timeWindowWidth;
        }

        const revisions = [];
        for (const index in this.initialRevisions) {
            const revision = this.initialRevisions[index];
            revisions.push({
                id: revision.id,
                published: new Date(revision.published_datetime),
            });
        }

        return {
            ganttLengthSeconds: 14 * 24 * 3600,
            revisions,
            templates: {},
            assignments: {},
            assignedFlightIds: {},
            loading: true,
            ganttWidth,
            draggingAssignmentIds: {},
            draggingTemplateIds: {},
            dragging: false,
            dragOffset: { x: 0, y: 0 },
            draggingStatusPrototype: false,
            draggingStatus: 0,
            dragoverRowShadows: {},
            unscheduledFlightCreateData: {},
            // 2-way bound models
            revision: 0,
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
        },
        currentTimeIndicatorVisible() {
            const now = new Date();
            return now >= this.startDate && now <= this.endDate;
        },
        currentTimeIndicatorLeft() {
            const now = new Date();
            return (now - this.startDate) / 1000 / this.ganttLengthSeconds * 100;
        },
    },
    mounted() {
        this.init();
    },
    methods: {
        init() {
            this.setScrollPosition();
            this.initDateForm();
            this.loadData();
            this.initInteractables();
        },
        setScrollPosition() {
            const timeWindowCount = this.days > 1 ? 14 / this.days : 14 * (24 / this.hours);
            const timeWindowWidth = this.$refs.gantt.clientWidth - 90;
            let scrollLeft = 0;
            if (this.windowAtEnd) {
                scrollLeft = (timeWindowCount - 1) * timeWindowWidth;
            }
            this.$refs.scrollWrapper.scrollLeft = scrollLeft;
        },
        initDateForm() {
            if (this.startParamExists) {
                this.$refs.startDateInput.value = Utils.formatTo2Digits(this.startDate.getMonth() + 1) + '/' + 
                    Utils.formatTo2Digits(this.startDate.getDate()) + '/' +
                    this.startDate.getFullYear();
            }
            if (this.endParamExists) {
                this.$refs.endDateInput.value = Utils.formatTo2Digits(this.endDate.getMonth() + 1) + '/' + 
                    Utils.formatTo2Digits(this.endDate.getDate()) + '/' + 
                    this.endDate.getFullYear();
            }
        },
        formatDate(date, dateFormat = 'MM/DD/YYYY HH:mm:ss', considerTimezone = true) {
            if (typeof date === 'string') {
                var _date = new Date(date);
            } else {
                var _date = new Date(date.getTime());
            }
            _date.setHours(parseInt(_date.getHours()) + (considerTimezone ? parseInt(this.timezone) : 0));
            return moment(_date).tz('UTC').format(dateFormat);
        },
        bigUnitText(n) {
            const oneUnit = this.days > 1 ? 24 : this.hours;
            const date = new Date(this.startDate.getTime());
            date.setSeconds(date.getSeconds() + n * oneUnit * 3600);
            return this.formatDate(date, 'ddd MM/DD/YYYY', false);
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
        alertErrorIfAny(response, singular) {
            if (singular) {
                if (response.duplication) {
                    alert('Timeframe overlapped with other assignments');
                } else if (response.physically_invalid) {
                    alert('Physically invalid assignment');
                }
            } else {
                var errorOccurred = false;
                var errors = "Some of assignments are not placed due to following errors:";
                if (response.duplication) {
                    errorOccurred = true;
                    errors += "\n- Overlapped timeframe";
                }
                if (response.physically_invalid) {
                    errorOccurred = true;
                    errors += "\n- Physically invalid assignment";
                }
                if (errorOccurred) {
                    alert(errors);
                }
            }
        },
        getLineTemplates(line) {
            return this.templates[line.id] ? this.templates[line.id] : {};
        },
        getTailAssignments(tail) {
            return this.assignments[tail.number] ? this.assignments[tail.number] : {};
        },
        getTailShadows(tail) {
            return this.dragoverRowShadows[tail.id] ? this.dragoverRowShadows[tail.id] : [];
        },
        loadData(assignmentsOnly = false) {
            if (!assignmentsOnly) {
                this.loading = true;
            }

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

                const assignedFlightIds = {};
                const assignments = {};
                data.assignments.forEach((assignment) => {
                    if (!(assignment.tail in assignments)) {
                        assignments[assignment.tail] = {};
                    }
                    assignments[assignment.tail][assignment.id] = assignment;
                    if (assignment.flight_id) {
                        assignedFlightIds[assignment.flight_id] = true;
                    }
                });

                this.assignedFlightIds = assignedFlightIds;
                this.assignments = assignments;

                if (!assignmentsOnly) {
                    const templates = {};
                    data.templates.forEach((template) => {
                        if (!(template.line_id in templates)) {
                            templates[template.line_id] = {};
                        }
                        templates[template.line_id][template.id] = template;
                    });
                    this.templates = templates;
                }

                this.loading = false;
            });
        },
        initInteractables() {
            // Template flights or assignments dragging
            interact('.gantt-bar .bar:not(.assigned)').draggable({
                autoScroll: true,
                onstart: (event) => {
                    const $bar = $(event.target);
                    const vm = $bar.closest('.gantt-bar')[0].__vue__;
                    const data = vm.data;

                    this.draggingTemplateIds = {};
                    this.draggingAssignmentIds = {};
                    if (data.status) {
                        if (this.selectedAssignmentIds[data.id]) {
                            this.draggingAssignmentIds = this.selectedAssignmentIds;
                        } else {
                            this.selectedAssignmentIds = {
                                [data.id]: true,
                            };
                            this.$set(this.draggingAssignmentIds, data.id, true);
                        }
                    } else {
                        if (this.selectedTemplateIds[data.id]) {
                            this.draggingTemplateIds = this.selectedTemplateIds;
                        } else {
                            this.selectedTemplateIds = {
                                [data.id]: true,
                            };
                            this.$set(this.draggingTemplateIds, data.id, true);
                        }
                    }

                    this.dragOffset.x = 0;
                    this.dragOffset.y = 0;
                    this.dragging = true;
                },
                onmove: (event) => {
                    const x = (this.dragOffset.x ? this.dragOffset.x : 0) + event.dx;
                    const y = (this.dragOffset.y ? this.dragOffset.y : 0) + event.dy;

                    this.dragOffset.x = x;
                    this.dragOffset.y = y;
                },
                onend: (event) => {
                    this.dragging = false;
                },
            })
            .actionChecker(function (pointer, event, action) {
                const pos = event.offsetX / $(event.target).closest('.bar').width();
                if (pos <= 0.15 || pos >= 0.85) {
                    action.name = 'resize';
                    action.edges = {};
                    if (pos <= 0.15) {
                        action.edges.left = true;
                    } else {
                        action.edges.right = true;
                    }
                }
                if (event.button !== 0) {
                    return null;
                }
                return action;
            })
            .on('click', (event) => {
                const $bar = $(event.target);
                const vm = $bar.closest('.gantt-bar')[0].__vue__;
                const data = vm.data;

                if (data.status) {
                    if (event.shiftKey) {
                        this.$set(this.selectedAssignmentIds, data.id, true);
                    } else if (event.altKey) {
                        this.$set(this.selectedAssignmentIds, data.id, false);
                    } else {
                        this.selectedAssignmentIds = {
                            [data.id]: true,
                        };
                    }
                } else {
                    if (event.shiftKey) {
                        this.$set(this.selectedTemplateIds, data.id, true);
                    } else if (event.altKey) {
                        this.$set(this.selectedTemplateIds, data.id, false);
                    } else {
                        this.selectedTemplateIds = {
                            [data.id]: true,
                        };
                    }
                }
            });

            // Status bar prototypes dragging
            interact('.status-prototype').draggable({
                autoScroll: true,
                onstart: (event) => {
                    const $bar = $(event.target);
                    const vm = $bar.closest('.bar.status-prototype')[0].__vue__;

                    this.dragOffset.x = 0;
                    this.dragOffset.y = 0;
                    this.draggingStatusPrototype = true;
                    this.draggingStatus = vm.status;
                },
                onmove: (event) => {
                    const x = (this.dragOffset.x ? this.dragOffset.x : 0) + event.dx;
                    const y = (this.dragOffset.y ? this.dragOffset.y : 0) + event.dy;

                    this.dragOffset.x = x;
                    this.dragOffset.y = y;
                },
                onend: (event) => {
                    this.draggingStatusPrototype = false;
                },
            })
            .actionChecker(function (pointer, event, action) {
                if (event.button !== 0) {
                    return null;
                }
                return action;
            });
        },
        handleClickPrevTimeWindow() {
            const offset = 0.01;

            const timeWindowWidth = this.$refs.gantt.clientWidth - 90;
            const timeWindowCount = this.days > 1 ? 14 / this.days : 14 * (24 / this.hours);
            let pos = this.$refs.scrollWrapper.scrollLeft / timeWindowWidth;
            if (pos <= offset) {
                window.location.href = `${this.ganttUrl}?mode=${this.mode}&start=${this.prevStartTmstmp}&window_at_end=1`;
            } else {
                if (Math.abs(pos - Math.round(pos)) <= offset) {
                    pos = Math.floor(pos) - 1;
                } else {
                    pos = Math.floor(pos);
                }
                this.$refs.scrollWrapper.scrollLeft = pos * timeWindowWidth;
            }
        },
        handleClickNextTimeWindow() {
            const offset = 0.01;

            const timeWindowWidth = this.$refs.gantt.clientWidth - 90;
            const timeWindowCount = this.days > 1 ? 14 / this.days : 14 * (24 / this.hours);
            let pos = this.$refs.scrollWrapper.scrollLeft / timeWindowWidth;
            if (Math.abs(timeWindowCount - 1 - pos) <= offset) {
                window.location.href = `${this.ganttUrl}?mode=${this.mode}&start=${this.nextStartTmstmp}`;
            } else {
                if (Math.abs(pos - Math.round(pos)) <= offset) {
                    pos = Math.ceil(pos) + 1;
                } else {
                    pos = Math.ceil(pos);
                }
                this.$refs.scrollWrapper.scrollLeft = pos * timeWindowWidth;
            }
        },
        handleClickNow() {
            const windowLengths = [3, 6, 12, 24, 72, 168];
            const now = new Date();
            const windowLength = windowLengths[this.mode - 1];

            if (now >= this.startDate && now < this.endDate) {
                const diffSeconds = (now - this.startDate) / 1000;
                const windowPage = parseInt(diffSeconds / 3600 / windowLength);
                const timeWindowWidth = this.$refs.gantt.clientWidth - 90;

                this.$refs.scrollWrapper.scrollLeft = windowPage * timeWindowWidth;
            }
            else {
                const baseUrl = `${this.ganttUrl}?mode=${this.mode}`;
                const newStartDate = new Date(now.getTime());
                newStartDate.setUTCDate(1);
                newStartDate.setUTCHours(0); newStartDate.setUTCMinutes(0); newStartDate.setUTCSeconds(0);

                const diffSeconds = (now - newStartDate) / 1000;
                const windowStartSeconds = parseInt(diffSeconds / 3600 / windowLength) * windowLength * 3600;
                newStartDate.setUTCSeconds(windowStartSeconds);

                window.location.href = `${baseUrl}&start=${parseInt(newStartDate.getTime() / 1000)}`;
            }
        },
        handleSubmitDateForm() {
            const startDateValue = this.$refs.startDateInput.value;
            const endDateValue = this.$refs.endDateInput.value;
            let url = `${this.ganttUrl}?mode=${this.mode}`;

            if (startDateValue) {
                var startDate = new Date(startDateValue);
                var _date = new Date(startDate.getTime());
                startDate.setUTCHours(0);
                startDate.setUTCDate(_date.getDate());
                url += `&start=${parseInt(startDate.getTime() / 1000)}`;
            }

            if (endDateValue) {
                var endDate = new Date(endDateValue);
                var _date = new Date(endDate.getTime());
                endDate.setUTCHours(0);
                endDate.setUTCDate(_date.getDate());
                url += `&end=${parseInt(endDate.getTime() / 1000)}`;
            }

            window.location.href = url;
        },
        handleDeleteRevision() {
            this.$http.post(this.deleteRevisionApiUrl, {
                revision: this.revision,
            })
            .then((response) => {
                const { data } = response;
                if (data.success) {
                    const revisions = [];
                    for (const index in data.revisions) {
                        const revision = data.revisions[index];
                        revisions.push({
                            id: revision.id,
                            published: new Date(revision.published * 1000),
                        });
                    }
                    this.revisions = revisions;

                    if (data.revisions.length > 0) {
                        this.revision = data.revisions[0].id;
                    } else {
                        this.revision = 0;
                    }

                    Vue.nextTick(() => {
                        this.loadData();
                    });
                }
            });
        },
        handleClearRevision() {
            this.$http.post(this.clearRevisionApiUrl, {
                revision: this.revision,
            })
            .then((response) => {
                const { data } = response;
                if (data.success) {
                    this.loadData();
                }
            });
        },
        handlePublishRevision() {
            this.$http.post(this.publishRevisionApiUrl, {
                revision: this.revision,
            })
            .then((response) => {
                const { data } = response;
                if (data.success) {
                    const revisions = [];
                    for (const index in data.revisions) {
                        const revision = data.revisions[index];
                        revisions.push({
                            id: revision.id,
                            published: new Date(revision.published * 1000),
                        });
                    }
                    this.revisions = revisions;
                    this.revision = data.revision;
                }
            });
        },
        handleDropOnRemoveZone(event) {
            this.dragoverRowShadows = {};

            const assignmentIds = Object.keys(this.selectedAssignmentIds);
            this.$http.post(this.removeAssignmentApiUrl, {
                assignment_data: JSON.stringify(assignmentIds),
                revision: this.revision,
            })
            .then((response) => {
                const { data } = response;
                if (data.success) {
                    this.loadData(true);
                }
            });
        },
        getTailIndex(tailNumber) {
            for (const index in this.tails) {
                const _tail = this.tails[index];
                if (tailNumber == _tail.number) {
                    return parseInt(index);
                }
            }
            return -1;
        },
        getLineIndex(lineId) {
            for (const index in this.lines) {
                const line = this.lines[index];
                if (lineId == line.id) {
                    return parseInt(index);
                }
            }
            return -1;
        },
        getAssignmentById(id) {
            for (const tailNumber in this.assignments) {
                if (this.assignments[tailNumber][id]) {
                    return this.assignments[tailNumber][id];
                }
            }
            return null;
        },
        getTemplateById(id) {
            for (const lineId in this.templates) {
                if (this.templates[lineId][id]) {
                    return this.templates[lineId][id];
                }
            }
            return null;
        },
        /* in handleDrag* methods, object should be dragged assignment/template object and null for prototypes,
         * status should be the status type value of the prototype and null for assignments/templates)
         */
        handleDragEnterAssignmentRow(tail, object, status) {
            const tailIndex = this.getTailIndex(tail.number);
            const dragoverRowShadows = {};

            if (object) {   /* Dragging assignments or templates */
                if (object.status) {    /* Dragging assignments */
                    const dragstartRowIndex = this.getTailIndex(object.tail);

                    for (const id in this.selectedAssignmentIds) {
                        const assignment = this.getAssignmentById(id);

                        if (!assignment || !assignment.flight_id) {
                            continue;
                        }

                        const srcRowIndex = this.getTailIndex(assignment.tail);
                        const dragOverTailIndex = tailIndex - dragstartRowIndex + srcRowIndex;
                        if (dragOverTailIndex >= 0 && dragOverTailIndex < this.tails.length) {
                            const tailId = this.tails[dragOverTailIndex].id;
                            const shadows = dragoverRowShadows[tailId] ? dragoverRowShadows[tailId] : [];
                            shadows.push(assignment);
                            dragoverRowShadows[tailId] = shadows;
                        }
                    }
                } else {    /* Dragging templates */
                    const dragstartRowIndex = this.getLineIndex(object.line_id);
                    for (const id in this.selectedTemplateIds) {
                        const template = this.getTemplateById(id);
                        if (!template) {
                            continue;
                        }

                        const srcRowIndex = this.getLineIndex(template.line_id);
                        const dragOverTailIndex = tailIndex - dragstartRowIndex + srcRowIndex;
                        if (dragOverTailIndex >= 0 && dragOverTailIndex < this.tails.length) {
                            const tailId = this.tails[dragOverTailIndex].id;
                            const shadows = dragoverRowShadows[tailId] ? dragoverRowShadows[tailId] : [];
                            shadows.push(template);
                            dragoverRowShadows[tailId] = shadows;
                        }
                    }
                }
                this.dragoverRowShadows = dragoverRowShadows;
            } else {    /* Dragging status prototype */
                // Status prototype has no dragging shadows by design so nothing to do here
            }
        },
        handleDragLeaveAssignmentRow(tail, object, status) {
        },
        handleDropOnAssignmentRow(tail, object, status, event, rowEl) {
            const tailIndex = this.getTailIndex(tail.number);
            let draggingStatusesOnly = true;

            this.dragoverRowShadows = {};

            if (object) {
                if (object.status) {    /* Assignment move */
                    const assignmentData = [];
                    const dragstartRowIndex = this.getTailIndex(object.tail);

                    for (const id in this.selectedAssignmentIds) {
                        const assignment = this.getAssignmentById(id);

                        if (!assignment) {
                            continue;
                        }

                        if (assignment.flight_id) {
                            draggingStatusesOnly = false;
                        }

                        const srcRowIndex = this.getTailIndex(assignment.tail);
                        const dragOverTailIndex = tailIndex - dragstartRowIndex + srcRowIndex;
                        if (dragOverTailIndex >= 0 && dragOverTailIndex < this.tails.length) {
                            assignmentData.push({
                                assignment_id: id,
                                tail: this.tails[dragOverTailIndex].number,
                            });
                        }
                    }

                    if (draggingStatusesOnly) {
                        /* Dragging only status assignments - which means dragging is horizontally free unlike flights */
                        assignmentData.length = 0;

                        const $row = $(rowEl);

                        for (const id in this.selectedAssignmentIds) {
                            const assignment = this.getAssignmentById(id);

                            if (!assignment) {
                                continue;
                            }

                            const srcRowIndex = this.getTailIndex(assignment.tail);
                            const dragOverTailIndex = tailIndex - dragstartRowIndex + srcRowIndex;
                            var startDiffSeconds = (new Date(assignment.start_time) - this.startDate) / 1000;
                            startDiffSeconds = Math.round(startDiffSeconds / 300) * 300;
                            var diffSeconds = this.ganttLengthSeconds / $row.width() * event.dragEvent.dx;
                            diffSeconds = Math.round(diffSeconds / 300) * 300;
                            var startTime = new Date(this.startDate.getTime() + startDiffSeconds * 1000 + diffSeconds * 1000);

                            if (dragOverTailIndex >= 0 && dragOverTailIndex < this.tails.length) {
                                assignmentData.push({
                                    assignment_id: id,
                                    tail: this.tails[dragOverTailIndex].number,
                                    start_time: startTime.toISOString(),
                                });
                            }
                        }
                    }

                    this.$http.post(this.moveAssignmentApiUrl, {
                        assignment_data: JSON.stringify(assignmentData),
                        revision: this.revision,
                    })
                    .then((response) => {
                        const { data } = response;
                        if (data.success) {
                            this.loadData(true);
                        }
                        this.alertErrorIfAny(data, assignmentData.length == 1);
                    });
                } else {                /* Template flight assign */
                    const flightData = [];
                    const dragstartRowIndex = this.getLineIndex(object.line_id);
                    for (const id in this.selectedTemplateIds) {
                        const template = this.getTemplateById(id);
                        if (!template) {
                            continue;
                        }

                        const srcRowIndex = this.getLineIndex(template.line_id);
                        const dragOverTailIndex = tailIndex - dragstartRowIndex + srcRowIndex;
                        if (dragOverTailIndex >= 0 && dragOverTailIndex < this.tails.length) {
                            flightData.push({
                                flight: id,
                                tail: this.tails[dragOverTailIndex].number,
                            });
                        }
                    }

                    flightData.sort((data1, data2) => {
                        var flight1 = this.getTemplateById(data1.flight);
                        var flight2 = this.getTemplateById(data2.flight);
                        if (flight1.departure_datetime > flight2.departure_datetime) {
                            return 1;
                        } else if (flight1.departure_datetime < flight2.departure_datetime) {
                            return -1;
                        } else {
                            return 0;
                        }
                    });

                    this.$http.post(this.assignFlightApiUrl, {
                        flight_data: JSON.stringify(flightData),
                        revision: this.revision,
                    })
                    .then((response) => {
                        const { data } = response;
                        if (data.success) {
                            this.loadData(true);
                        }
                        this.alertErrorIfAny(data, flightData.length == 1);
                    });
                }
            } else {
                const $row = $(rowEl);
                const x = event.dragEvent.clientX - $row.offset().left;
                var diffSeconds = this.ganttLengthSeconds / $row.width() * x;
                diffSeconds = Math.round(diffSeconds / 300) * 300;

                var startTime = new Date(this.startDate);
                startTime.setSeconds(startTime.getSeconds() + diffSeconds);
                startTime.setMinutes(0);
                startTime.setSeconds(0);
                var endTime = new Date(startTime.getTime() + 3600000);

                if (status == 3) {
                    this.unscheduledFlightCreateData = {
                        tail,
                        status,
                        startTime,
                        endTime,
                    };
                    this.$refs.unscheduledFlightModal.showModal();
                } else {
                    this.$http.post(this.assignStatusApiUrl, {
                        tail: tail.number,
                        status: status,
                        start_time: startTime.toISOString(),
                        end_time: endTime.toISOString(),
                        revision: this.revision,
                    })
                    .then((response) => {
                        const { data } = response;
                        if (data.success) {
                            this.loadData(true);
                        }
                    });
                }
            }
        },
        handleResizeBar(assignment_id, position, diff_seconds) {
            this.$http.post(this.resizeAssignmentApiUrl, {
                assignment_id,
                position,
                diff_seconds,
                revision: this.revision,
            })
            .then((response) => {
                const { data } = response;
                if (data.success) {
                    const startTime = new Date(data.start_time);
                    const endTime = new Date(data.end_time);

                    for (const tailNumber in this.assignments) {
                        if (this.assignments[tailNumber][assignment_id]) {
                            this.$set(this.assignments[tailNumber][assignment_id], 'start_time', startTime.toISOString());
                            this.$set(this.assignments[tailNumber][assignment_id], 'end_time', endTime.toISOString());
                            if (this.assignments[tailNumber][assignment_id].departure_datetime) {
                                this.$set(this.assignments[tailNumber][assignment_id], 'departure_datetime', startTime.toISOString());
                                this.$set(this.assignments[tailNumber][assignment_id], 'arrival_datetime', endTime.toISOString());
                            }
                            break;
                        }
                    }

                    this.loadData(true);
                }
            });
        },
        createUnscheduledFlight(origin, destination) {
            if (!this.unscheduledFlightCreateData.tail) {
                throw new Exception('Invalid unscheduled flight data');
            }

            var data = {
                tail: this.unscheduledFlightCreateData.tail.number,
                status: this.unscheduledFlightCreateData.status,
                start_time: this.unscheduledFlightCreateData.startTime.toISOString(),
                end_time: this.unscheduledFlightCreateData.endTime.toISOString(),
                origin,
                destination,
                revision: this.revision
            };

            this.$refs.unscheduledFlightModal.disableSubmit();

            this.$http.post(this.assignStatusApiUrl, data)
            .then((response) => {
                this.$refs.unscheduledFlightModal.enableSubmit();
                this.$refs.unscheduledFlightModal.hideModal();

                const { data } = response;
                if (data.success) {
                    this.loadData(true);
                }
            })
            .catch(() => {
                this.$refs.unscheduledFlightModal.enableSubmit();
            });
        },
        cancelUnscheduledFlightCreate() {
            this.unscheduledFlightCreateData = {};
        },
    },
    watch: {
        revision: function(val) {
            this.loadData();
        },
    }
}
</script>

<style>
#gantt-timezone {
    display: inline-block;
}
</style>