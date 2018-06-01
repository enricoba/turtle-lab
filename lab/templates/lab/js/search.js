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


var id_search = $('#id_search');

// perform search if search box not empty
if (id_search.val().length > 0) {
    search(id_search, "init");
}

id_search.focus().keyup(function() {
    search(this, "regular");
});

function search(id_search, call) {
    var td, i, x, finder, keyword;
    var row = $('#id_table > tbody > tr');
    var th_count = $('#id_table_head > thead > tr > th').length;

    // for loop for rows
    for (i = 0; i < row.length; i++) {
        finder = 0;
        //for loop for column
        for (x = 0; x < th_count; x++) {
            // define field
            td = row[i].getElementsByTagName("td")[x];
            if (td) {
                if (call === "init") {
                    keyword = id_search.val();
                } else {
                    keyword = id_search.value;
                }
                if (td.innerHTML.indexOf(keyword) > -1) {
                    finder++;
                }
            }
        }
        // hide if no hit
        if (finder > 0) {
            row[i].style.display = "";
            $('#id_search_error').hide();
        } else {
            row[i].style.display = "none";
        }
    }

    var count = row.filter(function() {
        return $(this).css('display') !== 'none';
    }).length;
    if (count === 0) {
        $('#id_search_error').show();
    }
}
