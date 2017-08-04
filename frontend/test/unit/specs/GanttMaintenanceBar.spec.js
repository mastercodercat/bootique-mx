import Vue from 'vue'
import GanttMaintenanceBar from '@frontend_components/GanttMaintenanceBar.vue'
import testData from '../fixtures/GanttMaintenanceBar.js'

describe('GanttMaintenanceBar.vue', () => {
    it('should render correct contents', () => {
        const Constructor = Vue.extend(GanttMaintenanceBar)
        const vm = new Constructor({
            propsData: {
                assignment: testData.assignment,
                startDate: testData.startDate,
                timezone: -7,
                unit: 3600,
            }
        }).$mount()
        expect(vm.$el.style.left)
            .to.equal(((new Date(testData.assignment.start_time) - testData.startDate) / (14 * 24 * 3600) / 10) + '%')
        expect(vm.$el.style.width).to.equal((5400 / (14 * 24 * 3600) * 100) + '%')
        expect(vm.$el.querySelector('.text').textContent).to.equal('Maintenance')
    })

    it('should render correct selected status', () => {
        const Constructor = Vue.extend(GanttMaintenanceBar)
        const vm = new Constructor({
            propsData: {
                assignment: testData.assignment,
                startDate: testData.startDate,
                timezone: -7,
                unit: 3600,
                selected: true,
            }
        }).$mount()
        expect(vm.$el.classList.contains('selected')).to.equal(true)
    })

    it('should render correct dragging status', () => {
        const Constructor = Vue.extend(GanttMaintenanceBar)
        const vm = new Constructor({
            propsData: {
                assignment: testData.assignment,
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

    it('should render correct resizing status', () => {
        const Constructor = Vue.extend(GanttMaintenanceBar)
        const vm = new Constructor({
            propsData: {
                assignment: testData.assignment,
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
