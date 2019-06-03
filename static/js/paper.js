var question_template = '<tr class="question">\
<td>问题{{num}}</td>\
<td>\
类型：<select onchange="javascript:question_gen()">\
    <option value="0">问答题</option>\
    <option value="1">单选题</option>\
    <option value="2">多选题</option>\
</select><input class="remove_question" type="button" value="删除" style="margin-top: 0px;" /><br/>\
标题：<input type="text" value="" style="margin-top: 0px;" /><br/>\
选项(多个选项用Enter分割)：<br><textarea width="300px" onchange="javascript:question_gen()" /></textarea><br/>\
</td>\
</tr>';

var type_arr = ['问题描述'];
var question_data = [];

function question_rerender() {
    $('.question').each(function(idx, elem) {
        $(elem).find('td:first-child').html('问题'+(idx+1));
    });
}

function question_gen(opt) {
    $('.remove_question').each(function(idx, elem) {
        if (elem.onclick == null) {
            elem.onclick = function() {
                $(elem).parents('tr').remove();
                question_count--;
                question_gen();
                question_rerender();
            }
        }
    });
    
    question_data = [];

    $('.question').each(function(idx, elem) {
        question_data.push({
            type: +$(elem).find('select').val(),
            title: $(elem).find('input:nth-of-type(2)').val(),
            options: $(elem).find('textarea:nth-of-type(1)').val().split('\n')
        });
    });
    $('input[name=questions]').val(JSON.stringify(question_data));
    if (!opt) {
        $('input[name=questions]').siblings('select').html("<option>" + question_data.map(function(d){
            return type_arr[d.type];
        }).join("</option><option>") + "</option");
        $('input[name=type]').val(question_data[0].type);
    }
}

$(document).ready(function() {
    $('#add_question').click(function() {
        var str = question_template.replace('{{num}}', question_count+1);
        $("table tr:nth-last-child(2)").before(str);
        question_count++;
        question_gen();
    });

    if ($('#add_question').length > 0) {
        question_gen(true);
    }
});