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



def CreateChatGroups(group_name, desc, owner, members):
    url = URL + "chatgroups/"

    token = ServerConfig.objects.first().huanxin_token
    header = {
        **JSON_HEADER,
        'Authorization': "Bearer " + token
    }
    param = {
            "groupname": group_name,
            "desc": desc,
            "public": False,
            "allowinvites": True,
            "owner": owner,
            "members": members,
        }

    response = requests.post(url, data=json.dumps(param), headers=header)
    if response.status_code == requests.codes.ok:
        return 200, response.json().get('data')
    elif response.status_code == 400:
        return response.status_code, response.json().get('error_description')
    elif response.status_code == 401:
        __refresh_access_token()
        return CreateChatGroups(group_name, desc, owner, members)
    else:
        return response.status_code, 'too fast'


def JoinedChatGroups(username):
    url = URL + "users/" + username + "/joined_chatgroups"

    token = ServerConfig.objects.first().huanxin_token
    header = {
        **JSON_HEADER,
        'Authorization': "Bearer " + token
    }

    response = requests.get(url, headers=header)
    if response.status_code == requests.codes.ok:
        return 200, response.json().get('data')
    elif response.status_code == 400:
        return response.status_code, response.json().get('error_description')
    elif response.status_code == 401:
        __refresh_access_token()
        return JoinedChatGroups(username)
    else:
        return response.status_code, 'too fast'


def DeleteChatGroups(group_id):
    url = URL + "chatgroups/" + group_id

    token = ServerConfig.objects.first().huanxin_token
    header = {
        **JSON_HEADER,
        'Authorization': "Bearer " + token
    }

    response = requests.delete(url, headers=header)
    if response.status_code == requests.codes.ok:
        return 200, response.json().get('data')
    elif response.status_code == 400:
        return response.status_code, response.json().get('error_description')
    elif response.status_code == 401:
        __refresh_access_token()
        return DeleteChatGroups(group_id)
    else:
        return response.status_code, 'too fast'

def GetChatGroupsMembers(group_id):
    url = URL + "chatgroups/"+ group_id + "/users"

    token = ServerConfig.objects.first().huanxin_token
    header = {
        **JSON_HEADER,
        'Authorization': "Bearer " + token
    }

    response = requests.get(url, headers=header)
    if response.status_code == requests.codes.ok:
        return 200, response.json().get('data')
    elif response.status_code == 400:
        return response.status_code, response.json().get('error_description')
    elif response.status_code == 401:
        __refresh_access_token()
        return DeleteChatGroups(group_id)
    elif response.status_code == 404:
        return response.status_code, "群组不存在"
    else:
        return response.status_code, 'too fast'


def AddUserToGroups(group_id, user_name):
    url = URL + "chatgroups/" + group_id + "/users/" + user_name

    token = ServerConfig.objects.first().huanxin_token
    header = {
        **JSON_HEADER,
        'Authorization': "Bearer " + token
    }

    response = requests.post(url, headers=header)
    if response.status_code == requests.codes.ok:
        return 200, response.json().get('data')
    elif response.status_code == 400:
        return response.status_code, response.json().get('error_description')
    elif response.status_code == 401:
        __refresh_access_token()
        return DeleteChatGroups(group_id)
    elif response.status_code == 404:
        return response.status_code, "用户不存在或已添加"
    else:
        return response.status_code, 'too fast'


def DeleteUserToGroups(group_id, user_name):
    url = URL + "chatgroups/" + group_id + "/users/" + user_name

    token = ServerConfig.objects.first().huanxin_token
    header = {
        **JSON_HEADER,
        'Authorization': "Bearer " + token
    }

    response = requests.delete(url, headers=header)
    if response.status_code == requests.codes.ok:
        return 200, response.json().get('data')
    elif response.status_code == 400:
        return response.status_code, response.json().get('error_description')
    elif response.status_code == 401:
        __refresh_access_token()
        return DeleteChatGroups(group_id)
    elif response.status_code == 404:
        return response.status_code, "群组不存在"
    else:
        return response.status_code, 'too fast'