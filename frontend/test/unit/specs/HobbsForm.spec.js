import Vue from 'vue'
import sinon from 'sinon'
import axios from 'axios'
import HobbsForm from '@frontend_components/HobbsForm.vue'
import testData from '../fixtures/ComingDueList.js'

const propsData = {
    type: 1,
    tailId: testData.tail.id,
    loadHobbsApiBase: '/routeplanning/api/hobbs/0',
    saveHobbsApi: '/routeplanning/api/tail/hobbs',
    urlToRedirectAfterSave: '/routeplanning/',
    writable: true,
}

const hobbsTimeString = '2017-04-20T06:00:00Z'

function to2Digits(n) {
    return n >= 10 ? n.toString() : '0' + n.toString()
}

describe('HobbsForm.vue', () => {
    let axiosGetStub, axiosPostStub

    before(function () {
        axiosGetStub = sinon.stub(axios, 'get')
        axiosPostStub = sinon.stub(axios, 'post')
        Vue.prototype.$http = axios
    })

    after(function () {
        axios.get.restore()
        axios.post.restore()
    })

    it('\'to2Digits\' and \'roundTo2\' methods should work correct', () => {
        expect(HobbsForm.methods.to2Digits(3)).to.equal('03')
        expect(HobbsForm.methods.to2Digits(15)).to.equal('15')
        expect(HobbsForm.methods.roundTo2(1.66667)).to.equal(1.67)
        expect(HobbsForm.methods.roundTo2(3)).to.equal(3.00)
    })

    it('should render correct contents', () => {
        const Constructor = Vue.extend(HobbsForm)
        const vm = new Constructor({
            propsData,
        }).$mount()
        expect(vm.$el.tagName).to.equal('FORM')
    })

    it('should react to \'set-values\' event by setting values into form field', () => {
        const hobbsTime = new Date(hobbsTimeString)
        const Constructor = Vue.extend(HobbsForm)
        const vm = new Constructor({
            propsData,
        }).$mount()

        vm.$emit('set-values', {
            date: hobbsTime,
            projected: 2.5,
        })

        expect(vm.$el.querySelector('.hobbs-id').value).to.equal('')
        expect(vm.$el.querySelector('.hobbs-date').value).to.equal(
            to2Digits(hobbsTime.getMonth() + 1) + '/' + to2Digits(hobbsTime.getDate()) + '/' + to2Digits(hobbsTime.getFullYear())
        )
        expect(vm.$el.querySelector('.hobbs-time').value).to.equal(
            to2Digits(hobbsTime.getHours()) + ':' + to2Digits(hobbsTime.getMinutes())
        )
        expect(vm.$el.querySelector('.hobbs-value').value).to.equal('2.5')
    })

    it('should react to \'load-hobbs\' event by loading values from api', (done) => {
        axiosGetStub.resolves({
            data: {
                pk: 1,
                type: 1,
                tail: testData.tail.id,
                hobbs: 1.5,
                hobbs_time: hobbsTimeString,
            }
        })

        const Constructor = Vue.extend(HobbsForm)
        const vm = new Constructor({
            propsData,
        }).$mount()
        vm.$emit('load-hobbs', 1)

        setTimeout(() => {
            const hobbsTime = new Date(hobbsTimeString)
            expect(vm.$el.querySelector('.hobbs-id').value).to.equal('1')
            expect(vm.$el.querySelector('.hobbs-date').value).to.equal(
                to2Digits(hobbsTime.getMonth() + 1) + '/' + to2Digits(hobbsTime.getDate()) + '/' + to2Digits(hobbsTime.getFullYear())
            )
            expect(vm.$el.querySelector('.hobbs-time').value).to.equal(
                to2Digits(hobbsTime.getHours()) + ':' + to2Digits(hobbsTime.getMinutes())
            )
            expect(vm.$el.querySelector('.hobbs-value').value).to.equal('1.5')
            done()
        }, 500)
    })

    it('\'submitForm\' should call save api with correct data', () => {
        const hobbsTime = new Date(hobbsTimeString)

        axiosPostStub.resolves({})

        const Constructor = Vue.extend(HobbsForm)
        const vm = new Constructor({
            propsData,
        }).$mount()

        vm.$emit('set-values', {
            date: hobbsTime,
            projected: 3.5,
        })
        vm.$el.querySelector('.hobbs-id').value = '3'
        vm.submitForm()

        expect(axiosPostStub.called).to.equal(true)
        const args = axiosPostStub.getCall(0).args
        expect(args[0]).to.equal(propsData.saveHobbsApi)
        expect(args[1].id).to.equal('3')
        expect(args[1].tail_id).to.equal(propsData.tailId)
        expect(args[1].type).to.equal(propsData.type)
        expect(args[1].hobbs).to.equal('3.5')
        expect(new Date(args[1].datetime).getTime()).to.equal(hobbsTime.getTime())
    })

    it('\'saveAndAddAnother\' should reset the form after save', () => {
        const hobbsTime = new Date(hobbsTimeString)

        axiosPostStub.resolves({})

        const Constructor = Vue.extend(HobbsForm)
        const vm = new Constructor({
            propsData,
        }).$mount()

        vm.$emit('set-values', {
            date: hobbsTime,
            projected: 3.5,
        })
        vm.$el.querySelector('.hobbs-id').value = '3'
        vm.saveAndAddAnother()

        setTimeout(() => {
            expect(vm.$el.querySelector('.hobbs-id').value).to.equal('')
            expect(vm.$el.querySelector('.hobbs-date').value).to.equal('')
            expect(vm.$el.querySelector('.hobbs-time').value).to.equal('')
            expect(vm.$el.querySelector('.hobbs-value').value).to.equal('')
        }, 0)
    })

    it('\'saveAndContinue\' should have new hobbs id in its hobbs id input field', () => {
        const hobbsTime = new Date(hobbsTimeString)

        axiosPostStub.resolves({
            data: {
                hobbs_id: 11,
            }
        })

        const Constructor = Vue.extend(HobbsForm)
        const vm = new Constructor({
            propsData,
        }).$mount()

        vm.$emit('set-values', {
            date: hobbsTime,
            projected: 3.5,
        })
        vm.saveAndContinue()

        setTimeout(() => {
            expect(vm.$el.querySelector('.hobbs-id').value).to.equal('11')
        }, 0)
    })
})
