#! /usr/bin/env python3
# -*- coding: utf-8 -*-
import os
from django import forms

from modellib.models.lottery import Lottery
from util.base.view import BaseView
from util.decorator.auth import client_auth
from util.decorator.param import validate_args, fetch_object


class LotteryListAndCreate(BaseView):

    @client_auth
    @validate_args({
        'finished': forms.BooleanField(required=False),
    })
    def get(self, request, finished=None, **kwargs):
        filter_param = {
            'user': request.user
        }
        if finished:
            filter_param['finished'] = finished
        qs = Lottery.objects.filter(**filter_param)
        return self.success({
            'list': [lottery_to_json(l) for l in qs],
            'count': qs.count(),
        })

    @client_auth
    @validate_args({
        'name': forms.CharField(max_length=100),
    })
    def post(self, request, name, **kwargs):
        Lottery.objects.create(name=name, user=request.user)
        return self.success()


class LotteryInfo(BaseView):
    @client_auth
    @validate_args({
        'lottery_id': forms.IntegerField(),
    })
    @fetch_object(Lottery.objects, 'lottery')
    def get(self, request, lottery, **kwargs):
        return self.success(lottery_to_json(lottery))

    @client_auth
    @validate_args({
        'lottery_id': forms.IntegerField(),
        'name': forms.CharField(max_length=100, required=False),
        'finished': forms.BooleanField(required=False),
    })
    @fetch_object(Lottery.objects, 'lottery')
    def post(self, request, lottery, **kwargs):
        # 可以修改的字段
        params_list = ('name', 'finished')
        # 构造更新参数
        update_param = {}
        for k in params_list:
            if k in kwargs:
                update_param[k] = kwargs[k]
        # 如果有要更新的字段，则更新
        if len(update_param) > 0:
            Lottery.objects.filter(id=lottery.id).update(**update_param)
        return self.success()


class LotteryMusicList(BaseView):
    @client_auth
    def get(self, request):
        prefix = "http://pre.web.chuangyh.com/lottery_music/"
        path = "/srv/SJZK_Web_Frontend/lottery_music"
        files = []
        for filename in os.listdir(path):
            files.append(prefix + str(filename))

        return self.success({
            'list': files,
            'count': len(files),
        })

class LotteryDetailInfo(BaseView):
    @client_auth
    @validate_args({
        'lottery_id': forms.IntegerField(),
    })
    @fetch_object(Lottery.objects, 'lottery')
    def get(self, request, lottery, **kwargs):
        res = {
            'id': lottery.id,
            'name': lottery.name,
            'finished': lottery.finished,
            'count_participant': lottery.users.all().count(),
        }
        infos = {}
        items = lottery.users.all()
        print(items.count())
        for item in items:
            round = item.lottery_round
            if infos.get(str(round), '') == '':
                infos[str(round)] = [{'name': item.info, 'count':1}]
            else:
                info = infos.get(str(round), '')
                flag = False
                for list in info:
                    if list.get('name', '') == item.info:
                        list['count'] = list.get('count', 1) + 1
                        flag = True
                        break
                if flag == False:
                    info.append({'name': item.info, 'count':1})

        res["infos"] = infos
        return self.success(res)


def lottery_to_json(lottery):
    return {
        'id': lottery.id,
        'name': lottery.name,
        'finished': lottery.finished,
        'count_participant': lottery.users.all().count(),
    }