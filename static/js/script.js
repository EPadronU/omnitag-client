//~ On document ready ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
$(document).ready(function() {
    $('nav .nav li a[href="#black-list"]').click(function() {
        fetch_list_entries('black-list');
    });

    $('nav .nav li a[href="#white-list"]').click(function() {
        fetch_list_entries('white-list');
    });

    $("#explorer").on("show.bs.modal", function() {
        explorer();
    });

    $("#explorer button.save").click(function() {
        save_data_path(get_active_list_name());
    });
});
//~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


//~ Functions ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
function delete_entry(list_name) {
    $.ajax({
        contentType: 'application/json',
        data: JSON.stringify({
            'entry-path': $(this).attr('data-path')
        }),
        type: 'DELETE',
        url: list_name
    }).done(function() {
        $('nav .nav li a[href="#' + list_name + '"]').click();
    });
}


function explorer(path) {
    $.ajax({
        data: {path: path},
        type: 'GET',
        url: "/explorer"
    }).done(function(data) {
        if(data.status === 'success') {
            $("#explorer .modal-body table").html(data.html);
            $("#explorer .modal-body table tbody tr .dir a").click(function() {
                explorer($(this).attr("data-path"));
            });
        }
    });
}


function fetch_list_entries(list_name) {
    $.ajax({
        type: 'GET',
        url: list_name
    }).success(function(data) {
        $('#' + list_name + ' table tbody').html(data.html);
        $('#' + list_name + ' table tbody tr td a').click(function() {
            delete_entry.call(this, list_name);
        });
    });
}


function get_active_list_name() {
    if($("nav .nav li.active").children("a").attr("href") == "#black-list") {
        return "black-list";

    } else {
        return "white-list";
    }
}


function save_data_path(list_name) {
    $.ajax({
        contentType: 'application/json',
        data: JSON.stringify({
            path: $("#explorer table thead tr th").attr("data-path")
        }),
        type: 'POST',
        url: list_name
    }).done(function(data) {
        if(data.status === 'success') {
            $("#explorer").modal("hide");
            $('nav .nav li a[href="#' + list_name + '"]').click();

        } else {
            // TODO
        }
    });
}
//~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
