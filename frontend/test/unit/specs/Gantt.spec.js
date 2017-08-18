import Vue from 'vue'
import sinon from 'sinon'
import axios from 'axios'
import Cookies from 'js-cookie'
import Gantt from '@frontend_components/Gantt.vue'
import testData from '../fixtures/Gantt.js'
import apiData from '../fixtures/full-data.js'

function createContainerElement() {
    const container = document.createElement('div')
    container.id = 'gantt-container'
    container.style.width = '1500px'
    container.style.height = '800px'
    document.body.appendChild(container)
    return container
}

describe('Gantt.vue', () => {
    let axiosGetStub

    before(function () {
        axiosGetStub = sinon.stub(axios, 'get')
        Vue.prototype.$http = axios
    })

    after(function () {
        axios.get.restore()
    })

    it('should render initial state', () => {
        const loadDataStub = sinon.stub(Gantt.methods, 'loadData')

        const Constructor = Vue.extend(Gantt)
        const container = createContainerElement()
        const vm = new Constructor({
            propsData: testData.props,
        }).$mount(container)

        Gantt.methods.loadData.restore()

        expect(vm.$el.tagName).to.equal('DIV')
        expect(vm.$el.querySelectorAll('.toggle-switch').length).not.to.equal(0)
        expect(vm.$el.querySelectorAll('.datetime-controls').length).not.to.equal(0)
        expect(vm.$el.querySelectorAll('.unit-control').length).not.to.equal(0)
        expect(vm.$el.querySelectorAll('.page-control').length).not.to.equal(0)
        expect(vm.$el.querySelectorAll('.date-range-control').length).not.to.equal(0)
        expect(vm.$el.querySelectorAll('.timezone-control').length).not.to.equal(0)
        expect(vm.$el.querySelectorAll('.gantt-labels').length).not.to.equal(0)
        expect(vm.$el.querySelectorAll('.status-bars').length).not.to.equal(0)
        expect(vm.$el.querySelectorAll('.cover').length).not.to.equal(0)
        expect(vm.$el.querySelector('.cover').classList.contains('loading')).to.equal(true)
        expect(vm.$el.querySelectorAll('.edit-tools-toggle').length).not.to.equal(0)
    })

    it('should render gantt bars when api returns data', (done) => {
        axiosGetStub.resolves({
            data: apiData,
        })

        const Constructor = Vue.extend(Gantt)
        const container = createContainerElement()
        const vm = new Constructor({
            propsData: testData.props,
        }).$mount(container)

        setTimeout(() => {
            expect(vm.$el.querySelectorAll('#flight-assignment-table .gantt-bar').length).to.equal(apiData.assignments.length)
            expect(vm.$el.querySelectorAll('#flight-template-table .gantt-bar').length).to.equal(apiData.templates.length)
            done()
        }, 0)
    })

    it('should load revision and timezoneName from cookie if existing', () => {
        Cookies.set('gantt-timezone', 'pst')
        Cookies.set('gantt-revision', 2)

        const loadDataStub = sinon.stub(Gantt.methods, 'loadData')

        const Constructor = Vue.extend(Gantt)
        const container = createContainerElement()
        const vm = new Constructor({
            propsData: testData.props,
        }).$mount(container)

        Gantt.methods.loadData.restore()

        expect(vm.timezoneName).to.equal('pst')
        expect(vm.revision).to.equal(2)
    })

    it('should save revision and timezoneName to cookie when changed', (done) => {
        Cookies.set('gantt-timezone', 'utc')
        Cookies.set('gantt-revision', 1)

        const loadDataStub = sinon.stub(Gantt.methods, 'loadData')

        const Constructor = Vue.extend(Gantt)
        const container = createContainerElement()
        const vm = new Constructor({
            propsData: testData.props,
        }).$mount(container)

        Gantt.methods.loadData.restore()

        const changeEvent = document.createEvent('Events')
        changeEvent.initEvent('change', true, false)
        vm.$el.querySelector('#gantt-timezone').value = 'est'
        vm.$el.querySelector('#gantt-timezone').dispatchEvent(changeEvent)
        vm.$el.querySelector('#gantt-revision').value = 2
        vm.$el.querySelector('#gantt-revision').dispatchEvent(changeEvent)

        setTimeout(() => {
            expect(Cookies.get('gantt-timezone')).to.equal('est')
            expect(Cookies.get('gantt-revision')).to.equal('2')
            done()
        }, 0)
    })
})
