"use strict";

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

/*
 * Route planning gantt class
 *
 * options:
 *  [api urls], startDate, endDate,
 *  flightAssignmentTable, flightTemplateTable, unit(in seconds), tablesWrapperSelector,
 *  csrfToken
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
        if (!this.options.readOnly) {
            this.initInteractables();
        }
        this.displayNowIndicator(this.options.flightAssignmentTable);
        this.displayNowIndicator(this.options.flightTemplateTable);
        this.loadData();
    } else {
        console.error('Invalid table element')
    }
}

/* class methods */

RoutePlanningGantt.prototype.getTdWidth = function($td) {
    return parseFloat($td.css('width').replace('px', ''));
}

RoutePlanningGantt.prototype.getTdIndex = function(date) {
    var self = this;

    var diffFromStart = (date - self.options.startDate) / 1000;
    var index = parseInt(diffFromStart / self.options.unit);
    return index > 0 ? index : 0;
}

RoutePlanningGantt.prototype.getTdPosition = function(date) {
    var self = this;

    var secondsDiff = parseInt((date - self.options.startDate) / 1000);
    var unit = parseInt(self.options.unit);
    var signalModifier = secondsDiff >= 0 ? 0 : -1;
    return parseFloat(secondsDiff % unit + signalModifier * unit) / parseFloat(self.options.unit);
}

RoutePlanningGantt.prototype.placeBar = function($tr, tdIndex, length, object) {
    /*
     * length := bar-width / td-width
     * object can be flight (from template table) or assignment (from assignment table)
     */
    var self = this;
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
            $bar = $('.status-prototype[data-status="' + status + '"]').clone();
            self.placeStatusBar($bar, $td, length, object);
        }
    }
    return $bar;
}

RoutePlanningGantt.prototype.setStatusBarInfo = function($bar, object) {
    var $info = $bar.find('.info');
    date = new Date(object.start_time);
    $info.find('.start').html(formatDate(date));
    date = new Date(object.end_time);
    $info.find('.end').html(formatDate(date));
}

RoutePlanningGantt.prototype.placeStatusBar = function($bar, $td, length, object) {
    var self = this;
    var tdPos = self.getTdPosition(new Date(object.start_time));

    $bar
        .removeClass('status-prototype')
        .css('left', tdPos * 100 + '%')
        .css('width', $td.css('width').replace('px', '') * length)
        .css('height', $td.css('height').replace('px', ''));

    self.setStatusBarInfo($bar, object);

    $td.append($bar);

    return $bar;
}

RoutePlanningGantt.prototype.displayNowIndicator = function($table) {
    var self = this;
    var now = new Date();
    if (now >= self.options.startDate && now <= self.options.endDate) {
        var firstColumnWidth = parseFloat($table.find('td:first-child').css('width').replace('px', ''));
        var normalCellWidth = parseFloat($table.find('tr:not(.head) td:nth-child(3)').css('width').replace('px', ''));
        var left = firstColumnWidth + normalCellWidth * (now - self.options.startDate) / 1000 / self.options.unit;
        $table.closest('.table-wrapper').find('.now-indicator').css('left', left).removeClass('hidden');
    }
}

RoutePlanningGantt.prototype.initInteractables = function() {
    var self = this;
    var assignmentTableId = self.options.flightAssignmentTable.attr('id');
    var assignmentTableTrSelector = '#' + assignmentTableId + ' tr:not(.head)';
    var ganttTableBarSelector = '.gantt-table tr:not(.head) > td > .bar:not(.assigned)';
    var statusBarPrototypeSelector = '.status-bars .bar';
    var draggables = [ganttTableBarSelector, statusBarPrototypeSelector];
    var removeAreaSelector = '#drop-to-remove-area';

    // Resizeable status assignment bar

    interact(assignmentTableTrSelector + ' .bar[data-status]').resizable({
        edges: { left: true, right: true }
    })
    .on('resizestart', function(event) {
        var $bar = $(event.target);

        $bar.attr('data-org-width', $bar.width())
            .addClass('resizing');
    })
    .on('resizemove', function(event) {
        var $bar = $(event.target);
        var resizeUnit = parseFloat(self.getTdWidth($bar.closest('td')) * 300 / self.options.unit);  // Resize unit will be per 5 mins

        var ow = parseFloat($bar.attr('data-org-width'));
        var w = Math.round(parseFloat(event.rect.width) / resizeUnit) * resizeUnit;
        var dw = w - ow;
        var tx = event.deltaRect.left != 0 ? ow - w : 0;
        var pos = event.deltaRect.left != 0 ? 'start' : 'end';

        $bar.css('width', w)
            .css('transform', 'translateX(' + tx + 'px)')
            .attr('data-dw', dw)
            .attr('data-pos', pos);
    })
    .on('resizeend', function(event) {
        var $bar = $(event.target);
        var dw = $bar.attr('data-dw');
        var pos = $bar.attr('data-pos');

        var dt = parseFloat(dw) / self.getTdWidth($bar.closest('td')) * self.options.unit;
        var assignmentId = $bar.data('assignment-id');
        if (!assignmentId) {
            console.log('No assignment Id on resizing status bar');
            $bar.css('width', $bar.attr('data-org-width'))
                .css('transform', 'none')
                .attr('data-dw', '')
                .attr('data-pos', '');
            return;
        }

        $bar.removeClass('resizing');

        self.resizeAssignment(assignmentId, pos, dt)
        .then(
            function(response) {
                $bar.css('width', $bar.attr('data-org-width'))
                    .css('transform', 'none')
                    .attr('data-dw', '')
                    .attr('data-pos', '');

                if (response.success) {
                    var startTime = new Date(response.start_time);
                    var endTime = new Date(response.end_time);
                    var tdIndex = self.getTdIndex(startTime);

                    self.placeStatusBar(
                        $bar,
                        $bar.closest('tr').children('td').eq(tdIndex + 1),
                        (endTime - startTime) / 1000 / self.options.unit,
                        response
                    );
                }
            },
            function() {
                $bar.css('width', $bar.attr('data-org-width'))
                    .css('transform', 'none')
                    .attr('data-dw', '')
                    .attr('data-pos', '');
            }
        );
    });

    // Template, assignment table bar, status bar draggable

    draggables.forEach(function(draggableSelector) {
        interact(draggableSelector).draggable({
            autoScroll: true,
            onstart: function(event) {
                var $bar = $(event.target);
                if ($bar.hasClass('selected')) {
                    var $selected = $bar.closest('.gantt-table').find('.bar.selected');
                } else {
                    var $selected = $bar;
                }
                $selected.each(function() {
                    var $selectedBar = $(this);
                    var $barClone = $selectedBar.clone().addClass('drag-clone').removeClass('selected');
                    $barClone.addClass('dragging').insertAfter($selectedBar);
                });
            },
            onmove: function dragMoveListener(event) {
                var $bar = $(event.target);
                if ($bar.hasClass('selected')) {
                    var $selected = $bar.closest('.gantt-table').find('.bar.selected');
                } else {
                    var $selected = $bar;
                }
                $selected.each(function() {
                    var $selectedBar = $(this);
                    var $bar = $selectedBar.next('.drag-clone');
                    var x = (parseFloat($bar.attr('data-x')) || 0) + event.dx;
                    var y = (parseFloat($bar.attr('data-y')) || 0) + event.dy;

                    $bar.css('transform', 'translate(' + x + 'px, ' + y + 'px)')
                        .attr('data-x', x)
                        .attr('data-y', y);
                });
            },
            onend: function (event) {
                var $bar = $(event.target);
                if ($bar.hasClass('selected')) {
                    var $selected = $bar.closest('.gantt-table').find('.bar.selected');
                } else {
                    var $selected = $bar;
                }
                $selected.each(function() {
                    var $selectedBar = $(this);
                    $selectedBar.removeClass('selected').next('.drag-clone').remove();
                });
            },
        });
    });

    // Drop into assignment table row (only accept bars from template table)

    interact(assignmentTableTrSelector).dropzone({
        accept: ganttTableBarSelector,
        ondragenter: function (event) {
            var $bar = $(event.relatedTarget);
            var $hoveringTr = $(event.target);
            var hoveringTrIndex = parseInt($hoveringTr.data('index'));
            var primaryTrIndex = parseInt($bar.closest('tr').data('index'));

            if ($bar.hasClass('selected')) {
                var $selected = $bar.closest('.gantt-table').find('.bar.selected');
            } else {
                var $selected = $bar;
            }

            $selected.each(function() {
                var $selectedBar = $(this);
                var originalTrIndex = parseInt($selectedBar.closest('tr').data('index'));
                if (primaryTrIndex == originalTrIndex) {
                    var $tr = $hoveringTr;
                } else {
                    var newTrIndex = hoveringTrIndex - primaryTrIndex + originalTrIndex;
                    var $tr = $hoveringTr.siblings('tr[data-index="' + newTrIndex + '"]');
                }
                if ($tr.length > 0) {
                    var tdIndex = $selectedBar.data('td-index');
                    var $td = $tr.children('td').eq(tdIndex + 1);

                    $td.addClass('dragging-over');
                }
            });
        },
        ondragleave: function (event) {
            var $bar = $(event.relatedTarget);
            var $hoveringTr = $(event.target);
            var hoveringTrIndex = parseInt($hoveringTr.data('index'));
            var primaryTrIndex = parseInt($bar.closest('tr').data('index'));

            if ($bar.hasClass('selected')) {
                var $selected = $bar.closest('.gantt-table').find('.bar.selected');
            } else {
                var $selected = $bar;
            }

            $selected.each(function() {
                var $selectedBar = $(this);
                var originalTrIndex = parseInt($selectedBar.closest('tr').data('index'));
                if (primaryTrIndex == originalTrIndex) {
                    var $tr = $hoveringTr;
                } else {
                    var newTrIndex = hoveringTrIndex - primaryTrIndex + originalTrIndex;
                    var $tr = $hoveringTr.siblings('tr[data-index="' + newTrIndex + '"]');
                }
                if ($tr.length > 0) {
                    var tdIndex = $selectedBar.data('td-index');
                    var $td = $tr.children('td').eq(tdIndex + 1);

                    $td.removeClass('dragging-over');
                }
            });
        },
        ondrop: function (event) {
            var $bar = $(event.relatedTarget);
            var $hoveringTr = $(event.target);
            var hoveringTrIndex = parseInt($hoveringTr.data('index'));
            var primaryTrIndex = parseInt($bar.closest('tr').data('index'));

            if ($bar.hasClass('selected')) {
                var $selected = $bar.closest('.gantt-table').find('.bar.selected');
            } else {
                var $selected = $bar;
            }

            var assignmentData = [];
            var elementMoveData = [];
            var assigning = true;

            $selected.each(function() {
                var $selectedBar = $(this);
                var originalTrIndex = parseInt($selectedBar.closest('tr').data('index'));
                if (primaryTrIndex == originalTrIndex) {
                    var $tr = $hoveringTr;
                } else {
                    var newTrIndex = hoveringTrIndex - primaryTrIndex + originalTrIndex;
                    var $tr = $hoveringTr.siblings('tr[data-index="' + newTrIndex + '"]');
                }
                if ($tr.length > 0) {
                    var tdIndex = $selectedBar.data('td-index');
                    var $td = $tr.children('td').eq(tdIndex + 1);
                    var tailNumber = $tr.data('tail-number');

                    $td.removeClass('dragging-over');

                    if ($selectedBar.data('assignment-id')) {
                        var assignmentId = $selectedBar.data('assignment-id');
                        assigning = false;
                        assignmentData.push({
                            assignment_id: assignmentId,
                            tail: tailNumber,
                        });
                        elementMoveData.push({
                            assignmentId: assignmentId,
                            bar: $selectedBar,
                            td: $td,
                        });
                    } else {
                        var flightId = $selectedBar.data('flight-id');
                        assignmentData.push({
                            flight: flightId,
                            tail: tailNumber,
                        });
                        elementMoveData.push({
                            flightId: flightId,
                            bar: $selectedBar,
                            td: $td,
                        });
                    }
                }
            });

            if (assigning) {
                self.assignFlight(assignmentData)
                    .then(function(elementMoveData, response) {
                        if (response.success) {
                            var assignedFlights = response.assigned_flights; /* { flightId: assignmentId, ... } */
                            elementMoveData.forEach(function(data) {
                                if (data.flightId in assignedFlights) {
                                    var $newBar = data.bar.clone().attr('enabled', true);
                                    $newBar.attr('data-assignment-id', assignedFlights[data.flightId]);
                                    data.td.append($newBar);
                                    data.bar.addClass('assigned')
                                        .attr('enabled', false);
                                }
                            });
                        }
                    }.bind(this, elementMoveData));
            } else {
                self.moveAssignment(assignmentData)
                    .then(function(elementMoveData, response) {
                        if (response.success) {
                            var assignments = response.assignments; /* { assignment_id: { start_time, end_time }, ... } */
                            elementMoveData.forEach(function(data) {
                                if (data.assignmentId in assignments) {
                                    data.bar.appendTo(data.td);
                                }
                            });
                        }
                    }.bind(this, elementMoveData));
            }
        },
    });

    // Drop into assignment table cell (status bar placement, status assignment move)

    interact(assignmentTableTrSelector + ' td').dropzone({
        accept: assignmentTableTrSelector + ' .bar[data-status], ' + statusBarPrototypeSelector,
        ondragenter: function (event) {
        },
        ondragleave: function (event) {
        },
        ondrop: function (event) {
            var $bar = $(event.relatedTarget);

            if ($bar.data('assignment-id')) {
                var assignmentId = $bar.data('assignment-id');
                var $td = $(event.target);
                var $tdFirst = self.options.flightAssignmentTable.find('tr:not(.head) td:not(:first-child)');
                var tdWidth = parseFloat($tdFirst.css('width').replace('px', ''));
                var $tr = $td.closest('tr');
                var tdIndex = $td.index();
                var tailNumber = $tr.data('tail-number');

                var $originalTd = $bar.closest('td');
                var oldStartTime = new Date(self.options.startDate.getTime()
                    + self.options.unit * ($originalTd.index() - 1) * 1000
                    + self.options.unit * 1000 * parseFloat($bar.css('left').replace('px', '')) / tdWidth);

                var diffSeconds = event.dragEvent.dx / tdWidth * self.options.unit;
                var seconds = oldStartTime.getTime() / 1000 + diffSeconds;
                var startTime = new Date(Math.round(seconds / 300) * 300 * 1000);

                var assignmentData = [{
                    assignment_id: assignmentId,
                    tail: tailNumber,
                    start_time: startTime,
                }];
                self.moveAssignment(assignmentData)
                    .then(function(response) {
                        if (response.success) {
                            var assignments = response.assignments; /* { assignment_id: { start_time, end_time }, ... } */
                            if (assignmentId in assignments) {
                                var assignmentData = assignments[assignmentId];
                                tdIndex = self.getTdIndex(startTime);
                                var $newTd = $tr.children('td').eq(tdIndex + 1);
                                var length = (new Date(assignmentData.end_time) - new Date(assignmentData.start_time)) / 1000 / self.options.unit;
                                self.placeStatusBar($bar, $newTd, length, assignmentData);
                            }
                        }
                    });
            } else if ($bar.data('status') > 0) {
                var $td = $(event.target);
                var $tr = $td.closest('tr');
                var tailNumber = $tr.data('tail-number');
                var tdIndex = $td.index();

                var startTime = new Date(self.options.startDate);
                startTime.setSeconds(startTime.getSeconds() + self.options.unit * (tdIndex - 1));
                var endTime = new Date(startTime.getTime() + 3600000);

                self.assignStatus(tailNumber, $bar.data('status'), startTime, endTime)
                    .then(function(response) {
                        if (response.success) {
                            var $newBar = $bar.clone();
                            self.placeStatusBar($newBar, $td, 3600 / self.options.unit, {
                                start_time: startTime,
                                end_time: endTime,
                            });
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

            if ($bar.hasClass('selected')) {
                var $selected = $bar.closest('.gantt-table').find('.bar.selected');
            } else {
                var $selected = $bar;
            }

            var assignmentIdsToRemove = [];
            var elementRemoveData = [];

            $selected.each(function() {
                var $selectedBar = $(this);
                if ($selectedBar.data('assignment-id')) {
                    var assignmentId = $selectedBar.data('assignment-id');
                    assignmentIdsToRemove.push(assignmentId);
                    elementRemoveData.push({
                        assignmentId: assignmentId,
                        bar: $selectedBar,
                    });
                }
            });

            if (assignmentIdsToRemove.length > 0) {
                self.removeAssignment(assignmentIdsToRemove)
                    .then(function(elementRemoveData, response) {
                        if (response.success) {
                            var removedAssignments = response.removed_assignments; /* [ assignment_ids ] */
                            elementRemoveData.forEach(function(data) {
                                if (removedAssignments.indexOf(data.assignmentId) >= 0) {
                                    var tdIndex = data.bar.closest('td').index();
                                    var flightNumber = data.bar.data('number');
                                    data.bar.remove();
                                    console.log(flightNumber)///
                                    console.log(self.options.flightTemplateTable.find('td:nth-child(' + (tdIndex + 1) + ') .bar.assigned[data-number="' + flightNumber + '"]'))///
                                    self.options.flightTemplateTable.find('td:nth-child(' + (tdIndex + 1) + ') .bar.assigned[data-number="' + flightNumber + '"]').removeClass('assigned');
                                }
                            });
                        }
                    }.bind(this, elementRemoveData));
            }
        },
    });

    // Select multiple and do action

    $(self.options.tablesWrapperSelector + ' .table-wrapper').on('mousedown', function(event) {
        var $target = $(event.target);
        if ($target.hasClass('bar') || $target.closest('.bar').length > 0) {
            return;
        }

        event.preventDefault();

        var $tableWrapper = $(this);
        var twOffset = $tableWrapper.offset();
        var $selectionMarker = $tableWrapper.children('.selection-area-indicator');
        var x = event.pageX - twOffset.left;
        var y = event.pageY - twOffset.top;

        $selectionMarker
            .css({
                left: x,
                top: y,
                width: 0,
                height: 0,
            })
            .attr('data-init-x', x)
            .attr('data-init-y', y)
            .addClass('active');
    })
    .on('mousemove', function(event) {
        var $tableWrapper = $(this);
        var twOffset = $tableWrapper.offset();
        var $selectionMarker = $tableWrapper.children('.selection-area-indicator');

        if ($selectionMarker.hasClass('active')) {
            event.preventDefault();
            var ix = parseInt($selectionMarker.attr('data-init-x'));
            var iy = parseInt($selectionMarker.attr('data-init-y'));
            var x = event.pageX - twOffset.left;
            var y = event.pageY - twOffset.top;
            var w = Math.abs(ix - x);
            var h = Math.abs(iy - y);
            $selectionMarker.css({
                width: w,
                height: h,
            });
            if (x < ix) {
                $selectionMarker.css('left', x);
            }
            if (y < iy) {
                $selectionMarker.css('top', y);
            }
        }
    })
    .on('mouseup', function(event) {
        var $tableWrapper = $(this);
        var $selectionMarker = $tableWrapper.children('.selection-area-indicator');

        if ($selectionMarker.hasClass('active')) {
            event.preventDefault();

            // Select items
            var sx = $selectionMarker.offset().left;
            var sy = $selectionMarker.offset().top;
            var sxe = sx + parseInt($selectionMarker.css('width').replace('px', ''));
            var sye = sy + parseInt($selectionMarker.css('height').replace('px', ''));
            var $bars = $tableWrapper.find('.bar');
            $bars.removeClass('selected').each(function() {
                var $bar = $(this);
                var bx = $bar.offset().left;
                var by = $bar.offset().top;
                var bxe = bx + parseInt($bar.css('width').replace('px', ''));
                var bye = by + parseInt($bar.css('height').replace('px', ''));

                if (
                    ((bx >= sx && bx <= sxe) || (bxe >= sx && bxe <= sxe) || (bx <= sx && bxe >= sxe))
                    && ((by >= sy && by <= sye) || (bye >= sy && bye <= sye) || (by <= sy && bye >= sye))
                    && !$bar.hasClass('assigned')
                ) {
                    $bar.addClass('selected');
                }
            });

            // Hide select rectangle
            $selectionMarker.removeClass('active');
        }
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

        var $cover = $(self.options.tablesWrapperSelector);
        $cover.removeClass('loading');
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
            tdIndex = self.getTdIndex(departureDateTime);
            tdPos = self.getTdPosition(departureDateTime);
            $bar = self.placeBar($tr, tdIndex, length, template);
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
        var tdIndex = self.getTdIndex(startTime);
        var length = (endTime - startTime) / 1000 / self.options.unit;
        var tdPos = self.getTdPosition(startTime);
        var $bar = self.placeBar($tr, tdIndex, length, assignment);
        if ($bar) {
            $bar
                .css('left', tdPos * 100 + '%')
                .attr('data-assignment-id', assignment.id)
                .attr('enabled', true);
        }
    }
}

RoutePlanningGantt.prototype.assignFlight = function(flightData) {
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
            flight_data: JSON.stringify(flightData),
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

RoutePlanningGantt.prototype.removeAssignment = function(assignmentIdsToRemove) {
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
            assignment_data: JSON.stringify(assignmentIdsToRemove),
        },
    });
}

RoutePlanningGantt.prototype.moveAssignment = function(assignmentData) {
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
            assignment_data: JSON.stringify(assignmentData),
        },
    });
}

RoutePlanningGantt.prototype.resizeAssignment = function(assignmentId, pos, diffSeconds) {
    var self = this;

    if (!self.options.moveAssignmentAPIUrl) {
        console.error('Move assignment API URL not configured');
        return;
    }

    return $.ajax({
        method: 'POST',
        url: self.options.resizeAssignmentAPIUrl,
        data: {
            csrfmiddlewaretoken: self.options.csrfToken,
            assignment_id: assignmentId,
            position: pos,
            diff_seconds: diffSeconds,
        },
    });
}
