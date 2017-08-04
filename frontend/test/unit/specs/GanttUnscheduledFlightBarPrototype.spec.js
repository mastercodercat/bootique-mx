import Vue from 'vue';
import GanttUnscheduledFlightBarPrototype from '@frontend_components/GanttUnscheduledFlightBarPrototype.vue';

describe('GanttUnscheduledFlightBarPrototype.vue', () => {
    it('should render correct contents', () => {
        const Constructor = Vue.extend(GanttUnscheduledFlightBarPrototype);
        const vm = new Constructor().$mount()
        expect(vm.$el.querySelector('.text').textContent).to.equal('Unscheduled Flight')
    })

    it('should render correct dragging status', () => {
        const Constructor = Vue.extend(GanttUnscheduledFlightBarPrototype);
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
