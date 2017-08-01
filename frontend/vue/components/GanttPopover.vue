<template>
    <div v-if="data">
        <div class="gantt-bar-popover" :style="componentStyle" ref="popover">

            <!-- Maintenance bar popover -->
            <div class="info bar-popover" v-if="data.status == 2">
                <div class="field">Status: Maintenance</div>
                <div class="field">Sched. Start Time: <span class="start"></span>{{ startTime }}</div>
                <div class="field">Sched. End Time: <span class="end"></span>{{ endTime }}</div>
            </div>

            <!-- Unscheduled flight bar popover -->
            <div class="bar-popover" v-else-if="data.status == 3">
                <div class="field">Unscheduled Flight</div>
                <div class="field">Origin: <span class="org">{{ data.origin }}</span></div>
                <div class="field">Destination: <span class="dest">{{ data.destination }}</span></div>
                <div class="field">Sched. OUT Time: <span class="departure">{{ scheduledOutDateTimeFormatted }}</span></div>
                <div class="field">Sched. IN Time: <span class="arrival">{{ scheduledInDateTimeFormatted }}</span></div>
                <template v-if="isEstimated">
                    <div class="field">Estimated OUT Time: <span class="departure">{{ estimatedOutDateTimeFormatted }}</span></div>
                    <div class="field">Estimated IN Time: <span class="arrival">{{ estimatedInDateTimeFormatted }}</span></div>
                </template>
                <template v-if="isActual">
                    <div class="field">Actual OUT Time: <span class="departure">{{ actualOutDateTimeFormatted }}</span></div>
                    <div class="field">Actual IN Time: <span class="arrival">{{ actualInDateTimeFormatted }}</span></div>
                </template>
                <div class="assignment-only">
                    <hr />
                    <div class="field">
                        Projected Hobbs: <span class="projected-hobbs">{{ data.actual_hobbs.toFixed(1) }}</span>
                    </div>
                    <div class="field">
                        Next Due Hobbs: <span class="next-due-hobbs"></span>{{ data.next_due_hobbs.toFixed(1) }}
                    </div>
                    <div :class="fieldHobbsLeftClass">
                        Hobbs Left: <span class="hobbs-left">{{ (data.next_due_hobbs - data.actual_hobbs).toFixed(1) }}</span>
                    </div>
                </div>
                <a class="edit-flight-link"
                    :href="`/routeplanning/flights/${data.flight_id}`"
                    v-if="writable">
                    <i class="fa fa-pencil-square-o"></i>
                </a>
            </div>

            <!-- Flight bar popover -->
            <div class="bar-popover" v-else>
                <div class="field">Flight <span class="number">{{ data.number }}</span></div>
                <div class="field">Origin: <span class="org">{{ data.origin }}</span></div>
                <div class="field">Destination: <span class="dest">{{ data.destination }}</span></div>
                <div class="field">Sched. OUT Time: <span class="departure">{{ scheduledOutDateTimeFormatted }}</span></div>
                <div class="field">Sched. IN Time: <span class="arrival">{{ scheduledInDateTimeFormatted }}</span></div>
                <template v-if="isEstimated">
                    <div class="field">Estimated OUT Time: <span class="departure">{{ estimatedOutDateTimeFormatted }}</span></div>
                    <div class="field">Estimated IN Time: <span class="arrival">{{ estimatedInDateTimeFormatted }}</span></div>
                </template>
                <template v-if="isActual">
                    <div class="field">Actual OUT Time: <span class="departure">{{ actualOutDateTimeFormatted }}</span></div>
                    <div class="field">Actual IN Time: <span class="arrival">{{ actualInDateTimeFormatted }}</span></div>
                </template>
                <div v-if="data.actual_hobbs">
                    <hr />
                    <div class="field">
                        Projected Hobbs: <span class="projected-hobbs">{{ data.actual_hobbs.toFixed(1) }}</span>
                    </div>
                    <div class="field">
                        Next Due Hobbs: <span class="next-due-hobbs"></span>{{ data.next_due_hobbs.toFixed(1) }}
                    </div>
                    <div :class="fieldHobbsLeftClass">
                        Hobbs Left: <span class="hobbs-left">{{ (data.next_due_hobbs - data.actual_hobbs).toFixed(1) }}</span>
                    </div>
                </div>
                <a class="edit-flight-link"
                    :href="`/routeplanning/flights/${data.flight_id}`"
                    v-if="writable">
                    <i class="fa fa-pencil-square-o"></i>
                </a>
            </div>

        </div>
    </div>
</template>

<script>
import moment from 'moment-timezone';

export default {
    name: 'GanttPopover',
    props: {
        'timezone': {
            type: Number,
            required: true,
        },
        'writable': {
            type: Boolean,
            required: true,
        },
    },
    data() {
        return {
            anchor: null,
            data: null,
            componentStyle: '',
            onBar: false,
            onPopover: false,
        };
    },
    computed: {
        isEstimated() {
            return this.data.estimated_in_datetime && this.data.estimated_out_datetime;
        },
        isActual() {
            return this.data.actual_in_datetime && this.data.actual_out_datetime;
        },
        startTime() {
            const date = new Date(this.data.start_time);
            return this.formatDate(date);
        },
        endTime() {
            const date = new Date(this.data.end_time);
            return this.formatDate(date);
        },
        scheduledOutDateTimeFormatted() {
            const date = new Date(this.data.scheduled_out_datetime);
            return this.formatDate(date);
        },
        scheduledInDateTimeFormatted() {
            const date = new Date(this.data.scheduled_in_datetime);
            return this.formatDate(date);
        },
        estimatedOutDateTimeFormatted() {
            const date = new Date(this.data.estimated_out_datetime);
            return this.formatDate(date);
        },
        estimatedInDateTimeFormatted() {
            const date = new Date(this.data.estimated_in_datetime);
            return this.formatDate(date);
        },
        actualOutDateTimeFormatted() {
            const date = new Date(this.data.actual_out_datetime);
            return this.formatDate(date);
        },
        actualInDateTimeFormatted() {
            const date = new Date(this.data.actual_in_datetime);
            return this.formatDate(date);
        },
        hobbs() {
            return this.data.next_due_hobbs - this.data.actual_hobbs;
        },
        fieldHobbsLeftClass() {
            return {
                'field field-hobbs-left': true,
                'hobbs-green': this.hobbs < 15 && this.hobbs >= 8,
                'hobbs-yellow': this.hobbs < 8 && this.hobbs >= 0,
                'hobbs-red': this.hobbs < 0,
            };
        },
    },
    mounted() {
        this.$root.$on('popover-show', this.handlePopoverShow);
        this.$root.$on('popover-hide', this.handlePopoverHide);
        $('body').on('mouseenter', '.gantt-bar-popover', this.handlePopoverMouseEnter);
        $('body').on('mouseleave', '.gantt-bar-popover', this.handlePopoverMouseLeave);
        $(window).on('scroll', this.updateComponentStyle)
    },
    beforeDestroy() {
        this.$root.$off('popover-show', this.handlePopoverShow);
        this.$root.$off('popover-hide', this.handlePopoverHide);
        $('body').off('mouseenter', '.gantt-bar-popover', this.handlePopoverMouseEnter);
        $('body').off('mouseleave', '.gantt-bar-popover', this.handlePopoverMouseLeave);
        $(window).off('scroll', this.updateComponentStyle)
    },
    methods: {
        formatDate(date, dateFormat = 'MM/DD/YYYY HH:mm:ss') {
            if (typeof date === 'string') {
                var _date = new Date(date);
            } else {
                var _date = new Date(date.getTime());
            }
            _date.setHours(parseInt(_date.getHours()) + parseInt(this.timezone));
            return moment(_date).tz('UTC').format(dateFormat);
        },
        updateComponentStyle() {
            let style = '';
            if (this.anchor) {
                const $anchor = $(this.anchor);
                style += `left: ${$anchor.offset().left}px;`;
                style += `top: ${$anchor.offset().top - $(window).scrollTop()}px;`;
            }
            this.componentStyle = style;
        },
        checkShouldPopoverBeHidden() {
            if (!this.onBar && !this.onPopover) {
                this.anchor = null;
                this.data = null;
            }
        },
        handlePopoverShow(anchor, data) {
            this.anchor = anchor;
            this.data = data;
            this.onBar = true;
            this.updateComponentStyle();
        },
        handlePopoverHide(anchor, data) {
            this.onBar = false;
            setTimeout(() => {
                this.checkShouldPopoverBeHidden();
            }, 100);
        },
        handlePopoverMouseEnter() {
            this.onPopover = true;
        },
        handlePopoverMouseLeave() {
            this.onPopover = false;
            this.checkShouldPopoverBeHidden();
        },
    }
};
</script>
