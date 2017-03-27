function RoutePlanningGantt($flightAssignmentTable, $flightTemplateTable, loadDataAPIUrl) {
    this.mode = 1;
    this.startDate = new Date();
    this.tails = {};
    this.lines = {};
    this.loadDataAPIUrl = loadDataAPIUrl;

    if ($flightAssignmentTable && $flightTemplateTable) {
        this.$flightAssignmentTable = $flightAssignmentTable;
        this.$flightTemplateTable = $flightTemplateTable;

        this.loadData();
    } else {
        console.error('Invalid table element')
    }
}

RoutePlanningGantt.prototype.loadData = function() {
    var self = this;

    var startDate = new Date('2017/03/06 00:00:00');
    var endDate = new Date('2017/03/06 23:59:59');
    $.ajax({
        url: this.loadDataAPIUrl,
        method: 'GET',
        data: {
            startdate: startDate.getTime() / 1000,
            enddate: endDate.getTime() / 1000,
        },
    })
    .then(function(response) {
        console.log(response);
    });
}
