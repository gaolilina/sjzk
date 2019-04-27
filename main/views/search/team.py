#! /usr/bin/env python3
# -*- coding: utf-8 -*-
from django import forms
from django.db.models import Q
from django.http import JsonResponse
from django.views.generic.base import View

from main.models import TeamAction, Team
from main.utils import action
from main.utils.decorators import fetch_user_by_token, validate_args
from main.utils.recommender import calculate_ranking_score


class SearchTeam(View):
    ORDERS = ('time_created', '-time_created', 'name', '-name')

    @validate_args({
        'offset': forms.IntegerField(required=False, min_value=0),
        'limit': forms.IntegerField(required=False, min_value=0),
        'order': forms.IntegerField(required=False, min_value=0, max_value=3),
        'by_tag': forms.IntegerField(required=False),
        'name': forms.CharField(max_length=20, required=False),
        'tag': forms.CharField(max_length=20, required=False),
    })
    def get(self, request, name, offset=0, limit=10, order=1, by_tag=0, **kwargs):
        """搜索团队
        :param offset: 偏移量
        :param limit: 数量上限
        :param order: 排序方式（若无则进行个性化排序）
            0: 注册时间升序
            1: 注册时间降序
            2: 昵称升序
            3: 昵称降序
        :param name: 团队名包含字段
        :param by_tag: 是否按标签检索

        :return:
            count: 团队总数
            list: 团队列表
                id: 团队ID
                name: 团队名
                icon_url: 头像
                owner_id: 创建者ID
                liker_count: 点赞数
                visitor_count: 最近7天访问数
                member_count: 团队成员人数
                fields: 所属领域，格式：['field1', 'field2']
                tags: 标签，格式：['tag1', 'tag2', ...]
                time_created: 注册时间
        """
        i, j = offset, offset + limit
        if by_tag == 0:
            # 按团队名称段检索
            condition = None
            if 'name' in kwargs:
                condition['name__icontains'] = kwargs['name']
            if 'tag' in kwargs:
                condition['tags__name__icontains'] = kwargs['tag']
            teams = Team.enabled.filter(**condition) if condition is not None else Team.enabled.all()
        else:
            # 按标签检索
            teams = Team.enabled.filter(tags__name=name)
        c = teams.count()
        if order is not None:
            teams = teams.order_by(self.ORDERS[order])[i:j]
        else:
            # 将结果进行个性化排序
            team_list = list()
            for t in teams:
                if fetch_user_by_token(request):
                    team_list.append((t, calculate_ranking_score(request.user, t)))
                else:
                    team_list.append((t, 0))
            team_list = sorted(team_list, key=lambda x: x[1], reverse=True)
            teams = (t[0] for t in team_list[i:j])
        l = [{'id': t.id,
              'name': t.name,
              'icon_url': t.icon,
              'owner_id': t.owner.id,
              'liker_count': t.likers.count(),
              'visitor_count': t.visitors.count(),
              'member_count': t.members.count(),
              'fields': [t.field1, t.field2],
              'tags': [tag.name for tag in t.tags.all()],
              'time_created': t.time_created} for t in teams]
        return JsonResponse({'count': c, 'list': l})


class SearchTeamActionList(View):
    @validate_args({
        'offset': forms.IntegerField(required=False, min_value=0),
        'limit': forms.IntegerField(required=False, min_value=0),
        'name': forms.CharField(max_length=20),
    })
    def get(self, request, offset=0, limit=10, **kwargs):
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

        r = TeamAction.objects.filter(Q(entity__name__icontains=kwargs['name'])
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
