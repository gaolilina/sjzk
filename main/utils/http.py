import urllib.parse, http.client
import urllib.request
import json
import tencentyun
from qcloud_image import Client
from qcloud_image import CIUrls


def identity_verify(id_number, real_number, m="GET"):
    """第三方身份证实名认证api(聚合数据)"""
    appkey = '778643c12a1bc37c78ba2463c91745a8'  # 填写你申请的账号的appkey
    url = "http://op.juhe.cn/idcard/query"
    params = {
        "idcard": id_number,  # 身份证号码
        "realname": real_number,  # 真实姓名
        "key": appkey,  # 申请的appkey
    }
    params = urllib.parse.urlencode(params)
    if m == "GET":
        f = urllib.request.urlopen("%s?%s" % (url, params))
    else:
        f = urllib.request.urlopen(url, params)
    content = f.read().decode('utf-8')
    res = json.loads(content)
    if res['error_code'] == 0:
        if res['result']['res'] == 1:
            return 1
        else:
            return 0
    else:
        return 0


def picture_verify(picture):
    """第三方图片审核api（万象优图）"""
    appid = "10072767"  # 项目ID
    secret_id = "AKIDZBf2DdSCLNoAPXvH4kHeq2AHF1bz4b9a"  # 密钥ID
    secret_key = "1xjPxMjx4zsfGICvyvg4MX5cHAAze9Xp"  # 密钥key
    bucket = 'chuangyi'  # 图片空间名称
    image = tencentyun.ImageV2(appid, secret_id, secret_key)
    try:
        # image_data = open(picture_url, "rb").read()
        # 将图片上传到图片空间
        obj = image.upload_binary(picture, bucket)  # 第二个参数为空间名称
        if obj["code"] == 0:
            fileid = obj["data"]["fileid"]
            download_url = obj["data"]["download_url"]
            # 图片检测
            client = Client(appid, secret_id, secret_key, bucket)
            client.use_http()
            client.set_timeout(30)
            pornRet = client.porn_detect(CIUrls([download_url]))
            image.delete(bucket, fileid)
            return pornRet["result_list"][0]["data"]["result"]
    except IOError:
        return None


def eid_verify(data):
    """调用eID接口进行认证"""
    url = "127.0.0.1"
    data = json.dumps(data)
    headers = {"Content-type": "application/json"}
    conn = http.client.HTTPConnection(url, 8080)
    conn.request('POST', '/apserver/login', data, headers)
    response = conn.getresponse()
    content = response.read().decode('utf-8')
    res = json.loads(content)
    if res['result'] == "00":
        return 1
    else:
        return int(res['result_detail'])


def notify_user(user, msg):
    """调用个推通知"""
    if user.getui_id != "":
        url = "127.0.0.1"
        data = "client=" + user.getui_id + "&msg=" + msg
        conn = http.client.HTTPConnection(url, 7999)
        conn.request('POST', '/index.php', data)
        response = conn.getresponse()
