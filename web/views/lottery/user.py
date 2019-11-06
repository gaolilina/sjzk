#! /usr/bin/env python3
# -*- coding: utf-8 -*-
from django import forms

from modellib.models.lottery import Lottery, LotteryParticipant
from util.base.view import BaseView
from util.decorator.auth import client_auth
from util.decorator.param import validate_args, fetch_object


class LotteryJoinedUserList(BaseView):
    @client_auth
    @validate_args({
        'lottery_id': forms.IntegerField(),
    })
    @fetch_object(Lottery.objects, 'lottery')
    def get(self, request, lottery, **kwargs):
        qs = lottery.users.filter(is_victory=False)
        return self.success({
            'list': [{
                'name': u.user.name,
                'id': u.user.id,
                'icon': u.user.icon,
            } for u in qs]
        })


class MyVictoryList(BaseView):
    @client_auth
    @validate_args({
        'lottery': forms.IntegerField(required=False),
    })
    def get(self, request, lottery=None, **kwargs):
        qs = LotteryParticipant.objects.filter(user=request.user, is_victory=True)
        if lottery:
            qs = qs.filter(lottery=lottery)
        return self.success({
            'list': [{
                'id': v.id,
                'is_handled': v.is_handled,
                'lottery_name': v.lottery.name,
                'info': v.info,
            } for v in qs]
        })
