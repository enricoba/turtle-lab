/*
turtle-lab.org
Copyright (C) 2018  Henrik Baran

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


// cover
$(window).on('load', function() {
   $("#cover").hide();
});

// VARIABLES
var table_row_color = "#98ccff";
var count_selected, i, index_unique, index_selected_old, index_selected_actual, all_tr, has_class;

//table
var table = $('#id_table');

// buttons
var button_delete = $("#id_nav_btn_delete");
var button_edit = $("#id_nav_btn_edit");
var button_duplicate = $("#id_nav_btn_duplicate");
var button_log_record = $("#id_nav_btn_audit_trail");
var button_movement = $("#id_nav_btn_movement");
var button_boxing = $("#id_nav_btn_overview_boxing");
var button_barcode = $("#id_nav_btn_barcode");
var button_password = $("#id_nav_btn_password");
var button_active = $("#id_nav_btn_active");

// functions for button control
function enable_all() {
    button_delete.removeClass('disabled').removeClass('btn-default').addClass('btn-danger');
    button_edit.removeClass('disabled').removeClass('btn-default').addClass('btn-primary');
    button_duplicate.removeClass('disabled').removeClass('btn-default').addClass('btn-success');
    button_log_record.removeClass('disabled').removeClass('btn-default').addClass('btn-warning');
    button_movement.removeClass('disabled').removeClass('btn-default').addClass('btn-info');
    button_boxing.removeClass('disabled').removeClass('btn-default').addClass('btn-primary');
    button_barcode.removeClass('disabled').removeClass('btn-default').addClass('btn-info');
    button_password.removeClass('disabled').removeClass('btn-default').addClass('btn-info');
    button_active.removeClass('disabled').removeClass('btn-default').addClass('btn-success');
}

function disable_all(del) {
    if (!del) {
       button_delete.addClass('disabled').removeClass('btn-danger').addClass('btn-default');
    }
    button_edit.addClass('disabled').removeClass('btn-primary').addClass('btn-default');
    button_duplicate.addClass('disabled').removeClass('btn-success').addClass('btn-default');
    button_log_record.addClass('disabled').removeClass('btn-warning').addClass('btn-default');
    button_movement.addClass('disabled').removeClass('btn-info').addClass('btn-default');
    button_boxing.addClass('disabled').removeClass('btn-primary').addClass('btn-default');
    button_barcode.addClass('disabled').removeClass('btn-info').addClass('btn-default');
    button_password.addClass('disabled').removeClass('btn-info').addClass('btn-default');
    button_active.addClass('disabled').removeClass('btn-success').addClass('btn-default');
}

// click handling
$(table).find('tbody tr').mousedown (function(event) {
    count_selected = $('.selected').length;
    event.preventDefault();
    document.getSelection().removeAllRanges();
    index_selected_old = $(table).find('.selected').index();
    enable_all();
    if (event.ctrlKey) {
        if (count_selected === 0) {
            $(this).addClass('selected').css("background-color", table_row_color).attr('id', 'id_unique');
        } else {
            if ($(this).hasClass('selected')) {
                $(this).removeClass('selected').css("background-color", "").attr('id', '');
                count_selected = $('.selected').length;
                if (count_selected > 1) {
                    disable_all(true);
                } else if (count_selected === 1) {
                    enable_all();
                } else {
                    disable_all();
                }
            } else {
                $(this).addClass('selected').css("background-color", table_row_color);
                disable_all(true);
            }
        }
    } else if (event.shiftKey) {
        // all until next selected
        index_selected_actual = $(this).index();
        index_unique = $(table).find('#id_unique').index();
        // just click
        if (count_selected === 0) {
            $(this).addClass('selected').css("background-color", table_row_color).attr('id', 'id_unique');
        } else {
            // reduce
            if ($(this).hasClass('selected')) {
                // above
                if (index_selected_actual < index_unique) {
                    all_tr = $(this).prevAll('tr').addBack();
                    for (i = 0; i < index_selected_actual; i++) {
                        $(all_tr[i]).removeClass('selected').css("background-color", "");
                    }
                    disable_all(true);
                // below
                } else if (index_selected_actual > index_unique) {
                    all_tr = $(this).nextAll('tr').addBack();
                    for (i = 1; i < all_tr.length; i++) {
                        $(all_tr[i]).removeClass('selected').css("background-color", "");
                    }
                    disable_all(true);
                    // equal
                } else if (index_selected_actual === index_unique) {
                    $(this).siblings().removeClass('selected').css("background-color", "");
                    if (count_selected > 1) {
                        enable_all();
                    } else {
                        $(this).removeClass('selected').css("background-color", "").attr('id', '');
                        disable_all();
                    }
                }
            // add
            } else {
                // above
                if (index_selected_actual < index_selected_old) {
                    // first remove all below
                    all_tr = $(table).find('#id_unique').nextAll('tr');
                    for (i = 0; i < all_tr.length; i++) {
                        $(all_tr[i]).removeClass('selected').css("background-color", "");
                    }
                    // then add all above
                    all_tr = $(this).nextAll('tr').addBack();
                    for (i = 0; i < all_tr.length; i++) {
                        has_class = $(all_tr[i]).attr('class');
                        if (has_class !== 'selected') {
                            $(all_tr[i]).addClass('selected').css("background-color", table_row_color);
                        } else {
                            break;
                        }
                    }
                // below
                } else if (index_selected_actual > index_selected_old) {
                    // first remove all above
                    all_tr = $(table).find('#id_unique').prevAll('tr');
                    for (i = 0; i < index_unique; i++) {
                        $(all_tr[i]).removeClass('selected').css("background-color", "");
                    }
                    // then add all below
                    all_tr = $(this).prevAll('tr').addBack();
                    for (i = all_tr.length; i > 0; i--) {
                        has_class = $(all_tr[i]).attr('class');
                        if (has_class !== 'selected') {
                            $(all_tr[i]).addClass('selected').css("background-color", table_row_color);
                        } else {
                            break;
                        }
                    }
                }
            disable_all(true);
            }
        }
    } else {
        if ($(this).hasClass('selected')) {
            $(this).removeClass('selected').css("background-color", "").attr('id', '');
            count_selected = $('.selected').length;
            if (count_selected > 0) {
                $(this).addClass('selected').siblings().removeClass('selected').attr('id', '').css("background-color", "");
                $(this).css("background-color", table_row_color).attr('id', 'id_unique');
            } else {
                disable_all();
            }
        } else {
            $(this).addClass('selected').siblings().removeClass('selected').attr('id', '').css("background-color", "");
            $(this).css("background-color", table_row_color).attr('id', 'id_unique');
        }
    }
});