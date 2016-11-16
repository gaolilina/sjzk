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
    secret_id = "AKIDZBf2DdSCLNoAPXvH4kHeq2AHF1bz4b9a"  # 密钥ID
    secret_key = "1xjPxMjx4zsfGICvyvg4MX5cHAAze9Xp"  # 密钥key
    bucket = 'chuangyi'  # 图片空间名称
    image = tencentyun.ImageV2(appid, secret_id, secret_key)
    try:
        image_data = open(picture_url, "rb").read()
    except IOError:
        return None
    # 将图片上传到图片空间
    obj = image.upload_binary(image_data, bucket)  # 第二个参数为空间名称
    if obj["code"] == 0:
        fileid = obj["data"]["fileid"]
        download_url = obj["data"]["download_url"]
        # 图片检测
        imageprocess = tencentyun.ImageProcess(appid,secret_id,secret_key,bucket)
        pornUrl = download_url
        pornRet = imageprocess.porn_detect(pornUrl)
        image.delete(bucket, fileid)
        return pornRet["data"]["result"]
