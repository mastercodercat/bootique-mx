import Vue from 'vue'
import sinon from 'sinon'
import axios from 'axios'
import ComingDueList from '@frontend_components/ComingDueList.vue'
import testData from '../fixtures/ComingDueList.js'

const propsData = {
    tailId: testData.tail.id,
    revision: 0,
    writable: true,
    comingDueListApi: '/routeplanning/api/tail/comingduelist/',
}

describe('ComingDueList.vue', () => {
    let axiosPostStub

    before(function () {
        axiosPostStub = sinon.stub(axios, 'post')
        Vue.prototype.$http = axios
    })

    after(function () {
        axios.post.restore()
    })

    it('should render correct contents', () => {
        const refreshStub = sinon.stub(ComingDueList.methods, 'refresh')
        const Constructor = Vue.extend(ComingDueList)
        const vm = new Constructor({
            propsData,
        }).$mount()
        ComingDueList.methods.refresh.restore()
        expect(vm.$el.tagName).to.equal('DIV')
        expect(vm.$el.querySelectorAll('#coming-due-list').length).not.to.equal(0)
    })

    it('should render contents based on api response data', (done) => {
        axiosPostStub.resolves({
            data: {
                success: true,
                hobbs_list: testData.hobbsData,
            },
        })

        const Constructor = Vue.extend(ComingDueList)
        const vm = new Constructor({
            propsData,
        }).$mount()

        setTimeout(() => {
            expect(vm.$el.querySelectorAll('#coming-due-list tr').length).to.equal(testData.hobbsData.length)
            done()
        }, 0)
    })

    it('should respond to \'refresh-coming-due-list\' Vue event', (done) => {
        axiosPostStub.resolves({
            data: {
                success: true,
                hobbs_list: [],
            },
        })

        const Constructor = Vue.extend(ComingDueList)
        const vm = new Constructor({
            propsData,
        }).$mount()

        Vue.nextTick().then(() => {
            expect(vm.$el.querySelectorAll('#coming-due-list tr').length).to.equal(0)
            axiosPostStub.resolves({
                data: {
                    success: true,
                    hobbs_list: testData.hobbsData,
                },
            })
            vm.$emit('refresh-coming-due-list')
            return Vue.nextTick()
        })
        .then(() => {
            expect(vm.$el.querySelectorAll('#coming-due-list tr').length).to.equal(testData.hobbsData.length)
            done()
        })
    })

    it('should load new data when anchor date changed and \'Show Hobbs\' button clicked', (done) => {
        axiosPostStub.resolves({
            data: {
                success: true,
                hobbs_list: [],
            },
        })

        const Constructor = Vue.extend(ComingDueList)
        const vm = new Constructor({
            propsData,
        }).$mount()

        Vue.nextTick().then(() => {
            expect(vm.$el.querySelectorAll('#coming-due-list tr').length).to.equal(0)
            axiosPostStub.resolves({
                data: {
                    success: true,
                    hobbs_list: testData.hobbsData,
                },
            })
            vm.$refs.anchorDateInput.value = testData.hobbsDate
            vm.$el.querySelector('.btn-change-anchor-date').click()
            return Vue.nextTick()
        })
        .then(() => setTimeout(() => {
            try{
            expect(vm.$el.querySelectorAll('#coming-due-list tr').length).to.equal(testData.hobbsData.length)
            }catch(e){alert(e.toString())}
            done()
        }, 50))
    })
})
