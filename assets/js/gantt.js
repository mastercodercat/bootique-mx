"use strict";

/*
 * Route planning gantt class
 *
 * options:
 *  loadDataAPIUrl, assignFlightAPIUrl, startDate, endDate, flightAssignmentTable, flightTemplateTable, unit(in seconds), csrfToken
 */
function RoutePlanningGantt(options) {
    this.mode = 1;
    this.templates = {};
    this.assignments = [];

    this.options = options;

    if (this.options.flightAssignmentTable
        && this.options.flightTemplateTable
        && this.options.startDate
        && this.options.endDate
    ) {
        this.bindEventHandlers();
        this.loadData();
    } else {
        console.error('Invalid table element')
    }
}

/* helper functions */

function format2Digits(number) {
    return (number < 10 ? '0' : '') + number;
}

function timeDiffInSeconds(time1, time2) {
    var date1 = new Date("2010-01-01T" + time1);
    var date2 = new Date("2010-01-01T" + time2);
    return (date1 - date2) / 1000;
}

function getTdIndex(self, date) {
    var diffFromStart = (date - self.options.startDate) / 1000;
    return Math.floor(diffFromStart / self.options.unit);
}

function getTdPosition(self, date) {
    var _date = new Date(date.getTime());
    _date.setMinutes(0);
    _date.setSeconds(0);
    var secondsDiff = (date - _date) / 1000;
    return parseFloat(parseInt(secondsDiff) % parseInt(self.options.unit)) / parseFloat(self.options.unit);
}

function replaceTimeInDate(date, timeString) {
    var _date = new Date(date.getTime());
    var times = timeString.split(':');
    _date.setHours(times[0]);
    _date.setMinutes(times[1]);
    _date.setSeconds(times[2]);
    return _date;
}

function placeBar($tr, tdIndex, length, flightNumber) {
    // length := bar-width / td-width
    var $bar = null;
    var $td = $tr.children('td').eq(tdIndex + 1);   // Index should be increased by 1 because first td is line/tail name cell
    if ($td.length > 0) {
        $bar = $('.bar.prototype').clone().removeClass('prototype');
        $bar
            .css('width', $td.css('width').replace('px', '') * length)
            .attr('data-td-index', tdIndex)
            .attr('data-number', flightNumber)
            .find('.number').html(flightNumber);

        $td.append($bar);
    }
    return $bar;
}

/* class methods */

RoutePlanningGantt.prototype.bindEventHandlers = function() {
    var self = this;
    var $body = $('body');
    var assignmentTableId = self.options.flightAssignmentTable.attr('id');
    var assignmentTableTrSelector = '#' + assignmentTableId + ' tr:not(.head)';
    var $prevDraggedTr;
    var $bar, $barPlaceholder;

    $body.on('dragstart', '.gantt-table tr:not(.head) > td > .bar', function(event) {
        $bar = $(event.target);
        $barPlaceholder = $(document.createElement('div'));
        $barPlaceholder.attr('id', 'bar-placeholder');
        $barPlaceholder
            .css('width', $bar.css('width'))
            .css('height', $bar.css('height'))
            .css('left', $bar.css('left'));
    });

    $body.on('dragenter', assignmentTableTrSelector, function(event) {
        event.preventDefault();
    });

    $body.on('dragover', assignmentTableTrSelector, function(event) {
        event.preventDefault();
        var tdIndex = $bar.data('td-index');
        var $tr = $(event.target).closest('tr');
        if (!$prevDraggedTr || $prevDraggedTr[0] !== $tr[0]) {
            var $td = $tr.children('td').eq(tdIndex);
            $barPlaceholder.appendTo($td);
            $prevDraggedTr = $tr;
        }
    });

    $body.on('drop', assignmentTableTrSelector, function(event) {
        event.preventDefault();
        var $tr = $(event.target).closest('tr');
        var flightNumber = $bar.data('number');
        var tailNumber = $tr.data('tail-number');
        var tdIndex = $bar.data('td-index');
        var departureTime = new Date($bar.data('departure-time'));

        self.assignFlight(flightNumber, tailNumber, departureTime)
            .then(function(response) {
                if (response.success) {
                    var $td = $tr.children('td').eq(tdIndex);
                    $td.append($bar.clone().attr('draggable', false));
                    $bar.addClass('assigned').attr('draggable', false);
                }
            });

        $barPlaceholder.remove();
        $barPlaceholder = null;
    });

    $body.on('dragend', function(event) {
        event.preventDefault();
        if ($barPlaceholder) {
            $barPlaceholder.remove();
        }
    });
}

RoutePlanningGantt.prototype.loadData = function() {
    var self = this;

    var startDate = this.options.startDate;
    var endDate = this.options.endDate;
    $.ajax({
        url: this.options.loadDataAPIUrl,
        method: 'GET',
        data: {
            startdate: startDate.getTime() / 1000,
            enddate: endDate.getTime() / 1000,
        },
    })
    .then(function(data) {
        data.templates.forEach(function(template) {
            self.templates[template.number] = template;
        });

        data.assignments.forEach(function(assignment) {
            self.assignments.push(assignment);
        });

        self.refreshTemplateTable();
        self.refreshAssignmentTable();
    });
}

RoutePlanningGantt.prototype.refreshTemplateTable = function() {
    var self = this;
    var template, length, tdIndex, tdPos;
    var $bar;

    for (var flightNumber in self.templates) {
        template = self.templates[flightNumber];
        length = timeDiffInSeconds(template.arrival_time, template.departure_time) / self.options.unit;

        var date = new Date(self.options.startDate.getTime());
        var $tr = self.options.flightTemplateTable.find('tr[data-line=' + template.line_id + ']');
        while (date <= self.options.endDate) {
            var weekday = (date.getDay() - 1) % 7;
            if (template.weekly_availability.substring(weekday, weekday + 1) == 'X') {
                var departureTime = replaceTimeInDate(date, template.departure_time);
                tdIndex = getTdIndex(self, departureTime);
                tdPos = getTdPosition(self, departureTime);
                $bar = placeBar($tr, tdIndex, length, template.number);
                if ($bar) {
                    $bar
                        .attr('data-departure-time', departureTime.toISOString())
                        .css('left', tdPos * 100 + '%')
                        .attr('draggable', true);
                }
            }

            date.setDate(date.getDate() + 1);
        }
    }
}

RoutePlanningGantt.prototype.refreshAssignmentTable = function() {
    var self = this;

    var asgnCount = self.assignments.length;
    for (var i = 0; i < asgnCount; i++) {
        var assignment = self.assignments[i];
        var $tr = self.options.flightAssignmentTable.find('tr[data-tail-number="' + assignment.tail + '"]');
        var startTime = new Date(assignment.start_time);
        var endTime = new Date(assignment.end_time);
        var tdIndex = parseInt((startTime - self.options.startDate) / 1000 / self.options.unit);
        var length = (endTime - startTime) / 1000 / self.options.unit;
        var tdPos = getTdPosition(self, startTime);
        var $bar = placeBar($tr, tdIndex, length, assignment.flight_number);
        if ($bar) {
            $bar
                .css('left', tdPos * 100 + '%');
        }
    }
}

RoutePlanningGantt.prototype.assignFlight = function(flightNumber, tailNumber, departureTime) {
    var self = this;

    if (!self.options.assignFlightAPIUrl) {
        console.error('Assign flight api URL not configured');
        return;
    }

    return $.ajax({
        method: 'POST',
        url: self.options.assignFlightAPIUrl,
        data: {
            csrfmiddlewaretoken: self.options.csrfToken,
            flight_number: flightNumber,
            tail: tailNumber,
            departure_time: departureTime.toISOString(),
        },
    });
}
