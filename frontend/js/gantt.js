var interact = require('interactjs');
var Utils = require('./utils.js');
var Cookies = require('js-cookie');
var moment = require('moment-timezone');

var ganttLengthSeconds = 14 * 24 * 3600;

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
    this.revision = 0;

    this.options = options;

    if (this.options.flightAssignmentTable
        && this.options.flightTemplateTable
        && this.options.startDate
        && this.options.endDate
    ) {
        this.setupTimezone();
        if (!this.options.readOnly) {
            this.initInteractables();
            this.initEventHandlers();
        }
        this.displayNowIndicator(this.options.flightAssignmentTable);
        this.displayNowIndicator(this.options.flightTemplateTable);
        this.loadData();
    } else {
        console.error('Invalid table initialization parameters')
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

RoutePlanningGantt.prototype.alertErrorIfAny = function(response, singular) {
    if (singular) {
        if (response.duplication) {
            alert('Timeframe overlapped with other assignments');
        } else if (response.physically_invalid) {
            alert('Physically invalid assignment');
        }
    } else {
        var errorOccurred = false;
        var errors = "Some of assignments are not placed due to following errors:";
        if (response.duplication) {
            errorOccurred = true;
            errors += "\n- Overlapped timeframe";
        }
        if (response.physically_invalid) {
            errorOccurred = true;
            errors += "\n- Physically invalid assignment";
        }
        if (errorOccurred) {
            alert(errors);
        }
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
                    if ($bar.data('status') == 3) {
                        self.loadData(true);
                    } else {
                        var startTime = new Date(response.start_time);
                        var endTime = new Date(response.end_time);

                        self.resizeStatusBar($bar, startTime, endTime);
                    }
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
                            }
                            self.alertErrorIfAny(response, assignmentData.length == 1);
                        });
                } else if ($bar.data('status') > 0) {
                    var $row = $(event.target);
                    var x = event.dragEvent.clientX - $row.offset().left;
                    var diffSeconds = ganttLengthSeconds / $row.width() * x;
                    diffSeconds = Math.round(diffSeconds / 300) * 300;
                    var status = $bar.data('status');
                    var tailNumber = $row.data('tail-number');
                    var startTime = new Date(self.options.startDate);
                    startTime.setSeconds(startTime.getSeconds() + diffSeconds);
                    startTime.setMinutes(0);
                    startTime.setSeconds(0);
                    var endTime = new Date(startTime.getTime() + 3600000);

                    if (status == 3) {
                        var data = {
                            tailNumber: tailNumber,
                            status: status,
                            startTime: startTime.getTime(),
                            endTime: endTime.getTime(),
                        };
                        self.options.unscheduledFlightForm.find('form').attr('data-assignment', JSON.stringify(data));
                        self.options.unscheduledFlightForm.modal();
                    } else {
                        self.assignStatus(tailNumber, status, startTime, endTime)
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
                                self.loadData(true);
                                var assignedFlights = response.assigned_flights; /* { flightId: assignmentId, ... } */
                                elementMoveData.forEach(function(data) {
                                    if (data.flightId in assignedFlights) {
                                        data.bar.addClass('assigned')
                                            .attr('enabled', false);
                                    }
                                });
                            }
                            self.alertErrorIfAny(response, assignmentData.length == 1);
                        }.bind(this, elementMoveData));
                } else {
                    self.moveAssignment(assignmentData)
                        .then(function(elementMoveData, response) {
                            if (response.success) {
                                self.loadData(true);
                            }
                            self.alertErrorIfAny(response, assignmentData.length == 1);
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
                            var removedAssignments = response.removed_assignments; /* [ assignment_ids ] */
                            elementRemoveData.forEach(function(data) {
                                if (removedAssignments.indexOf(data.assignmentId) >= 0) {
                                    var flightId = data.bar.data('flight-id');
                                    self.options.flightTemplateTable.find('.bar.assigned[data-flight-id="' + flightId + '"]').removeClass('assigned');
                                }
                            });
                        }
                    }.bind(this, elementRemoveData));
            }
        },
    });
}

RoutePlanningGantt.prototype.initEventHandlers = function() {
    var self = this;

    // Unscheduled Flight modal

    self.options.unscheduledFlightForm.on('click', '.btn-save-unscheduled-flight', function() {
        var $form = self.options.unscheduledFlightForm.find('form');
        var data = $form.data('assignment');
        if (!data.tailNumber || !data.status || !data.startTime || !data.endTime) {
            console.error('Unexpected error: no data about unscheduled flight found');
            return;
        }

        var origin = $form.find('.unscheduled-flight-origin').val();
        var destination = $form.find('.unscheduled-flight-destination').val();
        if (!origin || !destination) {
            alert('Please enter origin and destination of the unscheduled flight');
            return;
        }

        self.assignStatus(data.tailNumber, data.status,
            new Date(data.startTime), new Date(data.endTime),
            origin, destination)
            .then(function(response) {
                if (response.success) {
                    self.loadData(true);
                } else {
                    alert(response.error);
                }
            });

        self.options.unscheduledFlightForm.modal('hide');
    });

    // Revision buttons

    $('#publish-revision').on('click', function() {
        self.publishRevision()
        .then(function(response) {
            if (response.success) {
                self.revision = response.revision;
                $('#revisions').children('option:not(:first-child)').remove()
                for(var index in response.revisions) {
                    var revision = response.revisions[index];
                    $('#revisions').append($('<option value="' + revision.id + '">' + revision.published + '</option>'));
                }
                $('#revisions').val(self.revision);
            }
        });
    });

    $('#clear-revision').on('click', function() {
        self.clearRevision()
        .then(function(response) {
            if (response.success) {
                self.loadData();
            }
        });
    });

    $('#delete-revision').on('click', function() {
        self.deleteRevision()
        .then(function(response) {
            if (response.success) {
                $('#revisions').children('option:not(:first-child)').remove()
                for(var index in response.revisions) {
                    var revision = response.revisions[index];
                    $('#revisions').append($('<option value="' + revision.id + '">' + revision.published + '</option>'));
                }
                if (response.revisions.length > 0) {
                    self.revision = response.revisions[0].id;
                } else {
                    self.revision = 0;
                }
                $('#revisions').val(self.revision);
                self.loadData();
            }
        });
    });
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
            revision: self.revision,
        },
    });
}

RoutePlanningGantt.prototype.assignStatus = function(tailNumber, status, startTime, endTime, origin = '', destination = '') {
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
            origin: origin,
            destination: destination,
            revision: self.revision,
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
            revision: self.revision,
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
            revision: self.revision,
        },
    });
}

RoutePlanningGantt.prototype.resizeAssignment = function(assignmentId, pos, diffSeconds) {
    var self = this;

    if (!self.options.resizeAssignmentAPIUrl) {
        console.error('Resize assignment API URL not configured');
        return;
    }

    return $.ajax({
        method: 'POST',
        url: self.options.resizeAssignmentAPIUrl,
        data: {
            csrfmiddlewaretoken: self.options.csrfToken,
            assignment_id: assignmentId,
            revision: self.revision,
            position: pos,
            diff_seconds: diffSeconds,
        },
    });
}

RoutePlanningGantt.prototype.publishRevision = function() {
    var self = this;

    if (!self.options.publishRevisionAPIUrl) {
        console.error('Publish revision API URL not configured');
        return;
    }

    return $.ajax({
        method: 'POST',
        url: self.options.publishRevisionAPIUrl,
        data: {
            csrfmiddlewaretoken: self.options.csrfToken,
            revision: self.revision,
        },
    });
}

RoutePlanningGantt.prototype.clearRevision = function() {
    var self = this;

    if (!self.options.clearRevisionAPIUrl) {
        console.error('Clear revision API URL not configured');
        return;
    }

    return $.ajax({
        method: 'POST',
        url: self.options.clearRevisionAPIUrl,
        data: {
            csrfmiddlewaretoken: self.options.csrfToken,
            revision: self.revision,
        },
    });
}

RoutePlanningGantt.prototype.deleteRevision = function() {
    var self = this;

    if (!self.options.deleteRevisionAPIUrl) {
        console.error('Delete revision API URL not configured');
        return;
    }

    return $.ajax({
        method: 'POST',
        url: self.options.deleteRevisionAPIUrl,
        data: {
            csrfmiddlewaretoken: self.options.csrfToken,
            revision: self.revision,
        },
    });
}

window.RoutePlanningGantt = RoutePlanningGantt;

if (module && module.exports) {
    module.exports = RoutePlanningGantt;
}
