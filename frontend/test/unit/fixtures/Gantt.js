const lines = [
    {
        id: 12,
        name: "ATL/BNA",
    },
    {
        id: 7,
        name: "DEN/ALS",
    },
    {
        id: 4,
        name: "DEN/CDR",
    },
    {
        id: 11,
        name: "DEN/CEZ",
    },
    {
        id: 9,
        name: "DEN/VEL",
    },
    {
        id: 8,
        name: "DFW/CVN",
    },
    {
        id: 3,
        name: "DFW/GLH",
    },
    {
        id: 6,
        name: "DFW/SVC",
    },
    {
        id: 1,
        name: "LAX/MCE",
    },
    {
        id: 2,
        name: "MSP/TVF",
    },
    {
        id: 5,
        name: "PDX/PDT",
    },
    {
        id: 10,
        name: "PHX/ABQ",
    },
];

const tails = [
    {
        id: 1,
        number: "N455BC",
    },
    {
        id: 2,
        number: "N165TG",
    },
    {
        id: 3,
        number: "N166TG",
    },
    {
        id: 4,
        number: "N253AS",
    },
    {
        id: 5,
        number: "N300XX",
    },
    {
        id: 6,
        number: "N451SS",
    },
    {
        id: 7,
        number: "N471SS",
    },
    {
        id: 8,
        number: "N472SS",
    },
    {
        id: 9,
        number: "N474SS",
    },
    {
        id: 10,
        number: "N475SS",
    },
    {
        id: 11,
        number: "N476SS",
    },
    {
        id: 12,
        number: "N477SS",
    },
    {
        id: 13,
        number: "N512NG",
    },
    {
        id: 14,
        number: "N584JV",
    },
    {
        id: 15,
        number: "N645PC",
    },
    {
        id: 16,
        number: "N670WH",
    },
    {
        id: 17,
        number: "N719PC",
    },
    {
        id: 18,
        number: "N723ST",
    },
    {
        id: 19,
        number: "N776JT",
    },
    {
        id: 20,
        number: "N842WF",
    },
    {
        id: 21,
        number: "N95GE",
    },
    {
        id: 22,
        number: "N55NX",
    },
    {
        id: 23,
        number: "N74KS",
    },
    {
        id: 24,
        number: "N111WG",
    },
    
];

const initialRevisions = [
    {
        id: 2,
        published_datetime: "2017-07-11T11:10:55.218759-07:00",
        has_draft: true,
    },
    {
        id: 1,
        published_datetime: "2017-07-11T09:39:55.366701-07:00",
        has_draft: false,
    },
    
];

export default {
    lines,
    tails,
    initialRevisions,
    props: {
        lines: lines,
        tails: tails,
        initialRevisions: initialRevisions,
        ganttUrl: "/routeplanning/",
        addTailUrl: "/routeplanning/tail/add",
        addLineUrl: "/routeplanning/line/add",
        editLineUrl: "/routeplanning/line/0",
        loadDataAPIUrl: "/routeplanning/api/loaddata",
        assignFlightAPIUrl: "/routeplanning/api/tail/assignflight",
        assignStatusAPIUrl: "/routeplanning/api/tail/assignstatus",
        moveAssignmentAPIUrl: "/routeplanning/api/assignment/move",
        removeAssignmentAPIUrl: "/routeplanning/api/assignment/remove",
        resizeAssignmentAPIUrl: "/routeplanning/api/assignment/resize",
        publishRevisionAPIUrl: "/routeplanning/api/revision/publish",
        clearRevisionAPIUrl: "/routeplanning/api/revision/clear",
        deleteRevisionAPIUrl: "/routeplanning/api/revision/delete",
        days: 1,
        hours: 24,
        unit: 3600,
        writable: true,
        mode: 4,
        startTmstmp: 1492646400,
        prevStartTmstmp: 1491436800,
        nextStartTmstmp: 1493856000,
        bigUnits: 14,
        smallUnits: 336,
        windowAtEnd: 0,
        startParamExists: false,
        endParamExists: false,
    },
}
