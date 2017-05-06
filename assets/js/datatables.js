"use strict";

window.datatables = {

    _datatables: {},

    formatTo2Digits: function(val) {
        return val < 10 ? '0' + val : val;
    },

    /*
     * Automatic setup of datatables in the page
     *
     * Parameters for datatables: 
     *  class: datatable
     *  attributes: data-name, data-default-sort-column, [data-ajax-url], [data-selectable]
     *
     * Elements that will execute action predefined
     *  .select-all - Select/unselect all rows
     */
    setup: function () {
        var $datatable = $('.datatable');
        var name = $datatable.data('name');
        var self = this;

        var initSortColumn = $datatable.data('default-sort-column') ? parseInt($datatable.data('default-sort-column')) : 0;

        var options = {
            responsive: false,
            lengthMenu: [10, 25, 50, 100],
            aaSorting: [[initSortColumn, 'asc']],
        };

        if ($datatable.data('selectable')) {
            options['columnDefs'] = [
                {
                    "sortable": false,
                    render: function(data, type, full, meta) {
                        return '<input type="checkbox" class="checkbox-select" name="id[]" value="' + parseInt(full[1]) + '"/>'
                    },
                    targets: 0,
                }
            ];
            options['select'] = {
                style: 'multi'
            };
        }

        if ($datatable.data('timestamp-columns')) {
            var cols = $datatable.data('timestamp-columns').split(',');
            options['columnDefs'] = options['columnDefs'] ? options['columnDefs'] : [];
            for(var col of cols) {
                options['columnDefs'].push({
                    render: function(data, type, full, meta) {
                        var date = new Date(data * 1000);
                        return (date.getMonth() + 1) + '/' +
                            date.getDate() + '/' +
                            date.getFullYear() + ' ' +
                            self.formatTo2Digits(date.getHours()) + ':' +
                            self.formatTo2Digits(date.getMinutes());
                    },
                    targets: parseInt(col),
                });
            }
        }

        if ($datatable.data('ajax-url')) {
            var ajaxUrl = $datatable.data('ajax-url');
            var csrfToken = $datatable.data('ajax-csrf-token');
            options = Object.assign(options, {
                processing: true,
                serverSide: true,
                ajax: {
                    url: ajaxUrl,
                    type: "POST",
                    data: function(_data) {
                        if (csrfToken) {
                            _data = Object.assign(_data, {
                                csrfmiddlewaretoken: csrfToken,
                            });
                        }
                        if (window.datatableFilter) {
                            _data = Object.assign(_data, window.datatableFilter);
                        }
                        return _data;
                    }
                }
            });
        }

        var dt = $datatable.DataTable(options);
        this._datatables[name] = dt;

        // Check/uncheck all checkboxes in the table
        dt.on('click', '.select-all', function() {
            var rows = dt.rows({ 'search': 'applied' }).nodes();
            $('input[type="checkbox"]', rows).prop('checked', this.checked);
            if (this.checked) {
                dt.rows().select();
            } else {
                dt.rows().deselect();
            }
        });

        // Check/uncheck single checkbox
        dt.on('click', 'tr', function() {
            var $this = $(this);
            $this.toggleClass('selected');
            var $checkbox = $this.find('.checkbox-select');
            $this.hasClass('selected') ? $checkbox.prop('checked', 1) : $checkbox.prop('checked', 0);
        });
    },

    get: function(name) {
        return this._datatables[name];
    },

};

$(window).on('load', function() {
    window.datatables.setup();
});