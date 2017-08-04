import Vue from 'vue'
import GanttUnscheduledFlightBar from '@frontend_components/GanttUnscheduledFlightBar.vue'
import testData from '../fixtures/GanttUnscheduledFlightBar.js'

describe('GanttUnscheduledFlightBar.vue', () => {
    it('should render correct contents', () => {
        const Constructor = Vue.extend(GanttUnscheduledFlightBar)
        const vm = new Constructor({
            propsData: {
                flight: testData.flight,
                startDate: testData.startDate,
                timezone: -7,
                unit: 3600,
            }
        }).$mount()
        expect(vm.$el.style.left)
            .to.equal(((new Date(testData.flight.actual_out_datetime) - testData.startDate) / (14 * 24 * 3600) / 10) + '%')
        expect(vm.$el.style.width).to.equal((5400 / (14 * 24 * 3600) * 100) + '%')
        expect(vm.$el.querySelector('.text').textContent).to.equal('Unscheduled Flight')
    })

    it('should render correct selected status', () => {
        const Constructor = Vue.extend(GanttUnscheduledFlightBar)
        const vm = new Constructor({
            propsData: {
                flight: testData.flight,
                startDate: testData.startDate,
                timezone: -7,
                unit: 3600,
                selected: true,
            }
        }).$mount()
        expect(vm.$el.classList.contains('selected')).to.equal(true)
    })

    it('should render correct dragging status', () => {
        const Constructor = Vue.extend(GanttUnscheduledFlightBar)
        const vm = new Constructor({
            propsData: {
                flight: testData.flight,
                startDate: testData.startDate,
                timezone: -7,
                unit: 3600,
                dragging: true,
                dragOffset: {
                    x: 100, y: 150,
                },
            }
        }).$mount()
        expect(vm.$el.classList.contains('drag-clone')).to.equal(true)
        expect(vm.$el.style.webkitTransform).to.match(/translate\(100px,\s+150px\)/g)
    })

    it('should have correct `startTime` and `endTime` values based on estimated times', () => {
        const Constructor = Vue.extend(GanttUnscheduledFlightBar)
        const flight = Object.assign({}, testData.flight)
        delete flight.actual_out_datetime
        delete flight.actual_in_datetime
        const vm = new Constructor({
            propsData: {
                flight: flight,
                startDate: testData.startDate,
                timezone: -7,
                unit: 3600,
            }
        }).$mount()
        expect(vm.startTime.getTime()).to.equal(new Date('2017-08-03T12:00:00Z').getTime())
        expect(vm.endTime.getTime()).to.equal(new Date('2017-08-03T13:30:00Z').getTime())
    })

    it('should have correct `startTime` and `endTime` values based on actual times', () => {
        const Constructor = Vue.extend(GanttUnscheduledFlightBar)
        const flight = Object.assign({}, testData.flight)
        const vm = new Constructor({
            propsData: {
                flight: testData.flight,
                startDate: testData.startDate,
                timezone: -7,
                unit: 3600,
            }
        }).$mount()
        expect(vm.startTime.getTime()).to.equal(new Date('2017-08-03T15:00:00Z').getTime())
        expect(vm.endTime.getTime()).to.equal(new Date('2017-08-03T16:30:00Z').getTime())
    })

    it('should render correct resizing status', () => {
        const Constructor = Vue.extend(GanttUnscheduledFlightBar)
        const vm = new Constructor({
            propsData: {
                flight: testData.flight,
                startDate: testData.startDate,
                timezone: -7,
                unit: 3600,
            },
            data: {
                resizing: true,
                barWidth: 150,
                transform: 'translateX(-50px)',
            },
        }).$mount()
        expect(vm.$el.classList.contains('resizing')).to.equal(true)
        expect(vm.$el.style.width).to.equal('150px')
        expect(vm.$el.style.webkitTransform).to.equal('translateX(-50px)')
    })
})
