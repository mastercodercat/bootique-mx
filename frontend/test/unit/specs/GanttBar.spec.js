require('phantomjs-polyfill-find')
import Vue from 'vue'
import sinon from 'sinon'
import GanttBar from '@frontend_components/GanttBar.vue'
import testData from '../fixtures/full-data.js'

const flightAssignment = testData.assignments.find(assignment => assignment.status === 1)
const maintenanceAssignment = testData.assignments.find(assignment => assignment.status === 2)
const unscheduledFlightAssignment = testData.assignments.find(assignment => assignment.status === 3)

describe('GanttBar.vue', () => {
    it('should render flight assignment correctly', () => {
        const Constructor = Vue.extend(GanttBar)
        const vm = new Constructor({
            propsData: {
                data: flightAssignment,
                startDate: testData.startDate,
                timezone: -7,
                unit: 3600,
            }
        }).$mount()
        expect(vm.$el.classList.contains('gantt-bar')).to.equal(true)
        expect(vm.$el.querySelector('.bar:not(.status-bar)').length).not.to.equal(0)
    })

    it('should render maintenance assignment correctly', () => {
        const Constructor = Vue.extend(GanttBar)
        const vm = new Constructor({
            propsData: {
                data: maintenanceAssignment,
                startDate: testData.startDate,
                timezone: -7,
                unit: 3600,
            }
        }).$mount()
        expect(vm.$el.classList.contains('gantt-bar')).to.equal(true)
        expect(vm.$el.querySelector('.bar.status-bar.maintenance').length).not.to.equal(0)
    })

    it('should render unscheduled flight assignment correctly', () => {
        const Constructor = Vue.extend(GanttBar)
        const vm = new Constructor({
            propsData: {
                data: unscheduledFlightAssignment,
                startDate: testData.startDate,
                timezone: -7,
                unit: 3600,
            }
        }).$mount()
        expect(vm.$el.classList.contains('gantt-bar')).to.equal(true)
        expect(vm.$el.querySelector('.bar.status-bar.unscheduled-flight').length).not.to.equal(0)
    })

    it('should react to `mouseenter` event', () => {
        const spy = sinon.spy(GanttBar.methods, 'handleMouseEnter')
        const Constructor = Vue.extend(GanttBar)
        const vm = new Constructor({
            propsData: {
                data: flightAssignment,
                startDate: testData.startDate,
                timezone: -7,
                unit: 3600,
            }
        }).$mount()
        $(vm.$el).trigger('mouseenter')
        expect(spy.called).to.equal(true)
    })

    it('should react to `mouseleave` event', () => {
        const spy = sinon.spy(GanttBar.methods, 'handleMouseLeave')
        const Constructor = Vue.extend(GanttBar)
        const vm = new Constructor({
            propsData: {
                data: flightAssignment,
                startDate: testData.startDate,
                timezone: -7,
                unit: 3600,
            }
        }).$mount()
        $(vm.$el).trigger('mouseleave')
        expect(spy.called).to.equal(true)
    })
})
