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

function saveToken(token) {
    localStorage.setItem("token", token);
}

function readToken() {
    return localStorage.getItem("token");
}