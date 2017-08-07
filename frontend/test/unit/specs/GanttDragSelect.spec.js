import Vue from 'vue'
import GanttBar from '@frontend_components/GanttBar.vue'
import GanttDragSelect from '@frontend_components/GanttDragSelect.vue'
import testData1 from '../fixtures/GanttMaintenanceBar.js'
import testData2 from '../fixtures/GanttUnscheduledFlightBar.js'

const assignment1 = testData1.assignment
const assignment2 = testData2.flight
const startDate = testData1.startDate

function testGanttDragSelectComponent(selectedBars = []) {
    return Vue.extend({
        template: `<GanttDragSelect item-selector=".bar" :editing="true" v-model="selectedBars">
            <div class="row-line" style="position: relative; width: 2500px; height: 30px;">
                <GanttBar
                    id="bar1"
                    :data="assignment1"
                    :startDate="startDate"
                    :timezone="-7"
                    :unit="3600"
                ></GanttBar>
                <GanttBar
                    id="bar2"
                    :data="assignment2"
                    :startDate="startDate"
                    :timezone="-7"
                    :unit="3600"
                ></GanttBar>
            </div>
        </GanttDragSelect>`,
        components: {
            GanttDragSelect,
            GanttBar,
        },
        props: ['assignment1', 'assignment2', 'startDate'],
        data() {
            return {
                selectedBars,
            }
        },
    })
}

function dispatchMouseEvent(elem, eventName, x, y, altKey = false, shiftKey = false) {
    const event = new Event(eventName, {
        view: window,
        bubbles: true,
    })
    event.pageX = x
    event.pageY = y
    // event.altKey = altKey
    event.shiftKey = shiftKey
    elem.dispatchEvent(event)
}

describe('GanttDragSelect.vue', () => {
    it('should render initial state', () => {
        const Constructor = Vue.extend(GanttDragSelect)
        const vm = new Constructor({
            propsData: {
                itemSelector: '.bar',
                value: [],
                editing: true,
            }
        }).$mount()
        expect(vm.$el.classList.contains('drag-select')).to.equal(true)
        expect(vm.$el.querySelectorAll('.selection-area-indicator').length).not.to.equal(0)
    })

    it('should be able to select items by drag-select', (done) => {
        const Constructor = testGanttDragSelectComponent()
        const vm = new Constructor({
            propsData: {
                assignment1,
                assignment2,
                startDate,
            }
        }).$mount()

        const $el = $(vm.$el)
        dispatchMouseEvent($el[0], 'mousedown', 0, 0)
        Vue.nextTick()
        .then(() => {
            dispatchMouseEvent($el[0], 'mouseup', 2500, 30)
            return Vue.nextTick()
        })
        .then(() => {
            expect(vm.selectedBars[assignment1.id]).not.to.equal(undefined)
            expect(vm.selectedBars[assignment2.id]).not.to.equal(undefined)
            done()
        })
    })

    it('should be able to add items to selection by shift key + drag-select', (done) => {
        const Constructor = testGanttDragSelectComponent({
            [assignment2.id]: assignment2,
        })
        const vm = new Constructor({
            propsData: {
                assignment1,
                assignment2,
                startDate,
            }
        }).$mount()

        const $el = $(vm.$el)
        dispatchMouseEvent($el[0], 'mousedown', 445, 0)
        Vue.nextTick()
        .then(() => {
            dispatchMouseEvent($el[0], 'mouseup', 465, 30, false, true)
            return Vue.nextTick()
        })
        .then(() => {
            expect(vm.selectedBars[assignment1.id]).not.to.equal(undefined)
            expect(vm.selectedBars[assignment2.id]).not.to.equal(undefined)
            done()
        })
    })
})
