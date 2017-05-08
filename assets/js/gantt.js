"use strict";

var ganttLengthSeconds = 14 * 24 * 3600;

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

RoutePlanningGantt.prototype.getPosition = function(date) {
    var self = this;

    var diffFromStart = (date - self.options.startDate) / 1000;
    return diffFromStart / ganttLengthSeconds * 100;
}

RoutePlanningGantt.prototype.getUnitWidthPercentage = function() {
    return 100 / (ganttLengthSeconds / this.options.unit);
}

RoutePlanningGantt.prototype.getUnitWidth = function($row) {
    return $row.width() / (ganttLengthSeconds / this.options.unit);
}

RoutePlanningGantt.prototype.placeBar = function($row, pos, length, object) {
    /*
     * object can be flight (from template table) or assignment (from assignment table)
     */
    var self = this;
    var $bar = null;
    var date;
    var unitWidth = self.getUnitWidthPercentage();

    if (object.number > 0) {
        $bar = $('.bar.prototype').clone().removeClass('prototype');
        $bar
            .css({
                width: unitWidth * length + '%',
                left: pos + '%',
            });
        $bar.find('.number').html(object.number);
        $bar.find('.org').html(object.origin);
        $bar.find('.dest').html(object.destination);
        date = new Date(object.departure_datetime);
        $bar.find('.departure').html(formatDate(date));
        date = new Date(object.arrival_datetime);
        $bar.find('.arrival').html(formatDate(date));

        $row.append($bar);
    } else {
        var status = object.status;
        $bar = $('.status-prototype[data-status="' + status + '"]').clone().removeClass('status-prototype');
        $bar
            .css({
                width: unitWidth * length + '%',
                left: pos + '%',
            });
        self.setStatusBarInfo($bar, object);
        $row.append($bar);
    }
    return $bar;
}

RoutePlanningGantt.prototype.setFlightHobbsInfo = function($bar, actualHobbs, nextDueHobbs) {
    var hobbsLeft = nextDueHobbs - actualHobbs;
    $bar.find('.projected-hobbs').html(actualHobbs.toFixed(1));
    $bar.find('.next-due-hobbs').html(nextDueHobbs.toFixed(1));
    $bar.find('.hobbs-left').html(hobbsLeft.toFixed(1));
    $bar.removeClass('hobbs-green')
        .removeClass('hobbs-red')
        .removeClass('hobbs-yellow');
    $bar.find('.field-hobbs-left').removeClass('hobbs-green')
        .removeClass('hobbs-red')
        .removeClass('hobbs-yellow');
    if (hobbsLeft >= 15) {
        $bar.addClass('hobbs-green');
        $bar.find('.field-hobbs-left').addClass('hobbs-green');
    } else if (hobbsLeft >= 8) {
        $bar.addClass('hobbs-yellow');
        $bar.find('.field-hobbs-left').addClass('hobbs-yellow');
    } else {
        $bar.addClass('hobbs-red');
        $bar.find('.field-hobbs-left').addClass('hobbs-red');
    }
}

RoutePlanningGantt.prototype.setStatusBarInfo = function($bar, object) {
    var $info = $bar.find('.info');
    date = new Date(object.start_time);
    $info.find('.start').html(formatDate(date));
    date = new Date(object.end_time);
    $info.find('.end').html(formatDate(date));
}

RoutePlanningGantt.prototype.placeStatusBar = function($bar, $row, object) {
    var self = this;
    var startTime = new Date(object.start_time);
    var endTime = new Date(object.end_time);
    var pos = self.getPosition(startTime);
    var length = (endTime - startTime) / 1000 / self.options.unit;
    var unitWidth = self.getUnitWidthPercentage();

    $bar
        .removeClass('status-prototype')
        .css('left', pos + '%')
        .css('width', unitWidth * length + '%');

    self.setStatusBarInfo($bar, object);

    $row.append($bar);

    return $bar;
}

RoutePlanningGantt.prototype.resizeStatusBar = function($bar, startTime, endTime) {
    var self = this;
    var pos = self.getPosition(startTime);
    var length = (endTime - startTime) / 1000 / self.options.unit;
    var unitWidth = self.getUnitWidthPercentage();

    $bar
        .css('left', pos + '%')
        .css('width', unitWidth * length + '%');

    self.setStatusBarInfo($bar, {
        start_time: startTime.toISOString(),
        end_time: endTime.toISOString(),
    });

    return $bar;
}

RoutePlanningGantt.prototype.displayNowIndicator = function($table) {
    var self = this;
    var now = new Date();
    if (now >= self.options.startDate && now <= self.options.endDate) {
        var parentWidth = $table.width() - 90;
        var left = (now - self.options.startDate) / 1000 / ganttLengthSeconds;
        $table.closest('.table-wrapper').find('.now-indicator').css('left', parentWidth * left + 90).removeClass('hidden');
    }
}

RoutePlanningGantt.prototype.initInteractables = function() {
    var self = this;
    var assignmentTableId = self.options.flightAssignmentTable.attr('id');
    var assignmentTableRowSelector = '#' + assignmentTableId + ' > .row-line';
    var ganttTableBarSelector = '.gantt-table > .row-line .bar:not(.assigned)';
    var statusBarPrototypeSelector = '.status-bars .bar';
    var draggables = [ganttTableBarSelector, statusBarPrototypeSelector];
    var removeAreaSelector = '#drop-to-remove-area';

    // Resizeable status assignment bar

    interact(assignmentTableRowSelector + ' .bar[data-status]').resizable({
        edges: { left: true, right: true }
    })
    .on('resizestart', function(event) {
        var $bar = $(event.target);

        $bar.attr('data-org-width', $bar.width())
            .addClass('resizing');
    })
    .on('resizemove', function(event) {
        var $bar = $(event.target);
        var $row = $bar.closest('.row-line');
        var unitWidth = self.getUnitWidth($row);
        var resizeUnit = parseFloat(unitWidth * 300 / self.options.unit);  // Resize unit will be per 5 mins

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
        var $row = $bar.closest('.row-line');
        var unitWidth = self.getUnitWidth($row);
        var dw = $bar.attr('data-dw');
        var pos = $bar.attr('data-pos');

        var dt = parseFloat(dw) / unitWidth * self.options.unit;
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

                    self.resizeStatusBar($bar, startTime, endTime);
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
                    var flightId = $selectedBar.data('flight-id');
                    if (flightId) {
                        $('#shadow' + flightId).remove();
                    }
                });
            },
        }).actionChecker(function (pointer, event, action) {
            if (event.button !== 0) {
                return null;
            }
            return action;
        }).on('click', function(event) {
            var $target = $(event.target);
            var $bar = $target.hasClass('bar') || $target.closest('.bar');
            var $ganttTable = $target.closest('.gantt-table');
            if ($bar.length > 0 && $ganttTable.length > 0) {
                if (event.shiftKey) {
                    $bar.addClass('selected');
                } else if (event.altKey) {
                    $bar.removeClass('selected');
                } else {
                    $ganttTable.find('.bar.selected').removeClass('selected');
                    $bar.addClass('selected');
                }
            }
        });
    });

    // Drop into assignment table row (flight/status bar assign and move)

    interact(assignmentTableRowSelector).dropzone({
        accept: [ganttTableBarSelector, assignmentTableRowSelector + ' .bar[data-status]', statusBarPrototypeSelector].join(','),
        ondragenter: function (event) {
            var $bar = $(event.relatedTarget);
            if ($bar.data('status')) {
                return;
            }
            var $hoveringRow = $(event.target);
            var hoveringRowIndex = parseInt($hoveringRow.data('index'));
            var primaryRowIndex = parseInt($bar.closest('.row-line').data('index'));

            if ($bar.hasClass('selected')) {
                var $selected = $bar.closest('.gantt-table').find('.bar.selected');
            } else {
                var $selected = $bar;
            }

            $selected.each(function() {
                var $selectedBar = $(this);
                var originalRowIndex = parseInt($selectedBar.closest('.row-line').data('index'));
                if (primaryRowIndex == originalRowIndex) {
                    var $row = $hoveringRow;
                } else {
                    var newRowIndex = hoveringRowIndex - primaryRowIndex + originalRowIndex;
                    var $row = $hoveringRow.siblings('.row-line[data-index="' + newRowIndex + '"]');
                }
                var flightId = $selectedBar.data('flight-id');
                if (flightId) {
                    var $shadow = $('#shadow' + flightId);
                    if (!$shadow.length) {
                        $shadow = $('.shadow.prototype').clone()
                            .removeClass('prototype')
                            .attr('id', 'shadow' + flightId)
                            .css({
                                left: $selectedBar.css('left'),
                                width: $selectedBar.css('width'),
                            });
                    }
                    if ($row.length > 0) {
                        $row.append($shadow);
                    } else {
                        $('#reserves').append($shadow);
                    }
                }
            });
        },
        ondragleave: function (event) {
        },
        ondrop: function (event) {
            var $bar = $(event.relatedTarget);

            if ($bar.data('status')) {

                /* Status assignment or move */

                if ($bar.data('assignment-id')) {
                    var $hoveringRow = $(event.target);
                    var hoveringRowIndex = parseInt($hoveringRow.data('index'));
                    var primaryRowIndex = parseInt($bar.closest('.row-line').data('index'));

                    if ($bar.hasClass('selected')) {
                        var $selected = $bar.closest('.gantt-table').find('.bar.selected');
                    } else {
                        var $selected = $bar;
                    }

                    var assignmentData = [];
                    var elementMoveData = {};

                    $selected.each(function() {
                        var $selectedBar = $(this);
                        var originalRowIndex = parseInt($selectedBar.closest('.row-line').data('index'));
                        if (primaryRowIndex == originalRowIndex) {
                            var $row = $hoveringRow;
                        } else {
                            var newRowIndex = hoveringRowIndex - primaryRowIndex + originalRowIndex;
                            var $row = $hoveringRow.siblings('.row-line[data-index="' + newRowIndex + '"]');
                        }
                        if ($row.length > 0) {
                            var assignmentId = $selectedBar.data('assignment-id');
                            var tailNumber = $row.data('tail-number');
                            var startDiffSeconds = parseFloat($selectedBar.css('left')) / $row.width() * ganttLengthSeconds;
                            startDiffSeconds = Math.round(startDiffSeconds / 300) * 300;
                            var diffSeconds = ganttLengthSeconds / $row.width() * event.dragEvent.dx;
                            diffSeconds = Math.round(diffSeconds / 300) * 300;
                            var startTime = new Date(self.options.startDate.getTime() + startDiffSeconds * 1000 + diffSeconds * 1000);

                            assignmentData.push({
                                assignment_id: assignmentId,
                                tail: tailNumber,
                                start_time: startTime,
                            });
                            elementMoveData[assignmentId] = {
                                row: $row,
                                bar: $selectedBar,
                            };
                        }
                    });

                    self.moveAssignment(assignmentData)
                        .then(function(response) {
                            if (response.success) {
                                self.loadData(true);
                                // var assignments = response.assignments; /* { assignment_id: { start_time, end_time }, ... } */
                                // for (assignmentId in assignments) {
                                //     if (assignmentId in elementMoveData) {
                                //         // self.placeStatusBar(
                                //         //     elementMoveData[assignmentId].bar,
                                //         //     elementMoveData[assignmentId].row,
                                //         //     assignments[assignmentId]
                                //         // );
                                //     }
                                // }
                            }
                        });
                } else if ($bar.data('status') > 0) {
                    var $row = $(event.target);
                    var x = event.dragEvent.clientX - $row.offset().left;
                    var diffSeconds = ganttLengthSeconds / $row.width() * x;
                    diffSeconds = Math.round(diffSeconds / 300) * 300;
                    var tailNumber = $row.data('tail-number');
                    var startTime = new Date(self.options.startDate);
                    startTime.setSeconds(startTime.getSeconds() + diffSeconds);
                    startTime.setMinutes(0);
                    startTime.setSeconds(0);
                    var endTime = new Date(startTime.getTime() + 3600000);

                    self.assignStatus(tailNumber, $bar.data('status'), startTime, endTime)
                        .then(function(response) {
                            if (response.success) {
                                var $newBar = $bar.clone();
                                self.placeStatusBar($newBar, $row, {
                                    start_time: startTime,
                                    end_time: endTime,
                                });
                                $newBar.attr('data-assignment-id', response.id);
                            }
                        });
                }

            } else {

                /* Flight assignment mass assign/move */

                var $hoveringRow = $(event.target);
                var hoveringRowIndex = parseInt($hoveringRow.data('index'));
                var primaryRowIndex = parseInt($bar.closest('.row-line').data('index'));

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
                    var originalRowIndex = parseInt($selectedBar.closest('.row-line').data('index'));
                    if (primaryRowIndex == originalRowIndex) {
                        var $row = $hoveringRow;
                    } else {
                        var newRowIndex = hoveringRowIndex - primaryRowIndex + originalRowIndex;
                        var $row = $hoveringRow.siblings('.row-line[data-index="' + newRowIndex + '"]');
                    }

                    var flightId = $selectedBar.data('flight-id');
                    $('#shadow' + flightId).remove();

                    if ($row.length > 0) {
                        var tailNumber = $row.data('tail-number');

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
                                row: $row,
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
                                row: $row,
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
                                        var assignedFlightData = assignedFlights[data.flightId];

                                        var $newBar = data.bar.clone().attr('enabled', true);
                                        $newBar.attr('data-assignment-id', assignedFlightData.assignment_id)
                                            .appendTo(data.row);
                                        self.setFlightHobbsInfo($newBar, assignedFlightData.actual_hobbs, assignedFlightData.next_due_hobbs);

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
                                self.loadData(true);
                                // var assignments = response.assignments; /* { assignment_id: { start_time, end_time }, ... } */
                                // elementMoveData.forEach(function(data) {
                                //     if (data.assignmentId in assignments) {
                                //         data.bar.appendTo(data.row);
                                //         /////
                                //         // self.setFlightHobbsInfo(
                                //         //     data.bar,
                                //         //     assignments[data.assignmentId].actual_hobbs,
                                //         //     assignments[data.assignmentId].next_due_hobbs
                                //         // );
                                //     }
                                // });
                            }
                        }.bind(this, elementMoveData));
                }
            }
        },
    });

    // Drop into Remove area

    interact(removeAreaSelector).dropzone({
        accept: assignmentTableRowSelector + ' .bar',
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
                var flightId = $selectedBar.data('flight-id');
                $('#shadow' + flightId).remove();
            });

            if (assignmentIdsToRemove.length > 0) {
                self.removeAssignment(assignmentIdsToRemove)
                    .then(function(elementRemoveData, response) {
                        if (response.success) {
                            self.loadData(true);
                            // var removedAssignments = response.removed_assignments; /* [ assignment_ids ] */
                            // elementRemoveData.forEach(function(data) {
                            //     if (removedAssignments.indexOf(data.assignmentId) >= 0) {
                            //         var flightId = data.bar.data('flight-id');
                            //         data.bar.remove();
                            //         self.options.flightTemplateTable.find('.bar.assigned[data-flight-id="' + flightId + '"]').removeClass('assigned');
                            //     }
                            // });
                        }
                    }.bind(this, elementRemoveData));
            }
        },
    });

    // Select multiple and do action

    $(self.options.tablesWrapperSelector + ' .table-wrapper').on('mousedown', function(event) {
        var $target = $(event.target);
        if ($target.hasClass('bar') || $target.closest('.bar').length > 0
             || $target.closest('.axis-cell').length > 0
             || $target.closest('.label-cell').length > 0) {
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
            var $bars = $tableWrapper.find('.bar:not(.assigned)');

            if (!event.originalEvent.shiftKey && !event.originalEvent.altKey) {
                $bars.removeClass('selected');
            }

            $bars.each(function() {
                var $bar = $(this);
                var bx = $bar.offset().left;
                var by = $bar.offset().top;
                var bxe = bx + parseInt($bar.css('width').replace('px', ''));
                var bye = by + parseInt($bar.css('height').replace('px', ''));

                if (
                    ((bx >= sx && bx <= sxe) || (bxe >= sx && bxe <= sxe) || (bx <= sx && bxe >= sxe))
                    && ((by >= sy && by <= sye) || (bye >= sy && bye <= sye) || (by <= sy && bye >= sye))
                ) {
                    if (event.originalEvent.altKey) {
                        $bar.removeClass('selected');
                    } else {
                        $bar.addClass('selected');
                    }
                }
            });

            // Hide select rectangle
            $selectionMarker.removeClass('active');
        }
    });
}

RoutePlanningGantt.prototype.checkIfAssigned = function(flightId) {
    var assignmentCount = this.assignments.length;
    for (var i = 0; i < assignmentCount; i++) {
        if (this.assignments[i].flight_id == flightId) {
            return true;
        }
    }
    return false;
}

RoutePlanningGantt.prototype.loadData = function(assignmentsOnly = false) {
    var self = this;

    var startDate = this.options.startDate;
    var endDate = this.options.endDate;
    $.ajax({
        url: this.options.loadDataAPIUrl,
        method: 'GET',
        data: {
            startdate: startDate.getTime() / 1000,
            enddate: endDate.getTime() / 1000,
            assignments_only: assignmentsOnly,
        },
    })
    .then(function(data) {
        if (!assignmentsOnly) {
            self.options.flightTemplateTable.find('.bar').remove();
            self.templates = {};
            data.templates.forEach(function(template) {
                if (!(template.number in self.templates)) {
                    self.templates[template.number] = []
                }
                self.templates[template.number].push(template);
            });
            self.refreshTemplateTable();
        }

        self.options.flightAssignmentTable.find('.bar').remove();
        self.assignments = [];
        data.assignments.forEach(function(assignment) {
            self.assignments.push(assignment);
        });
        self.refreshAssignmentTable();

        var $cover = $(self.options.tablesWrapperSelector);
        $cover.removeClass('loading');
        $('.status-bars').removeClass('disabled');
    });
}

RoutePlanningGantt.prototype.refreshTemplateTable = function() {
    var self = this;
    var templates, template, length;
    var $bar;
    var departureDateTime, arrivalDateTime;

    for (var flightNumber in self.templates) {
        templates = self.templates[flightNumber];
        for(var index in templates) {
            template = templates[index];
            arrivalDateTime = new Date(template.arrival_datetime);
            departureDateTime = new Date(template.departure_datetime);

            var date = new Date(self.options.startDate.getTime());
            var $row = self.options.flightTemplateTable.find('.row-line[data-line=' + template.line_id + ']');
            pos = self.getPosition(departureDateTime);
            length = (arrivalDateTime - departureDateTime) / 1000 / self.options.unit;
            $bar = self.placeBar($row, pos, length, template);
            if ($bar) {
                $bar
                    .attr('data-departure-time', departureDateTime.toISOString())
                    .attr('data-flight-id', template.id);
                if (self.checkIfAssigned(template.id)) {
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
        var $row = self.options.flightAssignmentTable.find('.row-line[data-tail-number="' + assignment.tail + '"]');
        var startTime = new Date(assignment.start_time);
        var endTime = new Date(assignment.end_time);
        var length = (endTime - startTime) / 1000 / self.options.unit;
        var pos = self.getPosition(startTime);
        var $bar = self.placeBar($row, pos, length, assignment);
        if ($bar) {
            $bar.attr('data-assignment-id', assignment.id)
                .attr('enabled', true);
            if (assignment.flight_id) {
                $bar.attr('data-flight-id', assignment.flight_id);
            }
            if (assignment.status == 1) {
                self.setFlightHobbsInfo($bar, assignment.actual_hobbs, assignment.next_due_hobbs);
            }
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
