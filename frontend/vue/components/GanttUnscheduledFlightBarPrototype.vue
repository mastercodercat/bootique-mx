<template>
    <div :class="{ 'bar status-bar unscheduled-flight status-prototype': true, 'drag-clone': dragged }" :style="componentStyle">
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
</template>

<script>
export default {
    name: 'GanttUnscheduledFlightBarPrototype',
    props: ['status', 'dragged', 'drag-offset'],
    computed: {
        componentStyle() {
            if (this.dragOffset) {
                return {
                    'transform': `translate(${this.dragOffset.x}px, ${this.dragOffset.y}px)`,
                };
            } else {
                return {};
            }
        },
    },
}
</script>
