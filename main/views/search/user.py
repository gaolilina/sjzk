#! /usr/bin/env python3
# -*- coding: utf-8 -*-
from django import forms
from django.http import JsonResponse
from django.views.generic.base import View

from main.models import User
from util.decorator.param import validate_args


class SearchUser(View):
    ORDERS = ('time_created', '-time_created', 'name', '-name')

    @validate_args({
        'offset': forms.IntegerField(required=False, min_value=0),
        'limit': forms.IntegerField(required=False, min_value=0),
        'order': forms.IntegerField(required=False, min_value=0, max_value=3),
        'province': forms.CharField(required=False, max_length=20),
        'field': forms.CharField(required=False, max_length=20),
        'is_expert': forms.BooleanField(required=False),
        'name': forms.CharField(max_length=20, required=False),
        'tag': forms.CharField(max_length=20, required=False),
        'role': forms.CharField(max_length=20, required=False),
    })
    def get(self, request, offset=0, limit=10, order=1, province=None, field=None, is_expert=False, name=None,
            role=None, tag=None):
        """获取用户列表

        :param offset: 偏移量
        :param order: 排序方式
            0: 注册时间升序
            1: 注册时间降序（默认值）
            2: 昵称升序
            3: 昵称降序
        :return:
            count: 用户总数
            list: 用户列表
                id: 用户ID
                time_created: 注册时间
                username: 用户名
                name: 用户昵称
                icon_url: 用户头像
                tags: 标签
                gender: 性别
                liker_count: 点赞数
                follower_count: 粉丝数
                visitor_count: 访问数
                is_verified: 是否通过实名认证
                is_role_verified: 是否通过身份认证
        """
        condition = {}
        if province is not None:
            condition['province'] = province
        if field is not None:
            condition['adept_field'] = field
        if name is not None:
            condition['name__icontains'] = name
        if tag is not None:
            condition['tags__name__icontains'] = tag
        condition_expert = {
            'is_role_verified': 2,
            'role': '专家'
        }
        if is_expert:
            qs = User.enabled.filter(**condition).filter(**condition_expert)
        elif role:
            condition_expert['role'] = role
            qs = User.enabled.filter(**condition).filter(**condition_expert)
        else:
            qs = User.enabled.filter(**condition).exclude(**condition_expert)
        c = qs.count()
        users = qs.order_by(self.ORDERS[order])[offset:offset + limit]
        l = [{'id': u.id,
              'name': u.name,
              'gender': u.gender,
              'liker_count': u.likers.count(),
              'follower_count': u.followers.count(),
              'followed_count': u.followed_users.count() + u.followed_teams.count(),
              'visitor_count': u.visitors.count(),
              'icon_url': u.icon,
              'tags': [tag.name for tag in u.tags.all()],
              'is_verified': u.is_verified,
              'is_role_verified': u.is_role_verified,
              'time_created': u.time_created,
              'role': u.role,
              'username': u.username,
              } for u in users]
        return JsonResponse({'count': c, 'list': l})
