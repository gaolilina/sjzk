#! /usr/bin/env python3
# -*- coding: utf-8 -*-
import random

from django import forms

from modellib.models.lottery import Lottery, LotteryParticipant
from util.base.view import BaseView
from util.decorator.auth import client_auth
from util.decorator.param import validate_args, fetch_object


class JoinLottery(BaseView):
    @client_auth
    @validate_args({
        'lottery_id': forms.IntegerField(),
    })
    @fetch_object(Lottery.objects, 'lottery')
    def post(self, request, lottery, **kwargs):
        if lottery.finished:
            return self.fail(1, '已结束')
        # 已签到，无需再次签到
        user = request.user
        if not Lottery.objects.filter(user=user, lottery=lottery).exists():
            Lottery.objects.create(user=user, lottery=lottery)
        return self.success({
            'name': user.name,
            'id': user.id,
            'icon': user.icon,
        })


class LotteryAction(BaseView):

    @client_auth
    @validate_args({
        'lottery_id': forms.IntegerField(),
    })
    @fetch_object(Lottery.objects, 'lottery')
    def get(self, request, lottery, **kwargs):
        if lottery.user != request.user:
            return self.fail(1, '无权查看')
        victories = lottery.users.filter(is_victor=True)
        return self.success({
            'list': [{
                'is_handled': v.is_handled,
                'user': v.user.name,
                'id': v.id,
                'info': v.info,
            } for v in victories]
        })

    @client_auth
    @validate_args({
        'lottery_id': forms.IntegerField(),
        'count': forms.IntegerField(max_value=100),
        'info': forms.CharField(max_length=100),
    })
    @fetch_object(Lottery.objects, 'lottery')
    def post(self, request, lottery, count, info, **kwargs):
        if lottery.finished:
            return self.fail(2, '抽奖已结束')
        if lottery.user != request.user:
            return self.fail(3, '无权操作')
        qs = lottery.users.filter(is_victor=False)
        all_count = qs.count()
        if count > all_count:
            return self.fail(1, '中奖数量大于参与人数')
        victories = self.__generate_lottery(qs, count)
        for v in victories:
            LotteryParticipant.objects.filter(id=v.id).update(is_victory=True, info=info)
        # 返回中奖的用户列表
        return self.success({
            'list': [{
                'name': u.user.name,
                'id': u.user.id,
                'icon': u.user.icon,
            } for u in victories]
        })
        pass

    def __generate_lottery(self, users, count):
        """
        抽奖
        :param users:
        :param count:
        :return:
        """
        indexs = random.sample(range(0, len(users)), count)
        result = []
        index = 0
        for u in users:
            if index in indexs:
                result.append(u)
            index += 1
        return result
