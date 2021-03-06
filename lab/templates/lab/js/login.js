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


$('#id_user').focus();
function login() {
    var myDomElement = document.getElementById("id_form_login");
    var v_user = $(myDomElement).find("#id_user").val();
    var v_password = $(myDomElement).find("#id_password").val();
    $.ajax({
        method: "POST",
        url: "/" + "{{ content }}" + "/login/",
        data: {
            'user': v_user,
            'password': v_password
        },
        dataType: 'json',
        success: function (data) {
            if (!data.response) {
                handleErrorLogin(data.errors, data.form_id);
            } else {
                if (data.action === 'initial') {
                    showModalPassword(v_user);
                } else {
                    location.reload();
                }
            }
        }
    });
}

$("#id_submit_login").click(function () {
    login();
});

$('#id_form_login').keydown(function(e) {
    if (e.keyCode === 13) {
        login();
    }
});

function showModalPassword(v_user) {
    $('#id_modal_password').modal("show");
    $('#id_form_password').trigger("reset").find('#id_user').val(v_user);
}


$("#id_submit_password").click(function () {
    var myDomElement = document.getElementById("id_form_password");
    var v_user = $(myDomElement).find("#id_user").val();
    submitPassword(v_user);
});

$('#id_modal_password').keydown(function(e) {
    if (e.keyCode === 13) {
        var myDomElement = document.getElementById("id_form_password");
        var v_user = $(myDomElement).find("#id_user").val();
        submitPassword(v_user);
    }
}).on('shown.bs.modal', function () {
    $('#id_password_change').focus();
}).on('hidden.bs.modal', function () {
    $("br").remove();
    $("small").remove(".error");
});


function submitPassword(v_user) {
    var myDomElement = document.getElementById("id_form_password");
    var v_password = $(myDomElement).find("#id_password_change").val();
    var v_password_new = $(myDomElement).find("#id_password_new").val();
    var v_password_repeat = $(myDomElement).find("#id_password_repeat").val();
    $.ajax({
        method: "POST",
        url: "/" + "{{ content }}" + "/password/",
        data: {
            'user': v_user,
            'password_change': v_password,
            'password_new': v_password_new,
            'password_repeat': v_password_repeat
        },
        dataType: 'json',
        success: function (data) {
            if (!data.response) {
                handleError(data.errors, data.form_id);
            } else {
                location.reload();
            }
        }
    });
}
