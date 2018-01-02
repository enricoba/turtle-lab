/*
turtle-lab.org
Copyright (C) 2017  Henrik Baran

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
*/


// using jQuery
function getCookie(name) {
    var cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        var cookies = document.cookie.split(';');
        for (var i = 0; i < cookies.length; i++) {
            var cookie = jQuery.trim(cookies[i]);
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}


//var csrftoken = getCookie('csrftoken');
var csrftoken = jQuery("[name=csrfmiddlewaretoken]").val();


function csrfSafeMethod(method) {
    // these HTTP methods do not require CSRF protection
    return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
}


$.ajaxSetup({
    beforeSend: function(xhr, settings) {
        if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
            xhr.setRequestHeader("X-CSRFToken", csrftoken);
        }
    }
});


// VARIABLES
var table_row_color = "#98ccff";


// NAVIGATION
$('#id_nav_btn_new').click(function() {
    if (!$(this).hasClass("disabled")) {
        $('#id_modal_new').modal("show");
        $('#id_form_new').trigger("reset");
    }
});




$('#id_nav_btn_edit').click(function() {
    if (!$(this).hasClass("disabled")) {
        $('#id_modal_edit').modal("show");
        $('#id_form_edit').trigger("reset");

        // fill fields
        var values = [];
        $('#id_table').find('#id_unique').children('.gui').each(function() {
            values.push($(this).text());
        });

        var a = 0;
        values.forEach(function(i) {
            var element_type = $('#id_form_edit').find('p').eq(a).children().next().prop('nodeName');
            if (element_type === "INPUT") {
                var type = $('#id_modal_edit').find('p').eq(a).find('input').attr('type');
                if (type === "checkbox") {
                    if (i === "True") {
                        $('#id_modal_edit').find('p').eq(a).find('input').prop('checked', true);
                    } else {
                        $('#id_modal_edit').find('p').eq(a).find('input').prop('checked', false);
                    }
                } else if (type === "password") {
                    $('#id_modal_edit').find('p').eq(a).find('input').val('');
                } else {
                    $('#id_modal_edit').find('p').eq(a).find('input').val(i);
                }
            } else if (element_type === "SELECT") {
                var manual = $('#id_modal_edit').find('p').eq(a).find('select').hasClass("manual");
                if (manual === true) {
                    $('#id_modal_edit').find('p').eq(a).find('select').val(i);
                } else {
                    $('#id_modal_edit').find('p').eq(a).find('select option').each(function() {
                        if ($(this).text() === i) {
                            $('#id_modal_edit').find('p').eq(a).find('select').val($(this).val());
                        }
                    });
                }
            }
            a++;
        });
    }
});


// DELETE
$('#id_nav_btn_delete').click(function() {
    if (!$(this).hasClass("disabled")) {
        var items = [];
        $('.selected').each(function() {
          items.push($(this).find(".unique").text());
        });

        //console.log(items);
        if(confirm("Do you really want to delete record(s): " + items.toString() +  " ?")) {
            $.ajax({
                method: "POST",
                data: {
                    'dialog': 'delete',
                    'items': JSON.stringify(items)
                },
                dataType: 'json',
                success: function (data) {
                    if (data.response) {
                        location.reload();
                    } else {
                        alert(data.message);
                    }
                }
            });
        } else {
            return false;
        }
    }
});


// ACTIVATE
$('#id_nav_btn_active').click(function() {
    if (!$(this).hasClass("disabled")) {
        var item = $('#id_table').find('#id_unique').find("td:first").text();

        //console.log(items);
        $.ajax({
                method: "GET",
                data: {
                    'dialog': 'active',
                    'unique': item
                },
                dataType: 'json',
                success: function (data) {
                    if (data.response) {
                        if(data.is_active === true) {
                            if(confirm("Do you really want to deactivate user: " + item +  " ?")) {
                                $.ajax({
                                    method: "GET",
                                    data: {
                                        'dialog': 'active_response',
                                        'unique': data.unique,
                                        'response': 'deactivate'
                                    },
                                    dataType: 'json',
                                    success: function (data) {
                                        if (data.response) {
                                            location.reload();
                                        }
                                    }
                                })
                            }
                        } else {
                            if(confirm("Do you really want to activate user: " + item +  " ?")) {
                                $.ajax({
                                    method: "GET",
                                    data: {
                                        'dialog': 'active_response',
                                        'unique': data.unique,
                                        'response': 'activate'
                                    },
                                    dataType: 'json',
                                    success: function (data) {
                                        if (data.response) {
                                            location.reload();
                                        }
                                    }
                                })
                            }
                        }
                    }
                }
            });
    }
});




// rest size
/*var height_window = $(window).height();
var content_table = $('#id_content').height();
$('#id_rest').height(height_window - (145 + content_table));

// table size
//var width_window = $('#id_content').width();
//$('#id_tbody').width(width_window);
//$('#id_thead').width(width_window);
//$('#id_thead th').width(400);

$(window).resize(function(){
    var height_window = $(window).height();
    var content_table = $('#id_content').height();
    $('#id_rest').height(height_window - (145 + content_table));
});*/


// context menu
/*$.contextMenu({
    selector: '.context-menu',
    trigger: "right",
    items: {
        copy: {
            name: "Copy",
            icon: "copy"
        }
    }
});*/

$('#id_body').mousedown (function(event) {
    //event.preventDefault();
});


// tables
$('#id_table tbody tr').mousedown (function(event) {
    switch (event.which) {
        case 1:
            event.preventDefault();
            document.getSelection().removeAllRanges();
            $("#id_nav_btn_delete").removeClass('disabled').removeClass('btn-default').addClass('btn-danger');
            $("#id_nav_btn_edit").removeClass('disabled').removeClass('btn-default').addClass('btn-primary');
            $("#id_nav_btn_audittrail").removeClass('disabled').removeClass('btn-default').addClass('btn-warning');
            $("#id_nav_btn_movement").removeClass('disabled').removeClass('btn-default').addClass('btn-info');
            $("#id_nav_btn_barcode").removeClass('disabled').removeClass('btn-default').addClass('btn-info');
            $("#id_nav_btn_password").removeClass('disabled').removeClass('btn-default').addClass('btn-info');
            $("#id_nav_btn_active").removeClass('disabled').removeClass('btn-default').addClass('btn-success');
            if (event.ctrlKey) {
                event.preventDefault();
                $(this).addClass('selected');
                $(this).css("background-color", table_row_color);
                $("#id_nav_btn_edit").addClass('disabled').removeClass('btn-primary').addClass('btn-default');
                $("#id_nav_btn_audittrail").addClass('disabled').removeClass('btn-warning').addClass('btn-default');
                $("#id_nav_btn_movement").addClass('disabled').removeClass('btn-info').addClass('btn-default');
                $("#id_nav_btn_barcode").addClass('disabled').removeClass('btn-info').addClass('btn-default');
                $("#id_nav_btn_password").addClass('disabled').removeClass('btn-info').addClass('btn-default');
                $("#id_nav_btn_active").addClass('disabled').removeClass('btn-success').addClass('btn-default');
            } else {
                event.preventDefault();
                if ($(this).hasClass('.clicked')) {
                    $(this).removeClass('selected');
                    $(this).removeClass('.clicked');
                    $(this).css("background-color", "");
                    $(this).attr('id', '');
                    $("#id_nav_btn_delete").addClass('disabled').removeClass('btn-danger').addClass('btn-default');
                    $("#id_nav_btn_edit").addClass('disabled').removeClass('btn-primary').addClass('btn-default');
                    $("#id_nav_btn_audittrail").addClass('disabled').removeClass('btn-warning').addClass('btn-default');
                    $("#id_nav_btn_movement").addClass('disabled').removeClass('btn-info').addClass('btn-default');
                    $("#id_nav_btn_barcode").addClass('disabled').removeClass('btn-info').addClass('btn-default');
                    $("#id_nav_btn_password").addClass('disabled').removeClass('btn-info').addClass('btn-default');
                    $("#id_nav_btn_active").addClass('disabled').removeClass('btn-success').addClass('btn-default');
                } else {
                    $(this).addClass('selected').siblings().removeClass('selected').removeClass('.clicked').attr('id', '').css("background-color", "");
                    $(this).css("background-color", table_row_color);
                    $(this).addClass('.clicked');
                    $(this).attr('id', 'id_unique');
                    //console.log($(this).find("td:first").text());
                }
            }
            break;
        case 2:
            //alert('Middle Mouse button pressed.');
            break;
        case 3:
            //alert('Right Mouse button pressed.');
            break;
        default:
            //alert('You have a strange Mouse!');
    }
});
/*
$('#id_rest').on("click", function() {
    $("#id_nav_btn_delete").addClass('disabled').removeClass('btn-danger').addClass('btn-default');
    $("#id_nav_btn_edit").addClass('disabled').removeClass('btn-primary').addClass('btn-default');
    $("#id_nav_btn_audittrail").addClass('disabled').removeClass('btn-warning').addClass('btn-default');
    $("#id_nav_btn_movement").addClass('disabled').removeClass('btn-info').addClass('btn-default');
    $("#id_nav_btn_barcode").addClass('disabled').removeClass('btn-info').addClass('btn-default');
    $('#id_table tr').siblings().removeClass('selected').removeClass('.clicked').css("background-color", "");
});

$('#id_navbar').on("click", function() {
    $("#id_nav_btn_delete").addClass('disabled').removeClass('btn-danger').addClass('btn-default');
    $("#id_nav_btn_edit").addClass('disabled').removeClass('btn-primary').addClass('btn-default');
    $("#id_nav_btn_audittrail").addClass('disabled').removeClass('btn-warning').addClass('btn-default');
    $("#id_nav_btn_movement").addClass('disabled').removeClass('btn-info').addClass('btn-default');
    $("#id_nav_btn_barcode").addClass('disabled').removeClass('btn-info').addClass('btn-default');
    $('#id_table tr').siblings().removeClass('selected').removeClass('.clicked').css("background-color", "");
});

$('#id_footer').on("click", function() {
    $("#id_nav_btn_delete").addClass('disabled').removeClass('btn-danger').addClass('btn-default');
    $("#id_nav_btn_edit").addClass('disabled').removeClass('btn-primary').addClass('btn-default');
    $("#id_nav_btn_audittrail").addClass('disabled').removeClass('btn-warning').addClass('btn-default');
    $("#id_nav_btn_movement").addClass('disabled').removeClass('btn-info').addClass('btn-default');
    $("#id_nav_btn_barcode").addClass('disabled').removeClass('btn-info').addClass('btn-default');
    $('#id_table tr').siblings().removeClass('selected').removeClass('.clicked').css("background-color", "");
});*/
