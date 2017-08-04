import Vue from 'vue'
import GanttMaintenanceBarPrototype from '@frontend_components/GanttMaintenanceBarPrototype.vue'

describe('GanttMaintenanceBarPrototype.vue', () => {
    it('should render correct contents', () => {
        const Constructor = Vue.extend(GanttMaintenanceBarPrototype)
        const vm = new Constructor().$mount()
        expect(vm.$el.querySelector('.text').textContent).to.equal('Maintenance')
    })

    it('should render correct dragging status', () => {
        const Constructor = Vue.extend(GanttMaintenanceBarPrototype)
        const vm = new Constructor({
            propsData: {
                dragged: true,
                dragOffset: {
                    x: 100, y: 150,
                },
            }
        }).$mount()
        expect(vm.$el.classList.contains('drag-clone')).to.equal(true)
        expect(vm.$el.style.webkitTransform).to.match(/translate\(100px,\s+150px\)/g)
    })
})
