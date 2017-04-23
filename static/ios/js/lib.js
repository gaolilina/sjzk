var HOST = 'http://www.chuangyh.com:8000';

function ajax(method, url, params) {
    var dtd = $.Deferred();
    method({
        url: HOST + url,
        data: params,
        headers: readToken() == "" || readToken() == null ? undefined : {
            "X-User-Token": readToken()
        }
    }).done(function(data) {
        dtd.resolve(data);
    }).fail(function(jqXHR, textStatus, errorThrown) {
        dtd.reject(jqXHR.status, errorThrown);
    });
    return dtd;
}

function get(url, params) {
    return ajax($.get, url, params);
}

function post(url, params) {
    return ajax($.post, url, params);
}

function deleteAjax(url, params) {
    var dtd = $.Deferred();
    $.ajax({
        url: HOST + url,
        data: params,
        type: 'DELETE',
        headers: readToken() == "" || readToken() == null ? undefined : {
            "X-User-Token": readToken()
        }
    }).done(function(data) {
        dtd.resolve(data);
    }).fail(function(jqXHR, textStatus, errorThrown) {
        dtd.reject(jqXHR.status, errorThrown);
    });
    return dtd;
}

function saveToken(token) {
    localStorage.setItem("token", token);
}

function readToken() {
    return localStorage.getItem("token");
}

window.alert = function(msg) {
    BootstrapDialog.show({
        title: 'Error',
        message: msg,
        type: 'type-danger'
    });
}

function errorHandler(code, msg) {
    switch (code) {
        case 400:
            alert('输入有误');
            break;
        case 403:
            alert('用户权限不足');
            break;
        default:
            if (msg == "") alert('发生未知错误，请尝试注销后重新登陆');
            else alert(msg);
            break;
    }
}
