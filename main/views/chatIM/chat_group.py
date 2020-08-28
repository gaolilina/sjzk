from django import forms
from django.http import JsonResponse
from django.views.generic import View

from util.decorator.param import validate_args, fetch_object
from util.decorator.auth import app_auth
from main.models import Team
from main.models import User
from im.chatgroups import *


__all__ = ['GroupManagement', 'MemberManagement']


class GroupManagement(View):
    @app_auth
    @validate_args({
        "group_name": forms.CharField(required=False, max_length=20),
        "desc": forms.CharField(required=False, max_length=100)
    })
    @fetch_object(Team.enabled, "team")
    def post(self, request, team, group_name='', desc=''):
        members = []
        rs = team.members.all()
        if group_name == '':
            group_name = team.name
        if desc == '':
            desc = team.description

        for item in rs:
            members.append(str(item.user.phone_number))
        code, desc = CreateChatGroups(group_name, desc, str(team.owner.phone_number), members)
        if code == 200:
            team.group_id = desc["groupid"]
            team.save()
            return JsonResponse({'code': 0, "desc": "创建成功"})
        else:
            print("=========", desc)
            return JsonResponse({'code': -1, "desc": "创建失败"})

    @app_auth
    @fetch_object(Team.enabled, "team")
    def delete(self, request, team):
        code, desc = DeleteChatGroups(team.group_id)
        if code == 200:
            team.group_id = ''
            team.save()
            return JsonResponse({'code': 0, "desc": "删除成功"})
        else:
            return JsonResponse({'code': -1, "desc": "删除失败"})



class MemberManagement(View):

    @app_auth
    @fetch_object(Team.enabled, "team")
    def get(self, request, team):
        userIdList = []
        ret = []
        code, data = GetChatGroupsMembers(team.group_id)
        if code == 200:
            for item in data:
                userIdList.append(item.get("member", ""))
            userList = User.enabled.filter(phone_number__in=userIdList)
            for user in userList:
                ret.append({
                    "im_id": user.phone_number,
                    "user_id": user.id,
                    "name": user.name
                })
            return JsonResponse({'code': 0, "size": len(ret), "list": ret})
        else:
            return JsonResponse({'code': -1, "desc": "查询失败"})

    @app_auth
    @fetch_object(Team.enabled, "team")
    @fetch_object(User.enabled, "user")
    def post(self, request, team, user):
        code, desc = AddUserToGroups(team.group_id, user.phone_number)
        if code == 200:
            return JsonResponse({'code': 0, "desc": "添加成功"})
        else:
            print(team.group_id, user.phone_number, desc)
            return JsonResponse({'code': -1, "desc": "添加失败"})


    @app_auth
    @fetch_object(Team.enabled, "team")
    @fetch_object(User.enabled, "user")
    def delete(self, request, team, user):
        code, desc = DeleteUserToGroups(team.group_id, user.phone_number)
        if code == 200:
            return JsonResponse({'code': 0, "desc": "删除成功"})
        else:
            return JsonResponse({'code': -1, "desc": "删除失败"})