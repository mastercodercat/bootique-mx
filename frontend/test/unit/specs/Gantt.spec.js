import Vue from 'vue'
import sinon from 'sinon'
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
    it('should render initial state', () => {
        const container = createContainerElement()
        Gantt.methods.loadData = e => e
        const Constructor = Vue.extend(Gantt)
        const vm = new Constructor({
            propsData: testData.props,
        }).$mount(container)

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
})
