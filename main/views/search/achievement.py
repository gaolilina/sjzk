#! /usr/bin/env python3
# -*- coding: utf-8 -*-

# noinspection PyUnusedLocal
from django import forms
from django.http import JsonResponse
from django.views.generic.base import View

from main.models import Achievement
from main.models import Team
from main.models import User
from main.utils import deal_tags
from util.decorator.auth import app_auth
from util.decorator.param import validate_args, fetch_object


class SearchAllUserAchievement(View):
    ORDERS = ('time_created', '-time_created')

    @app_auth
    @validate_args({
        'offset': forms.IntegerField(required=False, min_value=0),
        'limit': forms.IntegerField(required=False, min_value=0),
        'order': forms.IntegerField(required=False, min_value=0, max_value=3),
        'description': forms.CharField(max_length=256, required=False),
    })
    def get(self, request, description='', offset=0, limit=10, order=1):
        """获取所有用户发布的成果

        :param offset: 偏移量
        :param limit: 数量上限
        :param order: 排序方式
            0: 发布时间升序
            1: 发布时间降序（默认值）
        :return:
            count: 成果总数
            list: 成果列表
                id: 成果ID
                user_id: 团队ID
                user_name: 团队名称
                icon_url: 团队头像
                description: 成果描述
                picture: 图片
                time_created: 发布时间
        """
        # 获取当前用户好友id.
        userIds = []
        for item in request.user.friends.all():
            userIds.append(str(item.other_user.id))
        userIds.append(str(request.user.id))
        i, j, k = offset, offset + limit, self.ORDERS[order]

        achievements = Achievement.objects.filter(team=None, description__icontains=description).order_by(k)
        c = achievements.count()
        achievements = achievements[i:j]
        l = [{'id': a.id,
              'name': a.name,
              'user_id': a.user.id,
              'user_name': a.user.real_name if str(a.user.id) in userIds and a.user.real_name != '' else a.user.name,
              'icon_url': a.user.icon,
              'description': a.description,
              'tags': deal_tags(a.tags),
              'picture': a.picture,
              'time_created': a.time_created,
              'yes_count': a.likers.count(),
              'is_yes': request.user in a.likers.all(),
              'require_count': a.requirers.count(),
              'is_require': request.user in a.requirers.all(),
              } for a in achievements]
        return JsonResponse({'count': c, 'list': l, 'code': 0})


class SearchAllTeamAchievement(View):
    ORDERS = ('time_created', '-time_created')

    @app_auth
    @validate_args({
        'offset': forms.IntegerField(required=False, min_value=0),
        'limit': forms.IntegerField(required=False, min_value=0),
        'order': forms.IntegerField(required=False, min_value=0, max_value=3),
        'description': forms.CharField(max_length=256, required=False),
    })
    def get(self, request, description='', offset=0, limit=10, order=1):
        """获取所有团队发布的成果

        :param offset: 偏移量
        :param limit: 数量上限
        :param order: 排序方式
            0: 发布时间升序
            1: 发布时间降序（默认值）
        :return:
            count: 成果总数
            list: 成果列表
                id: 成果ID
                team_id: 团队ID
                team_name: 团队名称
                icon_url: 团队头像
                description: 成果描述
                picture: 图片
                time_created: 发布时间
        """
        i, j, k = offset, offset + limit, self.ORDERS[order]

        # 团队成果，要 team 非空
        achievements = Achievement.objects.filter(team__isnull=False, description__icontains=description).order_by(k)
        c = achievements.count()
        achievements = achievements[i:j]
        l = [{'id': a.id,
              'name': a.name,
              'team_id': a.team.id,
              'team_name': a.team.name,
              'icon_url': a.team.icon,
              'description': a.description,
              'tags': deal_tags(a.tags),
              'picture': a.picture,
              'yes_count': a.likers.count(),
              'is_yes': request.user in a.likers.all(),
              'require_count': a.requirers.count(),
              'is_require': request.user in a.requirers.all(),
              'time_created': a.time_created} for a in achievements]
        return JsonResponse({'count': c, 'list': l, 'code': 0})



class SearchUserAchievement(View):

    @app_auth
    @fetch_object(User.objects, "user")
    def get(self, request, user):
        """获取用户发布的成果
        :return:
            count: 成果总数
            list: 成果列表
                id: 成果ID
                user_id: 团队ID
                user_name: 团队名称
                icon_url: 团队头像
                description: 成果描述
                picture: 图片
                time_created: 发布时间
        """
        # 获取当前用户好友id.
        userIds = []
        for item in request.user.friends.all():
            userIds.append(str(item.other_user.id))
        userIds.append(str(request.user.id))

        achievements = user.achievements.all()
        c = achievements.count()
        l = [{'id': a.id,
              'name': a.name,
              'user_id': a.user.id,
              'user_name': a.user.real_name if str(a.user.id) in userIds and a.user.real_name != '' else a.user.name,
              'icon_url': a.user.icon,
              'description': a.description,
              'tags': deal_tags(a.tags),
              'picture': a.picture,
              'time_created': a.time_created,
              'yes_count': a.likers.count(),
              'is_yes': request.user in a.likers.all(),
              'require_count': a.requirers.count(),
              'is_require': request.user in a.requirers.all(),
              } for a in achievements]
        return JsonResponse({'count': c, 'list': l, 'code': 0})

class SearchTeamAchievement(View):
    @app_auth
    @fetch_object(Team.objects, "team")
    def get(self, request, team):
        """获取指定团队发布的成果
        :return:
            count: 成果总数
            list: 成果列表
                id: 成果ID
                team_id: 团队ID
                team_name: 团队名称
                icon_url: 团队头像
                description: 成果描述
                picture: 图片
                time_created: 发布时间
        """

        # 团队成果，要 team 非空
        achievements = team.achievements.all()
        c = achievements.count()
        l = [{'id': a.id,
              'name': a.name,
              'team_id': a.team.id,
              'team_name': a.team.name,
              'icon_url': a.team.icon,
              'description': a.description,
              'tags': deal_tags(a.tags),
              'picture': a.picture,
              'yes_count': a.likers.count(),
              'is_yes': request.user in a.likers.all(),
              'require_count': a.requirers.count(),
              'is_require': request.user in a.requirers.all(),
              'time_created': a.time_created} for a in achievements]
        return JsonResponse({'count': c, 'list': l, 'code': 0})