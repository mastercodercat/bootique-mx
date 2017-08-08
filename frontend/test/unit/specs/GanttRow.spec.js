import Vue from 'vue'
import GanttRow from '@frontend_components/GanttRow.vue'
import testData from '../fixtures/full-data.js'

const tail = {
    id: 17,
    number: "N719PC",
}

function getTailAssignments() {
    const assignments = []
    for (const index in testData.assignments) {
        const assignment = testData.assignments[index]
        if (assignment.tail == tail.number) {
            assignments.push(assignment)
        }
    }
    return assignments
}

const assignments = getTailAssignments()

describe('GanttRow.vue', () => {
    it('should render correct contents', () => {
        const Constructor = Vue.extend(GanttRow)
        const vm = new Constructor({
            propsData: {
                startDate: testData.startDate,
                timezone: -7,
                objects: assignments,
                shadows: [],
                unit: 3600,
                dragging: false,
                editing: true,
                writable: true,
                selectedIds: {
                    [assignments[0].id]: true,
                    [assignments[1].id]: true,
                    [assignments[2].id]: true,
                },
                assignedIds: {
                    [assignments[3].id]: true,
                    [assignments[4].id]: true,
                },
            }
        }).$mount()

        expect(vm.$el.classList.contains('row-line')).to.equal(true)
        expect(vm.$el.querySelectorAll('.gantt-bar').length).to.equal(assignments.length)
        expect(vm.$el.querySelectorAll('.selected').length).to.equal(3)
        expect(vm.$el.querySelectorAll('.assigned').length).to.equal(2)
    })
})
