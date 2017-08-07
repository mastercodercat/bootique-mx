import Vue from 'vue'
import GanttAssignmentErrorModal from '@frontend_components/GanttAssignmentErrorModal.vue'
import testData from '../fixtures/conflict-data.js'

describe('GanttAssignmentErrorModal.vue', () => {
    it('should render correct contents', () => {
        const Constructor = Vue.extend(GanttAssignmentErrorModal)
        const vm = new Constructor({
            propsData: {
                conflictData: testData,
            }
        }).$mount()
        expect(vm.$el.querySelector('.modal-title').textContent).to.equal('Assignment Errors')
        expect(vm.$el.querySelector('.modal-body').children.length).to.equal(2)
    })

    it('should show/hide modal when showModal()/hideModal() is called', (done) => {
        const Constructor = Vue.extend(GanttAssignmentErrorModal)
        const vm = new Constructor({
            propsData: {
                conflictData: testData,
            }
        }).$mount()
        vm.showModal()
        Vue.nextTick().then(() => {
            expect(vm.$el.classList.contains('in')).to.equal(true)
            vm.hideModal()
            return Vue.nextTick()
        })
        .then(() => {
            expect(vm.$el.classList.contains('in')).to.equal(false)
            done()
        })
    })
})
