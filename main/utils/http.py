import urllib.parse
import urllib.request
import json
import tencentyun

def send_message(data, m="GET"):
    """第三方短信调用api(云信)"""
    data['uid'] = 'zq353996852' # 填写“云信”账号的id
    data['pwd'] = 'c334c800ae8802557106fe09d70f3eb8' # 填写“云信”账号的密码
    data['ac'] = 'send'
    url = "http://api.sms.cn/sms/"
    params = urllib.parse.urlencode(data)
    if m == "GET":
        urllib.request.urlopen("%s?%s" % (url, params))
    else:
        urllib.request.urlopen(url, params)


def identity_verify(id_number, m="GET"):
    """第三方身份证验证api(聚合数据)"""
    appkey = 'b5b4cdc54bd373c66ed391d8ba1c5cc1' # 填写你申请的账号的appkey
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


def picture_verify(picture_url):
    """第三方图片审核api（万象优图）"""
    appid = "10072767"  # 项目ID
    secret_id = "AKIDfA6xfAidaKrGURP8kFxYzDH9oGVd6G7r"  # 密钥ID
    secret_key = "2GLE5oLgGhw1wgEftW2PZxDk8KOGwSlr"  # 密钥key

    image = tencentyun.ImageV2(appid, secret_id, secret_key)

    # upload an image from local file
    # obj = image.upload(sample_image_path);
    # or from in-memory binary data
    # both upload and upload_binary is ok in Python 3
    try:
        image_data = open(picture_url, "rb").read()
    except IOError:
        return None
    obj = image.upload_binary(image_data, 'chaungyi')  # 第二个参数为空间名称
    return obj["code"]
