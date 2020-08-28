import json

import requests
from im import *
from modellib.models.config import ServerConfig


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


def register_to_huanxin(userid, psd, nickname):
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
            "nickname": nickname,
        }
    ]
    response = requests.post(url, data=json.dumps(param), headers=header)
    if response.status_code == requests.codes.ok:
        return 200, response.json().get('entities')[0]
    elif response.status_code == 400:
        return response.status_code, response.json().get('error_description')
    elif response.status_code == 401:
        __refresh_access_token()
        return register_to_huanxin(userid, psd, nickname)
    else:
        return response.status_code, 'too fast'


def update_nickname(userid, nickname):
    url = URL + 'users/' + userid
    token = ServerConfig.objects.first().huanxin_token
    header = {
        **JSON_HEADER,
        'Authorization': "Bearer " + token
    }
    param = {
        "nickname": nickname,
    }

    response = requests.put(url, data=json.dumps(param), headers=header)
    if response.status_code == requests.codes.ok:
        return 200, response.json().get('entities')[0]
    elif response.status_code == 400:
        return response.status_code, response.json().get('error_description')
    else:
        return response.status_code, 'too fast'


def update_password(userid, psd):
    url = URL + 'users/' + userid + '/password'
    token = ServerConfig.objects.first().huanxin_token
    header = {
        **JSON_HEADER,
        'Authorization': "Bearer " + token
    }
    param = {
        "newpassword": psd,
    }

    response = requests.put(url, data=json.dumps(param), headers=header)
    return response.status_code


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