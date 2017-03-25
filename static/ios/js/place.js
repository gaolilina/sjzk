window.cy_location = null;
window.cy_school = null;

$.get({
    url: "http://www.chuangyh.com/json/cy_location.txt"
}).done(function(data) {
    data = window.cy_location = JSON.parse(data);

    $('select[name=province]').html(genOptions(data));
});
$.get({
    url: "http://www.chuangyh.com/json/cy_school.txt"
}).done(function(data) {
    data = window.cy_school = JSON.parse(data);
});

function genOptions(data) {
    if (typeof data === "string" || data == null) return '<option value=""></option>';

    var arr = Array.isArray(data) ? data : Object.keys(data);
    return '<option value=""></option>' + arr.map(function(d) {
        return '<option value="' + d + '">' + d + '</option>';
    }).join('');
}

$('select[name=province]').change(function() {
    $('select[name=city]').html(genOptions(cy_location[$(this).val()]));
    $('select[name=county]').html(genOptions(""));

    if (cy_school)
        $('select[name=unit1]').html(genOptions(cy_school[$(this).val()]));
});

$('select[name=city]').change(function() {
    $('select[name=county]').html(genOptions(cy_location[$('select[name=province]').val()][$(this).val()]));
});