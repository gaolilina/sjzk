#! /usr/bin/env python3
# -*- coding: utf-8 -*-
import datetime

from django import forms
from django.http import JsonResponse
from django.views.generic.base import View

from main.models import Competition, CompetitionStage
from util.decorator.param import validate_args


class SearchCompetition(View):
    ORDERS = ('time_created', '-time_created', 'name', '-name')

    @validate_args({
        'offset': forms.IntegerField(required=False, min_value=0),
        'limit': forms.IntegerField(required=False, min_value=0),
        'order': forms.IntegerField(required=False, min_value=0, max_value=3),
        'name': forms.CharField(max_length=20, required=False),
        'tag': forms.CharField(max_length=20, required=False),
        'history': forms.BooleanField(required=False),
        'province': forms.CharField(required=False, max_length=20),
        'field': forms.CharField(required=False, max_length=20),
    })
    def get(self, request, offset=0, limit=10, order=1, history=False, province=None, field=None, **kwargs):
        """
        搜索竞赛

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
            count: 竞赛总数
            list: 竞赛列表
                id: 竞赛ID
                name: 竞赛名
                liker_count: 点赞数
                time_started: 开始时间
                time_ended: 结束时间
                deadline: 截止时间
                team_participator_count: 已报名人数
                time_created: 创建时间
                status:
                province:
        """
        i, j, k = offset, offset + limit, self.ORDERS[order]
        condition = {}
        # 一般情况只显示未结束的活动
        if not history:
            condition['time_ended__gt'] = datetime.datetime.now()
            condition['status__lt'] = CompetitionStage.STAGE_END
        if province is not None:
            condition['province'] = province
        if field is not None:
            condition['field'] = field
        if 'name' in kwargs:
            condition['name__icontains'] = kwargs['name']
        if 'tag' in kwargs:
            condition['tags__icontains'] = kwargs['tag']
        qs = Competition.enabled.filter(**condition) if condition is not None else Competition.enabled.all()
        c = qs.count()
        l = [{'id': a.id,
              'name': a.name,
              'liker_count': a.likers.count(),
              'time_started': a.time_started,
              'time_ended': a.time_ended,
              'team_participator_count': a.team_participators.count(),
              'time_created': a.time_created,
              'status': a.status,
              'field': a.field,
              'province': a.province} for a in qs.order_by(k)[i:j]]
        return JsonResponse({'count': c, 'list': l})
