/**
 * Created by fanxn on 16/4/1.
 */

$(document).ready(function () {
});


$('#likes').click(function () {
    $.get("/rango/like_category/", {category_id: $(this).attr('data-catid')}, function (data) {
        $('#like_count').html(data);
        $('#likes').hide();
    });
});

$("#suggestion").keyup(function () {
    var query = $(this).val();
    $.get("/rango/suggest_category/", {suggestion: query}, function (data) {
        $("#cats").html(data);
    });
});

function add_page(name) {
    var cur_obj = $('[name="' + name + '"]');
    var rsltData = {
        url: cur_obj.attr("url"),
        name: name,
        catid: cur_obj.attr("catid")
    };

    $.get("/rango/auto_add_page/", rsltData, function () {
        cur_obj.hide();
    });
}