$(document).ready(function() {
    $('.top img').before('<div id="navbtn">≡</div>');

    // 主目录
    var str = $('.topbar ul li').toArray().map(function(e){
        var elem = $(e).find('a');
        return {
            url: elem.attr('href'),
            data: elem.html(),
            active: $(e).hasClass('active')
        }
    }).map(function(data){
        return "<li"+(data.active?" class='active'":"")+"><a href='"+data.url+"'>"+data.data+"</a></li>";
    }).join("");
    $('body').append("<ul id='mobilebar'>"+str+"</ul>");

    // 次目录
    var str2 = $('.leftbar ul li').toArray().map(function(e){
        var elem = $(e).find('a');
        return {
            url: elem.attr('href'),
            data: elem.html(),
            active: $(e).hasClass('active')
        }
    }).map(function(data){
        return "<li"+(data.active?" class='active'":"")+"><a href='"+data.url+"'>"+data.data+"</a></li>";
    }).join("");
    $('#mobilebar li.active').append("<ul id='mobilebar2'>"+str2+"</ul>");

    var width = $('#mobilebar').width();
    $('#mobilebar').css('left', '-'+width+'px');
    var mobilebarshow = false;

    $('#navbtn').click(function() {
        if (mobilebarshow) {
            mobilebarshow=false;
            $('#mobilebar').animate({left:'-'+width+'px'}, 200);
        } else {
            mobilebarshow=true;
            $('#mobilebar').animate({left:"0"}, 200);
        }
    });
});