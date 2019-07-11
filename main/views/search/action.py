#! /usr/bin/env python3
# -*- coding: utf-8 -*-
from django import forms
from django.db.models import Q
from django.http import JsonResponse
from django.views.generic import View

from main.models.action import UserAction, TeamAction, LabAction
from main.utils import action
from main.utils.decorators import validate_args


class SearchUserAction(View):
    @validate_args({
        'offset': forms.IntegerField(required=False, min_value=0),
        'limit': forms.IntegerField(required=False, min_value=0),
        'is_expert': forms.BooleanField(required=False),
        'name': forms.CharField(required=False, max_length=20),
        'tag': forms.CharField(max_length=20, required=False),
        'province': forms.CharField(required=False, max_length=20),
        'field': forms.CharField(required=False, max_length=20),
    })
    def get(self, request, offset=0, limit=10, is_expert=False, name=None, tag=None, province=None, field=None,
            **kwargs):
        """获取用户的动态列表

        :param offset: 偏移量
        :param limit: 数量上限
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

        # 获取主语是用户的动态
        obj = UserAction.objects
        if name is not None:
            obj = obj.filter(Q(entity__name__icontains=name) | Q(action__icontains=name))
        if tag is not None:
            obj = obj.filter(entity__tags__name__icontains=tag)
        if province is not None:
            obj = obj.filter(entity__province=province)
        if field is not None:
            obj = obj.filter(entity__adept_field=field)
        condition_expert = {
            'entity__is_role_verified': 2,
            'entity__role': '专家'
        }
        if is_expert:
            obj = obj.filter(**condition_expert)
        else:
            obj = obj.exclude(**condition_expert)
        c = obj.count()
        records = (i for i in obj.all()[offset:offset + limit])
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


class SearchTeamAction(View):
    @validate_args({
        'offset': forms.IntegerField(required=False, min_value=0),
        'limit': forms.IntegerField(required=False, min_value=0),
        'name': forms.CharField(required=False, max_length=20),
        'province': forms.CharField(required=False, max_length=20),
        'field': forms.CharField(required=False, max_length=20),
    })
    def get(self, request, name=None, offset=0, limit=10, province=None, field=None, **kwargs):
        """获取团队的动态列表

        :param offset: 偏移量
        :param limit: 数量上限
        :return:
            count: 动态总数（包括标记为disabled的内容）
            last_time_created: 最近更新时间
            list: 动态列表
                id: 主语的id
                action_id: 动态id
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
        qs = TeamAction.objects.filter(Q(entity__name__icontains=name) | Q(action__icontains=name))
        if province is not None:
            qs = qs.filter(entity__province=province)
        if field is not None:
            qs = qs.filter(entity__field1=field)
        # 获取主语是团队的动态
        c = qs.count()
        records = (i for i in qs[offset:offset + limit])
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


class SearchLabAction(View):
    @validate_args({
        'offset': forms.IntegerField(required=False, min_value=0),
        'limit': forms.IntegerField(required=False, min_value=0),
        'name': forms.CharField(required=False, max_length=20),
        'province': forms.CharField(required=False, max_length=20),
        'field': forms.CharField(required=False, max_length=20),
    })
    def get(self, request, offset=0, limit=10, province=None, field=None, **kwargs):
        """搜索与团队名或者动态名相关的动态列表

        :param offset: 偏移量
        :param limit: 数量上限
        :param kwargs: 搜索条件
            name: 团队或动态名包含字段

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

        r = LabAction.objects.filter(Q(entity__name__icontains=kwargs['name'])
                                     | Q(action__icontains=kwargs['name']))
        if province is not None:
            r = r.filter(entity__province=province)
        if field is not None:
            r = r.filter(entity__field1=field)
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
