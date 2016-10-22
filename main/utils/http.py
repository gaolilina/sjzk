import urllib.parse
import urllib.request
import json


def send_message(data, m="GET"):
    # 填写“云信”账号的id和密码
    data['uid'] = 'zq353996852'
    data['pwd'] = 'c334c800ae8802557106fe09d70f3eb8'
    data['ac'] = 'send'
    url = "http://api.sms.cn/sms/"
    params = urllib.parse.urlencode(data)
    if m == "GET":
        urllib.request.urlopen("%s?%s" % (url, params))
    else:
        urllib.request.urlopen(url, params)


def identity_verify(id_number, m="GET"):
    # 填写你申请的账号的appkey
    appkey = 'b5b4cdc54bd373c66ed391d8ba1c5cc1'
    url = "http://apis.juhe.cn/idcard/index"
    params = {
        "cardno": id_number,  # 身份证号码
        "dtype": "json",  # 返回数据格式：json或xml,默认json
        "key": appkey,  # 申请的appkey
    }
    params = urllib.parse.urlencode(params)
    if m == "GET":
        f = urllib.request.urlopen("%s?%s" % (url, params))
    else:
        f = urllib.request.urlopen(url, params)
    content = f.read().decode('utf-8')
    res = json.loads(content)
    return res
