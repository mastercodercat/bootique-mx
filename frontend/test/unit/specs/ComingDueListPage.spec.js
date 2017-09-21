import Vue from 'vue'
import sinon from 'sinon'
import axios from 'axios'
import ComingDueListPage from '@frontend_components/ComingDueListPage.vue'
import testData from '../fixtures/ComingDueList.js'

const propsData = {
    tailId: testData.tail.id,
    tailNumber: testData.tail.number,
    revision: 0,
    comingDueListApi: '/routeplanning/api/tail/comingduelist/',
    saveHobbsApi: '/routeplanning/api/tail/savehobbs/',
    loadHobbsApiBase: '/routeplanning/api/tail/hobbs/',
    urlToRedirectAfterSave: '/',
    writable: true,
}

describe('ComingDueListPage.vue', () => {
    let axiosPostStub

    before(function () {
        axiosPostStub = sinon.stub(axios, 'post')
        Vue.prototype.$http = axios
    })

    after(function () {
        axios.post.restore()
    })

    it('should render correct contents based on hobbs data from api', () => {
        axiosPostStub.resolves({
            data: {
                hobbs_list: testData.hobbsData,
            }
        })

        const Constructor = Vue.extend(ComingDueListPage)
        const vm = new Constructor({
            propsData,
        }).$mount()

        setTimeout(() => {
            expect(vm.$el.tagName).to.equal('DIV')
            expect(vm.$el.querySelectorAll('form').length).to.equal(2)
            expect(vm.$el.querySelectorAll('#coming-due-list').length).to.equal(1)
            expect(vm.$el.querySelectorAll('#coming-due-list tr').length).to.equal(testData.hobbsData.length)
        }, 0)
    })

    it('should respond to \'refresh-coming-due-list\' event from hobbs forms', () => {
        axiosPostStub.resolves({
            data: {
                hobbs_list: testData.hobbsData,
            }
        })

        const refreshComingDueListStub = sinon.stub(ComingDueListPage.methods, 'refreshComingDueList')
        const Constructor = Vue.extend(ComingDueListPage)
        const vm = new Constructor({
            propsData,
        }).$mount()

        vm.$refs.actualHobbsForm.$emit('refresh-coming-due-list')
        expect(refreshComingDueListStub.called).to.equal(true)

        refreshComingDueListStub.resetHistory()
        vm.$refs.nextDueHobbsForm.$emit('refresh-coming-due-list')
        expect(refreshComingDueListStub.called).to.equal(true)

        refreshComingDueListStub.restore()
    })
})
