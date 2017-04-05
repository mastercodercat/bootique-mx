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
        this.initInteractables();
        this.loadData();
    } else {
        console.error('Invalid table element')
    }
}

/* helper functions */

function formatTo2Digits(number) {
    return (number < 10 ? '0' : '') + number;
}

function weekDayString(weekday) {
    var weekdays = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday'];
    return weekdays[weekday % 7];
}

function formatDate(date) {
    return formatTo2Digits(date.getMonth() + 1) + '/' +
        formatTo2Digits(date.getDate()) + '/' +
        formatTo2Digits(date.getFullYear())  + ' ' +
        formatTo2Digits(date.getHours())  + ':' +
        formatTo2Digits(date.getMinutes())  + ':' +
        formatTo2Digits(date.getSeconds());
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

function placeBar($tr, tdIndex, length, object) {
    /*
     * length := bar-width / td-width
     * object can be flight (from template table) or assignment (from assignment table)
     */
    var $bar = null;
    var date;
    var $td = $tr.children('td').eq(tdIndex + 1);   // Index should be increased by 1 because first td is line/tail name cell

    if ($td.length > 0) {
        if (object.number > 0) {
            $bar = $('.bar.prototype').clone().removeClass('prototype');
            $bar
                .css('width', $td.css('width').replace('px', '') * length);
            $bar
                .attr('data-td-index', tdIndex)
                .attr('data-number', object.number);
            $bar.find('.number').html(object.number);
            $bar.find('.org').html(object.origin);
            $bar.find('.dest').html(object.destination);
            date = new Date(object.departure_datetime);
            $bar.find('.departure').html(formatDate(date));
            date = new Date(object.arrival_datetime);
            $bar.find('.arrival').html(formatDate(date));

            $td.append($bar);
        } else {
            var status = object.status;
            if (status == 2) {
                $bar = $('.status-prototype[data-status="' + status + '"]').clone();
                placeStatusBar($bar, $td, length);
            }
        }
    }
    return $bar;
}

function placeStatusBar($bar, $td, length = 1) {
    $bar
        .removeClass('status-prototype')
        .css('width', $td.css('width').replace('px', '') * length)
        .css('height', $td.css('height').replace('px', ''));
    $td.append($bar);

    return $bar;
}

/* class methods */

RoutePlanningGantt.prototype.initInteractables = function() {
    var self = this;
    var assignmentTableId = self.options.flightAssignmentTable.attr('id');
    var assignmentTableTrSelector = '#' + assignmentTableId + ' tr:not(.head)';
    var ganttTableBarSelector = '.gantt-table tr:not(.head) > td > .bar';
    var statusBarPrototypeSelector = '.status-bars .bar';
    var draggables = [ganttTableBarSelector, statusBarPrototypeSelector];
    var removeAreaSelector = '#drop-to-remove-area';

    // Template, assignment table bar, status bar draggable

    draggables.forEach(function(draggableSelector) {
        interact(draggableSelector).draggable({
            autoScroll: true,
            onstart: function(event) {
                var $bar = $(event.target),
                    $barClone = $bar.clone().addClass('drag-clone');
                $barClone.appendTo($bar.parent());
            },
            onmove: function dragMoveListener(event) {
                var $bar = $(event.target).siblings('.drag-clone'),
                    x = (parseFloat($bar.attr('data-x')) || 0) + event.dx,
                    y = (parseFloat($bar.attr('data-y')) || 0) + event.dy;

                $bar.css('transform', 'translate(' + x + 'px, ' + y + 'px)')
                    .attr('data-x', x)
                    .attr('data-y', y)
                    .addClass('dragging');
            },
            onend: function (event) {
                var $bar = $(event.target).siblings('.drag-clone');

                $bar.remove();
            },
        });
    });

    // Drop into assignment table row (only accept bars from template table)

    interact(assignmentTableTrSelector).dropzone({
        accept: ganttTableBarSelector,
        ondragenter: function (event) {
            var $bar = $(event.relatedTarget),
                $tr = $(event.target),
                tdIndex = $bar.data('td-index'),
                $td = $tr.children('td').eq(tdIndex + 1);

            $td.addClass('dragging-over');
        },
        ondragleave: function (event) {
            var $bar = $(event.relatedTarget),
                $tr = $(event.target),
                tdIndex = $bar.data('td-index'),
                $td = $tr.children('td').eq(tdIndex + 1);

            $td.removeClass('dragging-over');
        },
        ondrop: function (event) {
            var $bar = $(event.relatedTarget),
                $tr = $(event.target),
                tdIndex = $bar.data('td-index'),
                $td = $tr.children('td').eq(tdIndex + 1),
                tailNumber = $tr.data('tail-number');

            $td.removeClass('dragging-over');

            if ($bar.data('assignment-id')) {
                var assignmentId = $bar.data('assignment-id');

                self.moveAssignment(assignmentId, tailNumber)
                    .then(function(response) {
                        if (response.success) {
                            $bar.appendTo($td);
                        }
                    });

            } else {
                var flightId = $bar.data('flight-id');

                self.assignFlight(flightId, tailNumber)
                    .then(function(response) {
                        if (response.success) {
                            var $newBar = $bar.clone().attr('enabled', true);
                            $newBar.attr('data-assignment-id', response.id);
                            $td.append($newBar);
                            $bar
                                .addClass('assigned')
                                .attr('enabled', false);
                        }
                    });
            }
        },
    });

    // Drop into assignment table cell (status bar placement, status assignment move)

    interact(assignmentTableTrSelector + ' td').dropzone({
        accept: assignmentTableTrSelector + ' .bar[data-status], ' + statusBarPrototypeSelector,
        ondragenter: function (event) {
            var $bar = $(event.relatedTarget),
                $td = $(event.target);

            $td.addClass('dragging-over');
        },
        ondragleave: function (event) {
            var $bar = $(event.relatedTarget),
                $td = $(event.target);

            $td.removeClass('dragging-over');
        },
        ondrop: function (event) {
            var $bar = $(event.relatedTarget);

            if ($bar.data('assignment-id')) {
                var assignmentId = $bar.data('assignment-id'),
                    $td = $(event.target),
                    $tr = $td.closest('tr'),
                    tdIndex = $td.index();
                    tailNumber = $tr.data('tail-number');

                var startTime = new Date(self.options.startDate);
                startTime.setSeconds(startTime.getSeconds() + self.options.unit * (tdIndex - 1));

                self.moveAssignment(assignmentId, tailNumber, startTime)
                    .then(function(response) {
                        if (response.success) {
                            $bar.appendTo($td);
                        }
                    });
            } else if ($bar.data('status') > 0) {
                var $td = $(event.target),
                    $tr = $td.closest('tr'),
                    tailNumber = $tr.data('tail-number'),
                    tdIndex = $td.index();

                $td.removeClass('dragging-over');

                var startTime = new Date(self.options.startDate);
                startTime.setSeconds(startTime.getSeconds() + self.options.unit * (tdIndex - 1));
                var endTime = new Date(startTime.getTime() + 3600000);

                self.assignStatus(tailNumber, $bar.data('status'), startTime, endTime)
                    .then(function(response) {
                        if (response.success) {
                            var $newBar = $bar.clone();
                            placeStatusBar($newBar, $td, 3600 / self.options.unit);
                            $newBar.attr('data-assignment-id', response.id);
                        }
                    });
            }
        },
    });

    // Drop into Remove area

    interact(removeAreaSelector).dropzone({
        accept: assignmentTableTrSelector + ' .bar',
        ondragenter: function (event) {
            $(event.target).addClass('dragging-over');
        },
        ondragleave: function (event) {
            $(event.target).removeClass('dragging-over');
        },
        ondrop: function (event) {
            var $bar = $(event.relatedTarget);

            $(event.target).removeClass('dragging-over');

            if ($bar.data('assignment-id')) {
                var assignmentId = $bar.data('assignment-id');
                self.removeAssignment(assignmentId)
                    .then(function(response) {
                        if (response.success) {
                            $bar.remove();
                        }
                    });
            }
        },
    });
}

RoutePlanningGantt.prototype.checkIfAssigned = function(flightNumber, departureDateTime) {
    var assignmentCount = this.assignments.length;
    for (var i = 0; i < assignmentCount; i++) {
        if (this.assignments[i].number == flightNumber) {
            if (new Date(this.assignments[i].start_time).getTime() == departureDateTime.getTime()) {
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
            if (!(template.number in self.templates)) {
                self.templates[template.number] = []
            }
            self.templates[template.number].push(template);
        });

        data.assignments.forEach(function(assignment) {
            self.assignments.push(assignment);
        });

        self.refreshTemplateTable();
        self.refreshAssignmentTable();

        $('.cover').removeClass('loading');
    });
}

RoutePlanningGantt.prototype.refreshTemplateTable = function() {
    var self = this;
    var templates, template, length, tdIndex, tdPos;
    var $bar;
    var departureDateTime, arrivalDateTime;

    for (var flightNumber in self.templates) {
        templates = self.templates[flightNumber];
        for(var index in templates) {
            template = templates[index];
            arrivalDateTime = new Date(template.arrival_datetime);
            departureDateTime = new Date(template.departure_datetime);
            length = (arrivalDateTime - departureDateTime) / 1000 / self.options.unit;

            var date = new Date(self.options.startDate.getTime());
            var $tr = self.options.flightTemplateTable.find('tr[data-line=' + template.line_id + ']');
            tdIndex = getTdIndex(self, departureDateTime);
            tdPos = getTdPosition(self, departureDateTime);
            $bar = placeBar($tr, tdIndex, length, template);
            if ($bar) {
                $bar
                    .attr('data-departure-time', departureDateTime.toISOString())
                    .attr('data-flight-id', template.id)
                    .css('left', tdPos * 100 + '%');
                if (self.checkIfAssigned(template.number, departureDateTime)) {
                    $bar.addClass('assigned');
                } else {
                    $bar.attr('enabled', true);
                }
            }
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
                .css('left', tdPos * 100 + '%')
                .attr('data-assignment-id', assignment.id)
                .attr('enabled', true);
        }
    }
}

RoutePlanningGantt.prototype.assignFlight = function(flightId, tailNumber) {
    var self = this;

    if (!self.options.assignFlightAPIUrl) {
        console.error('Assign flight API URL not configured');
        return;
    }

    return $.ajax({
        method: 'POST',
        url: self.options.assignFlightAPIUrl,
        data: {
            csrfmiddlewaretoken: self.options.csrfToken,
            flight_id: flightId,
            tail: tailNumber,
        },
    });
}

RoutePlanningGantt.prototype.assignStatus = function(tailNumber, status, startTime, endTime) {
    var self = this;

    if (!self.options.assignStatusAPIUrl) {
        console.error('Assign status API URL not configured');
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

RoutePlanningGantt.prototype.removeAssignment = function(assignmentId) {
    var self = this;

    if (!self.options.removeAssignmentAPIUrl) {
        console.error('Remove assignment API URL not configured');
        return;
    }

    return $.ajax({
        method: 'POST',
        url: self.options.removeAssignmentAPIUrl,
        data: {
            csrfmiddlewaretoken: self.options.csrfToken,
            assignment_id: assignmentId,
        },
    });
}

RoutePlanningGantt.prototype.moveAssignment = function(assignmentId, tailNumber, startTime = null) {
    var self = this;

    if (!self.options.moveAssignmentAPIUrl) {
        console.error('Move assignment API URL not configured');
        return;
    }

    return $.ajax({
        method: 'POST',
        url: self.options.moveAssignmentAPIUrl,
        data: {
            csrfmiddlewaretoken: self.options.csrfToken,
            assignment_id: assignmentId,
            tail: tailNumber,
            start_time: startTime ? startTime.toISOString() : '',
        },
    });
}
