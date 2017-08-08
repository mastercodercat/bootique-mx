import Vue from 'vue'
import GanttBar from '@frontend_components/GanttBar.vue'
import GanttPopover from '@frontend_components/GanttPopover.vue'
import maintenanceAssignmentData from '../fixtures/GanttMaintenanceBar.js'
import unscheduledFlightAssignmentData from '../fixtures/GanttUnscheduledFlightBar.js'

function testGanttPopoverComponent() {
    return Vue.extend({
        template: `<div>
            <div style="padding: 100px; position: relative; width: 2500px; height: 30px;">
                <GanttBar
                    ref="bar1"
                    :data="assignment1"
                    :startDate="startDate"
                    :timezone="-7"
                    :unit="3600"
                    v-if="assignment1"
                ></GanttBar>
                <GanttBar
                    ref="bar2"
                    :data="assignment2"
                    :startDate="startDate"
                    :timezone="-7"
                    :unit="3600"
                    v-if="assignment2"
                ></GanttBar>
            </div>
            <GanttPopover
                :timezone="-7"
                :writable="true"
            ></GanttPopover>
        </div>`,
        props: ['assignment1', 'assignment2', 'startDate'],
        components: {
            GanttBar,
            GanttPopover,
        },
    })
}

describe('GanttPopover.vue', () => {
    it('should render initial state correctly', () => {
        const Constructor = testGanttPopoverComponent()
        const vm = new Constructor().$mount()
        expect(vm.$el.nodeName).to.equal('DIV')
        expect(vm.$el.querySelectorAll('.gantt-bar-popover').length).to.equal(0)
    })

    it('should show/hide popover in reaction to `popover-show` and `popover-hide` Vue events', (done) => {
        const Constructor = testGanttPopoverComponent()
        const vm = new Constructor({
            propsData: {
                assignment1: maintenanceAssignmentData,
                assignment2: unscheduledFlightAssignmentData,
                startDate: maintenanceAssignmentData.startDate,
            }
        }).$mount()
        vm.$emit('popover-show', vm.$refs.bar1.$el, maintenanceAssignmentData)
        Vue.nextTick()
        .then(() => {
            expect(vm.$el.querySelectorAll('.gantt-bar-popover').length).to.equal(1)        // Show popover
            vm.$emit('popover-hide')
            setTimeout(() => {
                expect(vm.$el.querySelectorAll('.gantt-bar-popover').length).to.equal(0)    // Hide popover
                done()
            }, 200)
        })
    })
})
