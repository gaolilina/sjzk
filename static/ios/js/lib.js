var HOST = 'http://www.chuangyh.com:8000';

function ajax(method, url, params, other) {
    var dtd = $.Deferred();
    method({
        url: HOST + url,
        data: params,
        headers: readToken() == "" || readToken() == null ? undefined : {
            "X-User-Token": readToken()
        },
        ...other
    }).done(function (data) {
        dtd.resolve(data);
    }).fail(function (jqXHR, textStatus, errorThrown) {
        dtd.reject(jqXHR.status, errorThrown, jqXHR);
    });
    return dtd;
}

function get(url, params) {
    return ajax($.get, url, params);
}

function post(url, params) {
    return ajax($.post, url, params);
}

function postWithFile(url, formSelector) {
    return ajax($.post, url, new FormData(formSelector), {
        contentType: false,
        cache: false,
        processData: false,
    });
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
    }).done(function (data) {
        dtd.resolve(data);
    }).fail(function (jqXHR, textStatus, errorThrown) {
        dtd.reject(jqXHR.status, errorThrown, jqXHR);
    });
    return dtd;
}

function upload(url, file) {
    var dtd = $.Deferred();
    var data = new FormData();
    data.append("image", file);
    $.post({
        url: HOST + url,
        data: data,
        contentType: false,
        processData: false,
        headers: readToken() == "" || readToken() == null ? undefined : {
            "X-User-Token": readToken()
        }
    }).done(function (data) {
        dtd.resolve(data);
    }).fail(function (jqXHR, textStatus, errorThrown) {
        dtd.reject(jqXHR.status, errorThrown, jqXHR);
    });
    return dtd;
}

function uploadFile(url, fileName, file) {
    var dtd = $.Deferred();
    var data = new FormData();
    data.append(fileName, file);
    $.post({
        url: HOST + url,
        data: data,
        contentType: false,
        processData: false,
        headers: readToken() == "" || readToken() == null ? undefined : {
            "X-User-Token": readToken()
        }
    }).done(function (data) {
        dtd.resolve(data);
    }).fail(function (jqXHR, textStatus, errorThrown) {
        dtd.reject(jqXHR.status, errorThrown, jqXHR);
    });
    return dtd;
}

function saveToken(token) {
    localStorage.setItem("token", token);
}

function readToken() {
    return localStorage.getItem("token");
}

window.alertInfo = function (msg) {
    BootstrapDialog.show({
        title: '提示',
        message: msg,
        type: 'type-info'
    });
}

window.alert = function (msg) {
    BootstrapDialog.show({
        title: '提示',
        message: msg,
        type: 'type-danger'
    });
}

function errorHandler(code, msg, xhr) {
    switch (code) {
        case 400:
            alert(xhr.responseText || msg || '输入有误');
            break;
        case 403:
            alert(xhr.responseText || msg || '用户权限不足');
            break;
        default:
            alert(xhr.responseText || msg || '发生未知错误，请尝试注销后重新登陆');
            break;
    }
}
