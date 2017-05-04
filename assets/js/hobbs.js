"use strict";

/*
 * Coming Due List
 */

function ComingDueList(options) {
    this.options = options;
    this.$table = $(options.listSelector);
    this.anchorDate = new Date();

    this.refresh();
}

ComingDueList.prototype.setActualHobbsForm = function($form) {
    this.$actualHobbsForm = $form;
}

ComingDueList.prototype.setNextDueHobbsForm = function($form) {
    this.$nextDueHobbsForm = $form;
}

ComingDueList.prototype.formatHobbsDate = function(date) {
    var dateString = '';
    var weekdays = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday'];
    dateString += (date.getMonth() + 1) + '/'
    dateString += date.getDate() + '/';
    dateString += date.getFullYear() + ' ';
    dateString += weekdays[date.getDay()];
    return dateString;
}

ComingDueList.prototype.firstWeekDay = function() {
    var date = new Date(this.anchorDate.getTime());
    date.setDate(date.getDate() - date.getDay());
    return date;
}

ComingDueList.prototype.changeAnchorDate = function(date) {
    this.anchorDate = date;
    this.refresh();
}

ComingDueList.prototype.refresh = function() {
    var self = this;

    var data = {
        csrfmiddlewaretoken: self.options.apiCSRFToken,
        start: self.firstWeekDay().toISOString(),
        days: 7,
    };
    $.ajax({
        url: self.options.comingDueListAPI,
        method: 'POST',
        data: data,
    })
    .then(function(response) {
        if (response.success) {
            self.$table.empty();

            var $thead = $('<thead />');
            $thead.append('<th><strong>Date</strong></th>');
            $thead.append('<th><strong>Hobbs<br>EOD</strong></th>');
            $thead.append('<th><strong>Next Due<br>Hobbs</strong></th>');
            $thead.append('<th><strong>Hobbs<br>Left</strong></th>');
            if (self.options.writeable) {
                $thead.append('<th />');
            }
            self.$table.append($thead);

            var lastDay = '';
            for (var hobbs of response.hobbs_list) {
                var $tr = $('<tr data-actual-hobbs-id="' + hobbs.actual_hobbs_id + '" data-next-due-hobbs-id="' + hobbs.next_due_hobbs_id + '" />');
                if (hobbs.day != lastDay) {
                    $tr.append('<td>' + self.formatHobbsDate(new Date(hobbs.day)) + '</td>');
                    lastDay = hobbs.day;
                } else {
                    $tr.append('<td></td>');
                }
                $tr.append('<td>' + hobbs.actual + '</td>');
                $tr.append('<td>' + hobbs.next_due + '</td>');
                $tr.append('<td>' + (hobbs.next_due - hobbs.actual) + '</td>');
                if (self.options.writeable) {
                    $tr.append('<td style="padding-bottom: 3px;">' +
                        '<a href="javascript:;" class="btn btn-primary btn-xs btn-edit-hobbs"><i class="fa fa-fw fa-edit"></i></a> ' +
                        '<a href="javascript:;" class="btn-delete-flight btn btn-danger btn-xs btn-delete-hobbs"><i class="fa fa-fw fa-trash"></i></a>' +
                        '</td>');
                }
                self.$table.append($tr);
            }
        }
    });
}

/*
 * Hobbs Form (for both actual and next due forms)
 */

function HobbsForm(options) {
    this.options = options;
    this.$form = $(options.formSelector);

    this.init();
}

HobbsForm.prototype.init = function() {
    this.bindEventHandlers();
}

HobbsForm.prototype.bindEventHandlers = function() {
    var self = this;

    self.$form.on('click', '.save-and-add-another', function(event) {
        event.preventDefault();
        self.$form.find('.action-after-save').val('save-and-add-another');
        self.submitForm();
    });

    self.$form.on('click', '.save-and-continue', function() {
        event.preventDefault();
        self.$form.find('.action-after-save').val('save-and-continue');
        self.submitForm();
    });

    self.$form.on('click', '.save', function() {
        event.preventDefault();
        self.$form.find('.action-after-save').val('save');
        self.submitForm();
    });
}

HobbsForm.prototype.submitForm = function() {
    var self = this;
    var data = self.$form.serializeArray();
    var tmpData = {};
    var formData = {};

    for (var field of data) {
        tmpData[field.name] = field.value;
    }
    if (!tmpData['value'] || !tmpData['date'] || !tmpData['time']) {
        alert('Please enter all fields.');
        return;
    }

    formData['csrfmiddlewaretoken'] = tmpData['csrfmiddlewaretoken']
    formData['id'] = tmpData['hobbs_id'];
    formData['tail_id'] = tmpData['tail_id'];
    formData['type'] = tmpData['type'];
    formData['hobbs'] = tmpData['value'];
    var datetime = new Date(tmpData['date']);
    var timeparts = tmpData['time'].split(':');
    datetime.setHours(parseInt(timeparts[0]));
    datetime.setMinutes(parseInt(timeparts[1]));
    formData['datetime'] = datetime.toISOString();

    var apiUrl = self.$form.attr('action');

    $.ajax({
        url: apiUrl,
        method: 'POST',
        data: formData,
    })
    .then(function(data) {
        if (data.success) {
            self.$form.find('.hobbs-id').val(data.hobbs_id);
            var actionAfterSave = tmpData['action_after_save']
            if (actionAfterSave == 'save') {
                window.location.href = self.options.urlToRedirectAfterSave;
            } else if (actionAfterSave == 'save-and-add-another') {
                self.$form.find('.hobbs-id').val('');
                self.$form.find('.hobbs-date').val('');
                self.$form.find('.hobbs-time').val('');
                self.$form.find('.hobbs-value').val('');
            }
            if (actionAfterSave != 'save' && self.options.comingDueList) {
                var secondsDiff = (datetime - self.options.comingDueList.firstWeekDay()) / 1000;
                if (secondsDiff >= 0 && secondsDiff < 7 * 24 * 3600) {
                    self.options.comingDueList.refresh();
                }
            }
        }
    });
}
