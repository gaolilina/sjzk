#! /usr/bin/env python3
# -*- coding: utf-8 -*-
from django import forms
from django.http import JsonResponse
from django.views import View

from main.models import Activity
from main.utils.decorators import validate_args


class SearchActivity(View):
    ORDERS = ('time_created', '-time_created', 'name', '-name')

    @validate_args({
        'offset': forms.IntegerField(required=False, min_value=0),
        'limit': forms.IntegerField(required=False, min_value=0),
        'order': forms.IntegerField(required=False, min_value=0, max_value=3),
        'name': forms.CharField(max_length=20, required=False),
        'tag': forms.CharField(max_length=20, required=False),
    })
    def get(self, request, offset=0, limit=10, order=1, **kwargs):
        """
        搜索活动

        :param offset: 偏移量
        :param limit: 数量上限
        :param order: 排序方式
            0: 注册时间升序
            1: 注册时间降序（默认值）
            2: 昵称升序
            3: 昵称降序
        :param kwargs: 搜索条件
            name: 活动名包含字段

        :return:
            count: 活动总数
            list: 活动列表
                id: 活动ID
                name: 活动名
                liker_count: 点赞数
                time_started: 开始时间
                time_ended: 结束时间
                deadline: 截止时间
                user_participator_count: 已报名人数
                time_created: 创建时间
                status:
                province:
        """
        i, j, k = offset, offset + limit, self.ORDERS[order]
        condition = None
        if 'name' in kwargs:
            condition['name__icontains'] = kwargs['name']
        if 'tag' in kwargs:
            condition['tags__icontains'] = kwargs['tag']
        qs = Activity.enabled.filter(**condition) if condition is not None else Activity.enabled.all()
        c = qs.count()
        l = [{'id': a.id,
              'name': a.name,
              'liker_count': a.likers.count(),
              'time_started': a.time_started,
              'time_ended': a.time_ended,
              'deadline': a.deadline,
              'user_participator_count': a.user_participators.count(),
              'time_created': a.time_created,
              'status': a.status,
              'province': a.province} for a in qs.order_by(k)[i:j]]
        return JsonResponse({'count': c, 'list': l})
