import Vue from 'vue'
import GanttUnscheduledFlightModal from '@frontend_components/GanttUnscheduledFlightModal.vue'
import testData from '../fixtures/conflict-data.js'

function dispatchChangeEvent(elem) {
    const event = document.createEvent("HTMLEvents");
    event.initEvent("change", false, true);
    elem.dispatchEvent(event);
}

describe('GanttUnscheduledFlightModal.vue', () => {
    it('should render correct contents', () => {
        const Constructor = Vue.extend(GanttUnscheduledFlightModal)
        const vm = new Constructor().$mount()
        expect(vm.$el.querySelector('.modal-title').textContent).to.equal('Create Unscheduled Flight')
        expect(vm.$el.querySelector('.modal-body').children[0].tagName).to.equal('FORM')
    })

    it('should show/hide modal when showModal()/hideModal() is called', (done) => {
        const Constructor = Vue.extend(GanttUnscheduledFlightModal)
        const vm = new Constructor().$mount()
        vm.showModal()
        setTimeout(() => {
            expect(vm.$el.classList.contains('in')).to.equal(true)
            vm.hideModal()
            Vue.nextTick().then(() => {
                expect(vm.$el.classList.contains('in')).to.equal(false)
                done()
            })
        }, 300)
    })

    it('should return correct data when submitted', (done) => {
        const TestComponent = {
            template: `<div>
                <GanttUnscheduledFlightModal
                    ref="unscheduledFlightModal"
                    @submit="handleSubmit"
                ></GanttUnscheduledFlightModal>
            </div>`,
            components: {
                GanttUnscheduledFlightModal
            },
            methods: {
                handleSubmit() {},
            }
        }

        const submitSpy = sinon.spy(TestComponent.methods, 'handleSubmit')

        const Constructor = Vue.extend(TestComponent)
        const vm = new Constructor().$mount()
        const modal = vm.$refs.unscheduledFlightModal
        modal.origin = 'MCE'
        modal.destination = 'LAX'
        Vue.nextTick().then(() => {
            modal.$el.querySelector('.btn-save-unscheduled-flight').click()
            const args = submitSpy.getCall(0).args
            expect(submitSpy.called).to.equal(true)
            expect(args[0]).to.equal('MCE')
            expect(args[1]).to.equal('LAX')
            done()
        })
    })
})
