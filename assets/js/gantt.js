"use strict";

/*
 * Route planning gantt class
 *
 * options:
 *  loadDataAPIUrl, assignFlightAPIUrl, assignStatusAPIUrl, startDate, endDate,
 *  flightAssignmentTable, flightTemplateTable, unit(in seconds), csrfToken
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

function formatTo2Digits(number) {
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
    var _dateString = date.getUTCFullYear() + '-' + formatTo2Digits(date.getUTCMonth() + 1) + '-' + formatTo2Digits(date.getUTCDate());
    _dateString += 'T';
    _dateString += timeString;
    _dateString += 'Z';
    return new Date(_dateString);
}

function placeBar($tr, tdIndex, length, object) {
    /*
     * length := bar-width / td-width
     * object can be flight (from template table) or assignment (from assignment table)
     */
    var $bar = null;
    var date;
    var $td = $tr.children('td').eq(tdIndex + 1);   // Index should be increased by 1 because first td is line/tail name cell

    if ($td.length > 0) {
        $bar = $('.bar.prototype').clone().removeClass('prototype');
        $bar
            .css('width', $td.css('width').replace('px', '') * length);

        if (object.number > 0) {
            $bar
                .attr('data-td-index', tdIndex)
                .attr('data-number', object.number);
            $bar.find('.number').html(object.number);
            $bar.find('.org').html(object.origin);
            $bar.find('.dest').html(object.destination);
            date = replaceTimeInDate(new Date(), object.departure_time);
            $bar.find('.departure').html(formatTo2Digits(date.getHours()) + ':' + formatTo2Digits(date.getMinutes()) + ':' + formatTo2Digits(date.getSeconds()));
            date = replaceTimeInDate(new Date(), object.arrival_time);
            $bar.find('.arrival').html(formatTo2Digits(date.getHours()) + ':' + formatTo2Digits(date.getMinutes()) + ':' + formatTo2Digits(date.getSeconds()));
        } else {
            var status = object.status;
            if (status == 2) {
                $bar.addClass('maintenance').html('Maintenance');
            }
        }

        $td.append($bar);
    }
    return $bar;
}

function placeStatusBar($bar, $td) {
    $bar
        .css('width', $td.css('width').replace('px', ''));
    $td.append($bar);

    return $bar;
}

/* class methods */

RoutePlanningGantt.prototype.bindEventHandlers = function() {
    var self = this;
    var $body = $('body');
    var assignmentTableId = self.options.flightAssignmentTable.attr('id');
    var assignmentTableTrSelector = '#' + assignmentTableId + ' tr:not(.head)';
    var $prevDraggedTr, $prevDraggedTd;
    var $bar;

    $body.on('dragstart', '.gantt-table tr:not(.head) > td > .bar, .status-bars > .bar', function(event) {
        $bar = $(event.target);
    });
    // $body.on('dragstart', '.status-bars > .bar', function(event) {
    //     $bar = $(event.target);
    // });

    $body.on('dragenter', assignmentTableTrSelector, function(event) {
        event.preventDefault();
    });

    $body.on('dragover', assignmentTableTrSelector, function(event) {
        event.preventDefault();
        if ($bar.data('status') > 0) {
            var $td = $(event.target);
            if ($td.prop('tagName').toLowerCase() != 'td') {
                $td = $td.closest('td');
            }
            if (!$prevDraggedTd || $prevDraggedTd[0] !== $td[0]) {
                if ($prevDraggedTd) {
                    $prevDraggedTd.removeClass('dragging-over');
                }
                $td.addClass('dragging-over');
                $prevDraggedTd = $td;
            }
        } else {
            var tdIndex = $bar.data('td-index');
            var $tr = $(event.target).closest('tr');
            if (!$prevDraggedTr || $prevDraggedTr[0] !== $tr[0]) {
                var $td = $tr.children('td').eq(tdIndex + 1);
                if ($prevDraggedTd) {
                    $prevDraggedTd.removeClass('dragging-over');
                }
                $td.addClass('dragging-over');
                $prevDraggedTd = $td;
                $prevDraggedTr = $tr;
            }
        }
    });

    $body.on('drop', assignmentTableTrSelector, function(event) {
        event.preventDefault();
        var $tr = $(event.target).closest('tr');
        var tailNumber = $tr.data('tail-number');

        if ($bar.data('status') > 0) {
            var $td = $(event.target);
            if ($td.prop('tagName').toLowerCase() != 'td') {
                return;
            }
            var tdIndex = $td.index();
            var startTime = new Date(self.options.startDate);
            startTime.setSeconds(startTime.getSeconds() + self.options.unit * (tdIndex - 1));
            var endTime = new Date(startTime.getTime() + 3600000);
            self.assignStatus(tailNumber, $bar.data('status'), startTime, endTime)
                .then(function(response) {
                    if (response.success) {
                        var $newBar = $bar.clone();
                        placeStatusBar($newBar, $td);
                    }
                });
        } else {
            var flightNumber = $bar.data('number');
            var tdIndex = $bar.data('td-index');
            var departureTime = new Date($bar.data('departure-time'));

            self.assignFlight(flightNumber, tailNumber, departureTime)
                .then(function(response) {
                    if (response.success) {
                        var $td = $tr.children('td').eq(tdIndex + 1);
                        $td.append($bar.clone().attr('draggable', false));
                        $bar.addClass('assigned').attr('draggable', false);
                    }
                });
        }

        if ($prevDraggedTd) {
            $prevDraggedTd.removeClass('dragging-over');
            $prevDraggedTd = null;
        }
    });

    $body.on('dragend', function(event) {
        event.preventDefault();
        if ($prevDraggedTd) {
            $prevDraggedTd.removeClass('dragging-over');
            $prevDraggedTd = null;
        }
    });
}

RoutePlanningGantt.prototype.checkIfAssigned = function(flightNumber, departureTime) {
    var assignmentCount = this.assignments.length;
    for (var i = 0; i < assignmentCount; i++) {
        if (this.assignments[i].number == flightNumber) {
            if (new Date(this.assignments[i].start_time).getTime() == departureTime.getTime()) {
                return true;
            }
        }
    }
    return false;
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
                if (departureTime < date) {
                    departureTime.setDate(departureTime.getDate() + 1);
                }
                tdIndex = getTdIndex(self, departureTime);
                tdPos = getTdPosition(self, departureTime);
                $bar = placeBar($tr, tdIndex, length, template);
                if ($bar) {
                    $bar
                        .attr('data-departure-time', departureTime.toISOString())
                        .css('left', tdPos * 100 + '%');
                    if (self.checkIfAssigned(template.number, departureTime)) {
                        $bar.addClass('assigned');
                    } else {
                        $bar.attr('draggable', true);
                    }
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
        var $bar = placeBar($tr, tdIndex, length, assignment);
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

RoutePlanningGantt.prototype.assignStatus = function(tailNumber, status, startTime, endTime) {
    var self = this;

    if (!self.options.assignStatusAPIUrl) {
        console.error('Assign status api URL not configured');
        return;
    }

    return $.ajax({
        method: 'POST',
        url: self.options.assignStatusAPIUrl,
        data: {
            csrfmiddlewaretoken: self.options.csrfToken,
            tail: tailNumber,
            status: status,
            start_time: startTime.toISOString(),
            end_time: endTime.toISOString(),
        },
    });
}
