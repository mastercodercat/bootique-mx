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

HobbsForm.prototype.load = function(hobbsId) {
    var self = this;

    var apiUrl = self.options.loadHobbsAPI.replace('0', hobbsId);

    $.ajax({
        method: 'GET',
        url: apiUrl,
    })
    .then(function(response) {
        if (response.success) {
            var hobbsArray = JSON.parse(response.hobbs);
            if (!hobbsArray.length) {
                return;
            }
            var hobbs = hobbsArray[0];
            self.$form.find('.hobbs-id').val(hobbs.pk);
            var hobbsDate = new Date(hobbs.fields.hobbs_time);
            self.$form.find('.hobbs-date').closest('.input-group.date').datepicker('update', hobbsDate);
            self.$form.find('.hobbs-time').val(hobbsDate.getHours() + ':' + hobbsDate.getMinutes());
            self.$form.find('.hobbs-value').val(hobbs.fields.hobbs);
            self.$form.find('.hobbs-flight').val(hobbs.fields.flight);
        }
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
    if (tmpData['flight_id']) {
        formData['flight_id'] = tmpData['flight_id']
    }
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
                self.$form.find('.hobbs-flight').val('');
            }
            if (actionAfterSave != 'save' && self.options.comingDueList) {
                self.options.comingDueList.refresh();
            }
        }
    });
}

window.HobbsForm = HobbsForm;

if (module && module.exports) {
    module.exports = HobbsForm;
}
