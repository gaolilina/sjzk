#! /usr/bin/env python3
# -*- coding: utf-8 -*-
from django import forms
from django.http import JsonResponse
from django.views.generic.base import View

from main.models import Lab
from main.utils.decorators import fetch_user_by_token
from util.decorator.param import validate_args
from main.utils.recommender import calculate_ranking_score


class SearchLab(View):
    ORDERS = ('time_created', '-time_created', 'name', '-name')

    @validate_args({
        'offset': forms.IntegerField(required=False, min_value=0),
        'limit': forms.IntegerField(required=False, min_value=0),
        'order': forms.IntegerField(required=False, min_value=0, max_value=3),
        'by_tag': forms.IntegerField(required=False),
        'name': forms.CharField(max_length=20),
    })
    def get(self, request, name, offset=0, limit=10, order=1, by_tag=0):
        """搜索实验室
        :param offset: 偏移量
        :param limit: 数量上限
        :param order: 排序方式（若无则进行个性化排序）
            0: 注册时间升序
            1: 注册时间降序
            2: 昵称升序
            3: 昵称降序
        :param name: 实验室名包含字段
        :param by_tag: 是否按标签检索

        :return:
            count: 实验室总数
            list: 实验室列表
                id: 实验室ID
                name: 实验室名
                icon_url: 头像
                owner_id: 创建者ID
                liker_count: 点赞数
                visitor_count: 最近7天访问数
                member_count: 实验室成员人数
                fields: 所属领域，格式：['field1', 'field2']
                tags: 标签，格式：['tag1', 'tag2', ...]
                time_created: 注册时间
        """
        i, j = offset, offset + limit
        if by_tag == 0:
            # 按实验室名称段检索
            labs = Lab.enabled.filter(name__icontains=name)
        else:
            # 按标签检索
            labs = Lab.enabled.filter(tags__name=name)
        c = labs.count()
        if order is not None:
            labs = labs.order_by(self.ORDERS[order])[i:j]
        else:
            # 将结果进行个性化排序
            lab_list = list()
            for t in labs:
                if fetch_user_by_token(request):
                    lab_list.append((t, calculate_ranking_score(request.user, t)))
                else:
                    lab_list.append((t, 0))
            lab_list = sorted(lab_list, key=lambda x: x[1], reverse=True)
            labs = (t[0] for t in lab_list[i:j])
        l = [{'id': t.id,
              'name': t.name,
              'icon_url': t.icon,
              'owner_id': t.owner.id,
              'liker_count': t.likers.count(),
              'visitor_count': t.visitors.count(),
              'member_count': t.members.count(),
              'fields': [t.field1, t.field2],
              'tags': [tag.name for tag in t.tags.all()],
              'time_created': t.time_created} for t in labs]
        return JsonResponse({'count': c, 'list': l, 'code': 0})
