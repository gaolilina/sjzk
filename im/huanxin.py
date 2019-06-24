import json

import requests

from modellib.models.config import ServerConfig

JSON_HEADER = {'content-type': 'application/json'}
EASEMOB_HOST = "http://a1.easemob.com"

APP_ID = "1125190611181440"
APP_NAME = "chuangyihui"

CLIENT_ID = "YXA6itGt8IwVEem4S5WreGqDVA"
SECRET = "YXA6PxXmw-wSxMcGrYrjflRWRuY2wR4"

URL = EASEMOB_HOST + '/' + APP_ID + '/' + APP_NAME + '/'


def __refresh_access_token():
    url = URL + 'token'
    param = {
        "grant_type": "client_credentials",
        "client_id": CLIENT_ID,
        "client_secret": SECRET
    }
    response = requests.post(url, data=json.dumps(param), headers=JSON_HEADER)
    if response.status_code == requests.codes.ok:
        ServerConfig.objects.update(huanxin_token=response.json().get('access_token'))


def register_to_huanxin(userid, psd):
    url = URL + 'users'
    token = ServerConfig.objects.first().huanxin_token
    header = {
        **JSON_HEADER,
        'Authorization': "Bearer " + token
    }
    param = [
        {
            "username": userid,
            "password": psd,
        }
    ]
    response = requests.post(url, data=json.dumps(param), headers=header)
    if response.status_code == requests.codes.ok:
        return 200, response.json().get('entities')[0]
    elif response.status_code == 400:
        return response.status_code, response.json().get('error_description')
    elif response.status_code == 401:
        __refresh_access_token()
        return register_to_huanxin(userid, psd)
    else:
        return response.status_code, 'too fast'


def delete_user(userid):
    url = URL + 'users/' + userid
    token = ServerConfig.objects.first().huanxin_token
    header = {
        **JSON_HEADER,
        'Authorization': "Bearer " + token
    }
    response = requests.delete(url, headers=header)
    if response.status_code == requests.codes.ok:
        return 200, response.json().get('entities')[0]
    elif response.status_code == 400:
        return response.status_code, response.json().get('error_description')
    elif response.status_code == 401:
        __refresh_access_token()
        return delete_user(userid)
    else:
        return response.status_code, 'too fast'
