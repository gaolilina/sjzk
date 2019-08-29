#! /usr/bin/env python3
# -*- coding: utf-8 -*-
from django import forms
from django.http import JsonResponse
from django.views.generic import View

from main.models import User, Team
from main.models.need import TeamNeed
from main.utils import abort, get_score_stage
from main.utils.decorators import require_verification_token
from util.decorator.auth import app_auth
from util.decorator.param import validate_args, fetch_object


class Need(View):
    member_keys = ('id', 'title', 'description', 'number', 'age_min',
                   'age_max', 'gender', 'field', 'skill', 'degree', 'major',
                   'time_graduated', 'deadline', 'province', 'city', 'county')
    outsource_keys = ('id', 'title', 'description', 'number', 'age_min',
                      'age_max', 'gender', 'degree', 'field', 'skill', 'major',
                      'cost', 'cost_unit', 'time_started', 'time_ended',
                      'deadline', 'province', 'city', 'county')
    undertake_keys = ('id', 'title', 'description', 'field', 'skill', 'major',
                      'cost', 'cost_unit', 'time_started', 'time_ended',
                      'deadline', 'province', 'city', 'county')

    @fetch_object(TeamNeed.objects, 'need')
    @app_auth
    def get(self, request, need):
        """获取需求详情

        :return:
            if type==0(人员需求)：
                id: 需求id
                title: 需求标题
                description: 需求描述
                team_id: 团队ID
                team_name: 团队名称
                icon_url: 团队头像
                number: 所需人数
                age_min: 最小年龄
                age_max: 最大年龄
                gender: 性别要求
                field: 领域
                skill: 技能
                degree: 学历
                major: 专业
                province: 省
                city: 市
                county: 县\区
                members: 已加入成员
                time_graduated: 毕业时间
                deadline: 截止时间
            if type==1(外包需求):
                id: 需求id
                title: 需求标题
                description: 需求描述
                team_id: 团队ID
                team_name: 团队名称
                icon_url: 团队头像
                number: 所需人数
                age_min: 最小年龄
                age_max: 最大年龄
                gender: 性别要求
                field: 领域
                skill: 技能
                degree: 学历
                major: 专业
                cost: 费用
                province: 省
                city: 市
                county: 县\区
                cost_unit: 费用单位
                members: 已加入团队
                time_started: 任务开始时间
                time_ended: 任务结束时间
                deadline: 截止时间
            if type==2(承接需求):
                id: 需求id
                deadline: 截止时间
                title: 需求标题
                description: 需求描述
                team_id: 团队ID
                team_name: 团队名称
                icon_url: 团队头像
                field: 领域
                skill: 技能
                major: 专业
                cost: 费用
                province: 省
                city: 市
                county: 县\区
                cost_unit: 费用单位
                members: 已加入团队
                time_started: 任务开始时间
                time_ended: 任务结束时间
        """

        d = {'team_id': need.team.id, 'team_name': need.team.name}
        if need.type == 0:
            keys = self.member_keys
        elif need.type == 1:
            keys = self.outsource_keys
        elif need.type == 2:
            keys = self.undertake_keys
        else:
            abort(500)

        # noinspection PyUnboundLocalVariable
        for k in keys:
            d[k] = getattr(need, k)

        members = dict()
        if need.members:
            ids = need.members.split("|")
            for uid in ids:
                uid = int(uid)
                if need.type == 0:
                    members[uid] = User.enabled.get(id=uid).name
                else:
                    members[uid] = Team.enabled.get(id=uid).name
        d['members'] = members
        d['icon_url'] = need.team.icon
        return JsonResponse(d)

    @fetch_object(TeamNeed.objects, 'need')
    @require_verification_token
    def post(self, request, need):
        """将需求标记成已满足"""

        if request.user != need.team.owner:
            abort(403, '只有队长可以操作')
        need.status = 1
        need.save()
        request.user.score += get_score_stage(1)
        request.user.score_records.create(
            score=get_score_stage(1), type="能力",
            description="将团队需求标记为已满足")
        need.team.score += get_score_stage(1)
        need.team.score_records.create(
            score=get_score_stage(1), type="能力",
            description="将团队需求标记为已满足")
        request.user.save()
        need.team.save()
        abort(200)

    @fetch_object(TeamNeed, 'need')
    @require_verification_token
    def delete(self, request, need):
        """将需求标记成已删除"""

        if request.user != need.team.owner:
            abort(403, '只有队长可以操作')
        need.status = 2
        need.save()
        abort(200)


class NeedScreen(View):
    @validate_args({
        'offset': forms.IntegerField(required=False, min_value=0),
        'limit': forms.IntegerField(required=False, min_value=0),
        'status': forms.IntegerField(required=False, min_value=0, max_value=2),
        'type': forms.IntegerField(required=False, min_value=0, max_value=2),
        'name': forms.CharField(required=False, max_length=20),
        'province': forms.CharField(required=False, max_length=20),
        'city': forms.CharField(required=False, max_length=20),
        'county': forms.CharField(required=False, max_length=20),
        'number': forms.IntegerField(required=False, min_value=0),
        'degree': forms.CharField(required=False, max_length=20),
    })
    def get(self, request, type=None, status=None, offset=0, limit=10,
            **kwargs):
        """
        筛选发布中的需求列表

        :param offset: 起始量
        :param limit: 偏移量
        :param type: 需求的类型，默认为获取全部
        :param status: 需求状态，默认为获取全部
        :param kwargs:
                    name: 标题包含字段
                    province: 省
                    city: 市
                    county: 区\县
                    number: 需要人数
                    degree: 学历
        :return:
            count: 需求总数
            list: 需求列表
                need_id: 需求ID
                team_id: 团队ID
                team_name: 团队名称
                icon_url: 团队头像
                status: 需求状态
                type: 需求类别
                title: 需求标题
                number: 所需人数/团队人数
                degree: 需求学历
                members: 需求的加入者
                time_created: 发布时间
        """
        qs = TeamNeed.objects.all()
        if status is not None:
            # 按需求状态筛选
            qs = qs.filter(status=status)
        if type is not None:
            # 按需求类别筛选
            qs = qs.filter(type=type)
        name = kwargs.pop('name', '')
        if name:
            # 按标题检索
            qs = qs.filter(title__icontains=name)

        province = kwargs.pop('province', '')
        if province:
            # 按省会筛选
            qs = qs.filter(province=province)
        city = kwargs.pop('city', '')
        if city:
            # 按城市筛选
            qs = qs.filter(city=city)
        county = kwargs.pop('county', '')
        if county:
            # 按区/县筛选
            qs = qs.filter(county=county)
        number = kwargs.pop('number', '')
        if number:
            # 按需求所需最多人数筛选
            qs = qs.filter(number__lte=number)
        degree = kwargs.pop('degree', '')
        if degree:
            # 按学历筛选
            qs = qs.filter(degree=degree)

        c = qs.count()
        needs = qs[offset:offset + limit]
        l = list()
        for n in needs:
            need_dic = dict()
            members = dict()
            if n.members:
                ids = n.members.split("|")
                for id in ids:
                    id = int(id)
                    if n.type == 0:
                        members[id] = User.enabled.get(id=id).name
                    else:
                        members[id] = Team.enabled.get(id=id).name
            need_dic['id'] = n.id
            need_dic['team_id'] = n.team.id
            need_dic['team_name'] = n.team.name
            need_dic['number'] = n.number
            need_dic['icon_url'] = n.team.icon
            need_dic['status'] = n.status
            need_dic['type'] = n.type
            need_dic['title'] = n.title
            need_dic['degree'] = n.degree
            need_dic['members'] = members
            need_dic['time_created'] = n.time_created
            l.append(need_dic)
        return JsonResponse({'count': c, 'list': l})


