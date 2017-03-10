window.datatables = {

    _datatables: {},

    /*
     * Automatic setup of datatables in the page
     * Parameters for datatables: 
     *  class: datatable
     *  attributes: data-name, [data-ajax-url]
     */
    setup: function () {
        var $datatable = $('.datatable');
        var name = $datatable.attr('data-name');

        var options = {
            responsive: true,
            columnDefs: [
                {
                    "sortable": false,
                    render: function(data, type, full, meta) {
                        return '<input type="checkbox" class="checkbox-select" name="id[]" value="' + parseInt(full[0]) + '"/>'
                    },
                    targets: 0,
                }
            ],
            select: {
                style: 'multi'
            },
            lengthMenu: [10, 25, 50, 100],
        };

        if ($datatable.data('ajax-url')) {
            var ajaxUrl = $datatable.data('ajax-url');
            options = Object.assign(options, {
                processing: true,
                serverSide: true,
                ajax: {
                    url: ajaxUrl,
                    type: "POST",
                    data: function(_data) {
                        if (window.datatableFilter) {
                            _data = Object.assign(_data, window.datatableFilter);
                        }
                        return _data;
                    }
                }
            });
        }

        this._datatables[name] = $datatable.DataTable(options);

        // Check/uncheck all checkboxes in the table
        $('.select-all').on('click', function(){
            var dtName = $(this).closest('.datatable').attr('data-name');
            var datatable = window.datatables.get(dtName);
            var rows = datatable.rows({ 'search': 'applied' }).nodes();
            $('input[type="checkbox"]', rows).prop('checked', this.checked);
            // if (this.checked) {
            //     datatable.rows().select();
            // } else {
            //     datatable.rows().deselect();
            // }
        });
    },

    get: function(name) {
        return this._datatables[name];
    },

};

$(window).on('load', function() {
    window.datatables.setup();
});