var stage_template = '<tr class="stage">\
<td>活动阶段{{num}}</td>\
<td>\
类　　型：<select onchange="javascript:stage_gen()">\
    <option value="0">前期宣传</option>\
    <option value="1">报名</option>\
    <option value="2">预赛</option>\
    <option value="3">周赛</option>\
    <option value="4">月赛</option>\
    <option value="5">中间赛</option>\
    <option value="6">结束</option>\
</select><input class="remove_stage" type="button" value="删除" style="margin-top: 0px;" /><br/>\
开始时间：<input type="text" data-field="date" readonly onchange="javascript:stage_gen()" /><br/>\
结束时间：<input type="text" data-field="date" readonly onchange="javascript:stage_gen()" /><br/>\
</td>\
</tr>';

var status_arr = ['前期宣传','报名','预赛','周赛','月赛','中间赛','结束'];
var stage_data = [];

function stage_rerender() {
    $('.stage').each(function(idx, elem) {
        $(elem).find('td:first-child').html('活动阶段'+(idx+1));
    });
}

function stage_gen(opt) {
    $('.remove_stage').each(function(idx, elem) {
        if (elem.onclick == null) {
            elem.onclick = function() {
                $(elem).parents('tr').remove();
                stage_count--;
                stage_gen();
                stage_rerender();
            }
        }
    });
    
    stage_data = [];

    $('.stage').each(function(idx, elem) {
        stage_data.push({
            status: +$(elem).find('select').val(),
            time_started: $(elem).find('input:nth-of-type(2)').val(),
            time_ended: $(elem).find('input:nth-of-type(3)').val()
        });
    });
    if (!opt) {
        $('input[name=stages]').val(JSON.stringify(stage_data));
        $('input[name=stages]').siblings('select').html("<option>" + stage_data.map(function(d){
            return status_arr[d.status];
        }).join("</option><option>") + "</option");
        $('input[name=status]').val(stage_data[0].status);
    }
}

$(document).ready(function() {
    $('#add_stage').click(function() {
        var str = stage_template.replace('{{num}}', stage_count+1);
        $("table tr:nth-last-child(2)").before(str);
        stage_count++;
        stage_gen();
        setDateTimePicker();
    });

    $('#status').change(function() {
        $('input[name=status]').val(stage_data[$('#status')[0].selectedIndex].status);
    });

    if ($('#add_stage').length > 0) {
        stage_gen(true);
    }
});