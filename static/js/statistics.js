const answers = {};
function show_statistics(paper_id,paper_name,paper_desc){
    var inner_html = '\
    <style>\
    #statistics{margin:30px 50px;}\
    p{font-size:1.05em;width:100%;padding:8px 10px;border-bottom:0.8px solid #C1C1C1;margin-bottom:5px;}\
    #questions p{padding-left:40px;}\
    .inline-block{display:inline-block;}\
    .title-bar{padding:8px 20px;margin-bottom:20px;font-size:14px;background-color:#E1FAFE;}\
    input[type="button"]{background-color:#55CE63;float:right;margin-right:20px;margin-top:-5px;;width:65px;height:30px;border:1px solid #55CE63;border-radius:3px;}\
    .c-blue{color:blue;}\
    .font-bold{font-weight:bold;}\
    .result{display:inline-block;margin:0 5px;}\
    </style>\
    <div id="statistics">\
    <p>问卷名称：'+paper_name+'</p>\
    <p>问卷描述：'+paper_desc+'</p>\
    <p id="question_count"></p>\
    <div id="questions"></div><br/>\
    <div class="title-bar">统计图表</div>\
    <div id="div-echarts"></div>\
    </div>\
    <div class="title-bar">统计表格<input type="button" id="export" value="导出"/></div>\
    <table style="width:1200px;margin:0 auto;">\
    <thead><tr>\
            <th class="min-width-50">序号</th>\
            <th class="min-width-150">问题名称</th>\
            <th class="min-width-80">问题类型</th>\
            <th class="min-width-150">选项</th>\
            <th class="min-width-80">统计(<i id="person_count"></i>人)</th>\
    </tr></thead>\
    <tbody id="statistics_body">\
        <tr>\
            <td rowspan="3">123</td>\
            <td rowspan="3">123</td>\
            <td>123</td>\
            <td>123</td>\
            <td>123</td>\
        </tr>\
        <tr>\
            <td>123</td>\
            <td>123</td>\
            <td>123</td>\
        </tr>\
        <tr>\
            <td>123</td>\
            <td>123</td>\
            <td>123</td>\
        </tr>\
    </tbody>\
    </table><br/>\
    <div class="title-bar">统计搜索</div>\
    <div style="width:1200px;margin:0 auto;">\
    选择问题：<select id="question_select"></select>&nbsp;&nbsp;&nbsp;\
    输入关键字：<input type="text" id="keyword"/>&nbsp;&nbsp;&nbsp;\
    <button class="btn" onclick="question_search()" style="margin-top:0;">搜索</button>\
    <br/><br/>\
    <div id="search_result">搜索结果</div>\
    <table id="table_search_result"></table>\
    </div>\
    \
    <br/><br/><br/><br/>\
    ';
    $('#main').html(inner_html);
    const type_list = ['问答题','单选题','多选题'];
    var statis_data = [];//用于生成统计表格
    var export_data = [];
    $.get(base_url+'admin/paper/'+paper_id+'/analysis/',{},function(data){
        // console.log(data);
        result = data.result;
        $('#question_count').html('问题：'+result.length);
        var echarts_data = [];
        var question_html = '';//问题详情
        var echarts_html = '';//echarts内容
        var statistics_html = '';//统计表格
        var question_select_html = '';//统计搜搜
        for(let ques_index in result){
            let question = result[ques_index];
            let options_html = '';
            if(question.type!=0){
                //统计数据
                let counts = question.analysis.count;
                let l_data = [];
                let s_data = [];
                let s_data_bar = [];
                let options = question.options;
                for(let op_index in options){
                    options_html += options[op_index]+'  ';
                    if(options[op_index]!=''){
                        l_data.push(options[op_index]);
                        s_data.push({'name':options[op_index],'value':counts[op_index]});
                        s_data_bar.push(counts[op_index]);
                    }
                }
                echarts_html += '<div id="div-echarts'+ques_index+'" style="width:560px;height:350px;margin-right:20px;margin-bottom:20px;" class="inline-block"></div>';
                echarts_html += '<div id="div2-echarts'+ques_index+'" style="width:560px;height:350px;margin-right:20px;margin-bottom:20px;" class="inline-block"></div>';
                echarts_data.push({
                    'type':'pie',
                    'id':'div-echarts'+ques_index,
                    'name':question.title,
                    'l_data':l_data,
                    's_data':s_data,
                });
                echarts_data.push({
                    'type':'bar',
                    'id':'div2-echarts'+ques_index,
                    'name':question.title,
                    'l_data':l_data,
                    's_data':s_data_bar,
                });
                statis_data = s_data;
                
            } else{
                question_select_html += '<option value="ques'+ques_index+'">'+question.title+'</option>';
                //统计数据
                let origins = question.analysis.origin;
                $('#person_count').html(origins.length);//总人数
                answers['ques'+ques_index] = origins;//用于统计搜索
                let s_data = [];
                let l_data_bar = [];
                let s_data_bar = [];
                let origin_counts = {};
                //统计问答题选项个数
                for(let o_index in origins){
                    if(origin_counts[origins[o_index]]==undefined)
                        origin_counts[origins[o_index]] = 1
                    else origin_counts[origins[o_index]] += 1;
                }
                for(let og in origin_counts){
                    s_data.push({'name':og,'value':origin_counts[og]});
                    l_data_bar.push(og);
                    s_data_bar.push(origin_counts[og]);
                }
                statis_data = s_data;
            }
            question_html += '<p>'+question.title+'：'+options_html+'</p>';
            let statis_data_length = statis_data.length;
            statistics_html += '<tr><td rowspan="'+statis_data_length+'">'+(ques_index*1+1)+'</td>\
            <td rowspan="'+statis_data_length+'">'+question.title+'</td>\
            <td rowspan="'+statis_data_length+'">'+type_list[question.type]+'</td>';
            for(let sd in statis_data){
                let pecent = (statis_data[sd].value/statis_data_length*100).toFixed(2);
                let tr = '<tr>';
                if(sd == 0) {
                    tr = '';
                    export_data.push(gen_question(ques_index*1+1,question.title,type_list[question.type],statis_data[sd].name,
                        statis_data[sd].value+'|'+pecent+'%'));
                    
                } else{
                    export_data.push(gen_question('','','',statis_data[sd].name,statis_data[sd].value+'|'+pecent+'%'));
                }
                statistics_html += tr+'<td>'+statis_data[sd].name+'</td>\
                <td>'+statis_data[sd].value+',<div class="c-blue font-bold result">'+pecent+'%</div></td></tr>';
            }
        }
        $('#div-echarts').html(echarts_html);
        $('#questions').html(question_html);
        for(let e_index in echarts_data){
            let echart = echarts_data[e_index];
            if(echart.type=='pie'){
                pie_echarts(echart.id,echart.name,echart.l_data,'',echart.s_data);
            } else{
                init_echarts(echart.id,echart.name,echart.type,'','',echart.l_data,echart.s_data);
            }
        }
        $('#statistics_body').html(statistics_html);
        $('#question_select').html(question_select_html);
    });
    $('#export').click(function(){
        let title = paper_name+'统计表格';
        JSONToCSVConvertor({data:export_data, title: title, showLabel: true});
    });
}
//生成问题对象
function gen_question(ques_index,title,type,option,statis){
    let question = {};
    question["序号"] = ques_index;
    question["问题名称"] = title;
    question["问题类型"] = type;
    question["选项"] = option;
    question["统计"] = statis;
    return question;
}
/*id,name,type,x,s*/
//type:line-折线图
//type:bar-柱状图
//e_boundaryGap:坐标轴两端空白
//init_echarts('div-echarts1','折线图','line','横轴','纵轴',[1,2,3,4],[9,12,55,24]);
//init_echarts('div-echarts2','柱形图','bar','横轴','纵轴',[1,2,3,4],[9,12,55,24]);
function init_echarts(div_echarts,e_name,e_type,x_name,y_name,x_data,s_data){
    // 基于准备好的dom，初始化echarts图表
    var e_boundaryGap = true;
    if(e_type=='line') e_boundaryGap = false;
    option = {
        title: {
            text: e_name,
            textStyle:{
                fontSize:12
            },
            left:'center',
            bottom:0
        },
        tooltip : {
            trigger: 'axis'
        },
        xAxis : [
            {
                type : 'category',
                boundaryGap : e_boundaryGap,
                name:x_name,
                data : x_data
            }
        ],
        yAxis : [
            {
                type : 'value',
                name:y_name,
                axisLabel:{
                    formatter: '{value}'
                },
            }
        ],
        series : [
            {
                name:'',
                type:e_type,
                //stack: '总量',
                data:s_data
            }
        ]
    };
    var myChart = echarts.init(document.getElementById(div_echarts));
    myChart.setOption(option);
}
//pie_echarts('div-echarts3','饼图',['name1','name2','name3'],'',[{name:'name1',value:1},{name:'name2',value:2},{name:'name3',value:3}]);
function pie_echarts(div_echarts,e_name,l_data,s_name,s_data){
    option = {
        title : {
            text: e_name,
            subtext: '各选项答题人数统计',
            left:'center',
            bottom:0
        },
        tooltip : {
            trigger: 'item',
            // formatter: "{a} <br/>{b} : {c} ({d}%)"
            formatter: "{b} : {c} ({d}%)"
        },
        legend: {
            type: 'scroll',
            orient: 'vertical',
            right: 10,
            top: 20,
            bottom: 20,
            data: l_data,
            // selected: {}
        },
        series : [
            {
                name: s_name,
                type: 'pie',
                radius : '55%',
                center: ['50%', '50%'],
                data: s_data,
                itemStyle: {
                    emphasis: {
                        shadowBlur: 10,
                        shadowOffsetX: 0,
                        shadowColor: 'rgba(0, 0, 0, 0.5)'
                    }
                }
            }
        ]
    };
    var myChart = echarts.init(document.getElementById(div_echarts));
    myChart.setOption(option);
}

function question_search(){
    var question_select = $('#question_select').val();
    var keyword = $('#keyword').val();
    if(keyword=="") {
        $('#search_result').html('请输入关键字');
        return;
    }
    let count = 0;
    let origins = answers[question_select];
    let length = origins.length;
    for(let o_index in origins){
        if(origins[o_index].indexOf(keyword)!=-1) count++;
    }
    let pecent = (count/length*100).toFixed(2);
    $('#search_result').html('包含关键字<div class="c-blue font-bold result">'+keyword+'</div>的回答共有\
        <div class="c-blue font-bold result">'+count+'</div>个，占比<div class="c-blue font-bold result">'+pecent+'%</div>');
}