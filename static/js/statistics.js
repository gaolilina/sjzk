function show_statistics(paper_id,paper_name,paper_desc){
    var inner_html = '\
    <style>\
    #statistics{margin:30px 50px;}\
    p{font-size:1.05em;width:100%;padding:8px 10px;border-bottom:0.8px solid #C1C1C1;margin-bottom:5px;}\
    #questions p{padding-left:40px;}\
    .inline-block{display:inline-block;}\
    </style>\
    <div id="statistics">\
    <p>问卷名称：'+paper_name+'</p>\
    <p>问卷描述：'+paper_desc+'</p>\
    <p id="question_count"></p>\
    <div id="questions"></div><br/>\
    <div id="div-echarts"></div>\
    </div>\
    ';
    $('#main').html(inner_html);
    $.get(base_url+'admin/paper/'+paper_id+'/analysis/',{},function(data){
        // console.log(data);
        result = data.result;
        $('#question_count').html('问题：'+result.length);
        var echarts_data = [];
        var question_html = '';//问题详情
        var echarts_html = '';//echarts内容
        for(let ques_index in result){
            let question = result[ques_index];
            let options_html = '';
            if(question.type!=0){
                //统计数据
                let counts = question.analysis.count;
                let l_data = [];
                let s_data = [];
                let options = question.options;
                for(let op_index in options){
                    options_html += options[op_index]+'  ';
                    if(options[op_index]!=''){
                        l_data.push(options[op_index]);
                        s_data.push({'name':options[op_index],'value':counts[op_index]});
                    }
                }
                echarts_html += '<div id="div-echarts'+ques_index+'" style="width:560px;height:350px;margin-right:20px;margin-bottom:20px;" class="inline-block"></div>';
                echarts_data.push({
                    'type':'pie',
                    'id':'div-echarts'+ques_index,
                    'name':question.title,
                    'l_data':l_data,
                    's_data':s_data,
                });
            } else{
                //统计数据
                let origins = question.analysis.origin;
                let s_data = [];
                let origin_counts = {};
                //统计问答题选项个数
                for(let o_index in origins){
                    if(origin_counts[origins[o_index]]==undefined)
                        origin_counts[origins[o_index]] = 1
                    else origin_counts[origins[o_index]] += 1;
                }
                for(let og in origin_counts){
                    s_data.push({'name':og,'value':origin_counts[og]});
                }
                echarts_html += '<div id="div-echarts'+ques_index+'" style="width:560px;height:350px;margin-right:20px;margin-bottom:20px;" class="inline-block"></div>';
                echarts_data.push({
                    'type':'pie',
                    'id':'div-echarts'+ques_index,
                    'name':question.title,
                    'l_data':origins,
                    's_data':s_data,
                });
            }
            question_html += '<p>'+question.title+'：'+options_html+'</p>';
        }
        $('#div-echarts').html(echarts_html);
        $('#questions').html(question_html);
        for(let e_index in echarts_data){
            let echart = echarts_data[e_index];
            if(echart.type=='pie'){
                pie_echarts(echart.id,echart.name,echart.l_data,'',echart.s_data);
            } else{
                // init_echarts(echart.id,echart.name,echart.type,'','',[],[])
            }
        }
    });
}
/*id,name,type,x,s*/
//type:line-折线图
//type:bar-柱状图
//e_boundaryGap:坐标轴两端空白
//init_echarts('div-echarts1','折线图','line','横轴','纵轴',[1,2,3,4],[9,12,55,24]);
//init_echarts('div-echarts2','柱形图','bar','横轴','纵轴',[1,2,3,4],[9,12,55,24]);
function init_echarts(div_echarts,e_name,e_type,x_name,y_name,x_data,s_data){
    // 基于准备好的dom，初始化echarts图表
    var e_boundaryGap = false;
    if(type=='line') e_boundaryGap = true;
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
