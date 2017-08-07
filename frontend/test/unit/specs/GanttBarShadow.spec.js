import Vue from 'vue'
import GanttBarShadow from '@frontend_components/GanttBarShadow.vue'
import testData from '../fixtures/GanttUnscheduledFlightBar.js'

describe('GanttBarShadow.vue', () => {
    it('should render correct contents', () => {
        const Constructor = Vue.extend(GanttBarShadow)
        const vm = new Constructor({
            propsData: {
                data: testData.flight,
                startDate: testData.startDate,
            }
        }).$mount()
        const ganttLength = 14 * 24 * 3600      // 2 weeks
        const expectedLeftPos = (new Date(testData.flight.start_time) - testData.startDate) / 1000 / ganttLength * 100;
        expect(vm.$el.style.left).to.equal(expectedLeftPos + '%')
        const expectedWidth = (new Date(testData.flight.end_time) - new Date(testData.flight.start_time)) / 1000 / ganttLength * 100;
        expect(vm.$el.style.width).to.equal(expectedWidth + '%')
    })
})
