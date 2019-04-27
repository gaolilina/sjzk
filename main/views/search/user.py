#! /usr/bin/env python3
# -*- coding: utf-8 -*-
from django import forms
from django.db.models import Q
from django.http import JsonResponse
from django.views.generic.base import View

from main.models import User, UserAction
from main.utils import action
from main.utils.decorators import fetch_user_by_token, validate_args
from main.utils.recommender import calculate_ranking_score


class SearchUser(View):
    ORDERS = ('time_created', '-time_created', 'name', '-name')

    @validate_args({
        'offset': forms.IntegerField(required=False, min_value=0),
        'limit': forms.IntegerField(required=False, min_value=0),
        'order': forms.IntegerField(required=False, min_value=0, max_value=3),
        'by_tag': forms.IntegerField(required=False),
        'name': forms.CharField(max_length=20, required=False),
        'tag': forms.CharField(max_length=20, required=False),
    })
    def get(self, request, name, offset=0, limit=10, order=None, by_tag=0, **kwargs):
        """
        搜索用户

        :param offset: 偏移量
        :param limit: 数量上限
        :param order: 排序方式（若无则进行个性化排序）
            0: 注册时间升序
            1: 注册时间降序
            2: 昵称升序
            3: 昵称降序
        :param name: 用户名包含字段
        :param by_tag: 是否按标签检索

        :return:
            count: 用户总数
            list: 用户列表
                id: 用户ID
                name: 用户昵称
                icon_url: 用户头像
                gender: 性别
                like_count: 点赞数
                follower_count: 粉丝数
                followed_count: 关注的实体数
                visitor_count: 访问数
                tags: 标签
                is_verified: 是否实名认证
                is_role_verified: 是否通过身份认证
                time_created: 注册时间
        """
        i, j = offset, offset + limit
        if by_tag == 0:
            # 按用户昵称段检索
            condition = None
            if 'name' in kwargs:
                condition['name__icontains'] = kwargs['name']
            if 'tag' in kwargs:
                condition['tags__name__icontains'] = kwargs['tag']
            users = User.enabled.filter(**condition) if condition is not None else User.enabled.all()
        else:
            # 按标签检索
            users = User.enabled.filter(tags__name=name)
        c = users.count()
        if order is not None:
            users = users.order_by(self.ORDERS[order])[i:j]
        else:
            # 将结果进行个性化排序
            user_list = list()
            for u in users:
                if fetch_user_by_token(request):
                    user_list.append((u, calculate_ranking_score(request.user, u)))
                else:
                    user_list.append((u, 0))
            user_list = sorted(user_list, key=lambda x: x[1], reverse=True)
            users = (u[0] for u in user_list[i:j])
        l = [{'id': u.id,
              'name': u.name,
              'gender': u.gender,
              'like_count': u.likers.count(),
              'follower_count': u.followers.count(),
              'followed_count': u.followed_users.count() + u.followed_teams.count(),
              'visitor_count': u.visitors.count(),
              'icon_url': u.icon,
              'tags': [tag.name for tag in u.tags.all()],
              'is_verified': u.is_verified,
              'is_role_verified': u.is_role_verified,
              'time_created': u.time_created} for u in users]
        return JsonResponse({'count': c, 'list': l})


class SearchUserActionList(View):
    @validate_args({
        'offset': forms.IntegerField(required=False, min_value=0),
        'limit': forms.IntegerField(required=False, min_value=0),
        'name': forms.CharField(max_length=20),
        'tag': forms.CharField(max_length=20, required=False),
    })
    def get(self, request, offset=0, limit=10, **kwargs):
        """搜索与用户名或者动态名相关的动态列表

        :param offset: 偏移量
        :param limit: 数量上限
        :param kwargs: 搜索条件
            name: 用户名或动态名包含字段

        :return:
            count: 动态总数（包括标记为disabled的内容）
            last_time_created: 最近更新时间
            list: 动态列表
                action_id: 动态id
                id: 主语的id
                name: 主语的名称
                icon: 主语的头像
                action: 相关动作
                object_type: 相关对象的类型
                object_id: 相关对象的ID
                object_name: 相关对象名称
                icon_url: 头像
                related_object_type: 额外相关对象的类型
                related_object_id: 额外相关对象的ID
                related_object_name: 额外相关对象的名称
                liker_count: 点赞数
                comment_count: 评论数
                time_created: 创建时间
        """

        r = UserAction.objects.filter(Q(entity__name__icontains=kwargs['name'])
                                      | Q(action__icontains=kwargs['name']))
        c = r.count()
        records = (i for i in r[offset:offset + limit])
        l = [{'id': i.entity.id,
              'action_id': i.id,
              'name': i.entity.name,
              'icon': i.entity.icon,
              'action': i.action,
              'object_type': i.object_type,
              'object_id': i.object_id,
              'object_name': action.get_object_name(i),
              'icon_url': action.get_object_icon(i),
              'related_object_type': i.related_object_type,
              'related_object_id': i.related_object_id,
              'related_object_name': action.get_related_object_name(i),
              'liker_count': i.likers.count(),
              'comment_count': i.comments.count(),
              'time_created': i.time_created,
              } for i in records]
        return JsonResponse({'count': c, 'list': l})
