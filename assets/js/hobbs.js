"use strict";

/*
 * Coming Due List
 */

function ComingDueList(options) {
    this.options = options;
    this.$list = $(options.listSelector);

    this.refresh();
}

ComingDueList.prototype.setActualHobbsForm = function($form) {
    this.$actualHobbsForm = $form;
}

ComingDueList.prototype.setNextDueHobbsForm = function($form) {
    this.$nextDueHobbsForm = $form;
}

ComingDueList.prototype.refresh = function() {
    ///
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
    formData['value'] = tmpData['value'];
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
        }
    });
}
