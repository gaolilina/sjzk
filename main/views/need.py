#! /usr/bin/env python3
# -*- coding: utf-8 -*-
from django import forms
from django.db import transaction
from django.http import JsonResponse
from django.views.generic import View

from main.models import User, Team
from main.models.need import TeamNeed
from main.utils import abort, get_score_stage, action
from main.utils.decorators import require_verification_token
from util.decorator.auth import app_auth
from main.utils.dfa import check_bad_words
from util.decorator.param import validate_args, fetch_object


class AllNeedList(View):
    # noinspection PyShadowingBuiltins
    @validate_args({
        'offset': forms.IntegerField(required=False, min_value=0),
        'limit': forms.IntegerField(required=False, min_value=0),
        'status': forms.IntegerField(required=False, min_value=0, max_value=2),
        'type': forms.IntegerField(required=False, min_value=0, max_value=2),
        'province': forms.CharField(required=False, max_length=100),
        'field': forms.CharField(required=False, max_length=100),
    })
    def get(self, request, type=None, status=None, province=None, field=None, offset=0, limit=10):
        """
        获取发布中的需求列表

        :param offset: 起始量
        :param limit: 偏移量
        :param type: 需求类型 - 0: member, 1: outsource, 2: undertake
        :param status: 需求状态 - 0: pending, 1: completed, 2: removed
        :return:
            count: 需求总数
            list: 需求列表
                need_id: 需求ID
                team_id: 团队ID
                team_name: 团队名称
                icon_url: 团队头像
                status: 需求状态
                title: 需求标题
                number: 所需人数/团队人数
                degree: 需求学历
                members: 需求的加入者
                time_created: 发布时间
        """
        qs = TeamNeed.objects
        if type is not None:
            qs = qs.filter(type=type)
        if status is not None:
            qs = qs.filter(status=status)
        else:
            qs = qs.filter(status=0)
        if province is not None:
            qs = qs.filter(province=province)
        if field is not None:
            qs = qs.filter(field=field)
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
            need_dic['title'] = n.title
            need_dic['degree'] = n.degree
            need_dic['members'] = members
            need_dic['time_created'] = n.time_created
            need_dic['field'] = n.field
            need_dic['province'] = n.province
            l.append(need_dic)
        return JsonResponse({'count': c, 'list': l})


class NeedList(View):
    # noinspection PyShadowingBuiltins
    @fetch_object(Team.enabled, 'team')
    @validate_args({
        'offset': forms.IntegerField(required=False, min_value=0),
        'limit': forms.IntegerField(required=False, min_value=0),
        'status': forms.IntegerField(required=False, min_value=0, max_value=2),
        'type': forms.IntegerField(required=False, min_value=0, max_value=2)
    })
    def get(self, request, team, type=None, status=None, offset=0, limit=10):
        """
        :param offset: 起始量
        :param limit: 偏移量
        :param type: 需求类型 - 0: member, 1: outsource, 2: undertake
        :param status: 需求状态 - 0: pending, 1: completed, 2: removed
        :return:
            count: 需求总数
            list: 需求列表
                id: 需求ID
                team_id: 团队ID
                team_name: 团队名称
                icon_url: 团队头像
                status: 需求状态
                title: 需求标题
                number: 所需人数/团队人数
                degree: 需求学历
                time_created: 发布时间
        """
        qs = team.needs
        if type is not None:
            qs = qs.filter(type=type)
        if status is not None:
            qs = qs.filter(status=status)
        else:
            qs = qs.filter(status=0)
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
            need_dic['icon_url'] = n.team.icon
            need_dic['status'] = n.status
            need_dic['title'] = n.title
            need_dic['members'] = members
            need_dic['degree'] = n.degree
            need_dic['number'] = n.number
            need_dic['time_created'] = n.time_created
            l.append(need_dic)
        return JsonResponse({'count': c, 'list': l})

    # noinspection PyShadowingBuiltins
    @fetch_object(Team.enabled, 'team')
    @require_verification_token
    def post(self, request, team, type):
        """发布需求

        人员需求：
            deadline: 截止时间
            description: 需求描述
            number: 所需人数
            age_min: 最小年龄
            age_max: 最大年龄
            gender: 性别要求
            field: 领域
            skill: 技能
            province: 省
            city: 市
            county: 县\区
            degree: 学历
            major: 专业
            time_graduated: 毕业时间
        外包需求：
            deadline: 截止时间
            description: 需求描述
            number: 所需人数
            age_min: 最小年龄
            age_max: 最大年龄
            gender: 性别要求
            field: 领域
            skill: 技能
            province: 省
            city: 市
            county: 县\区
            degree: 学历
            major: 专业
            cost: 费用
            cost_unit: 费用单位
            time_started: 外包任务开始时间
            time_ended: 外包任务结束时间
        承接需求：
            deadline: 截止时间
            description: 需求描述
            field: 领域
            skill: 技能
            major: 专业
            province: 省
            city: 市
            county: 县\区
            cost: 费用
            cost_unit: 费用单位
            time_started: 承接开始时间
            time_ended: 承接结束时间
        """
        if request.user != team.owner:
            abort(403, '只有队长可以操作')

        if type == 0:
            self.create_member_need(request, team)
        elif type == 1:
            self.create_outsource_need(request, team)
        elif type == 2:
            self.create_undertake_need(request, team)
        else:
            abort(500)

    @validate_args({
        'deadline': forms.DateField(),
        'title': forms.CharField(max_length=20),
        'description': forms.CharField(required=False, max_length=200),
        'number': forms.IntegerField(min_value=1),
        'gender': forms.IntegerField(required=False, min_value=0, max_value=2),
        'field': forms.CharField(required=False, max_length=20),
        'skill': forms.CharField(required=False, max_length=20),
        'degree': forms.CharField(required=False, max_length=20),
        'major': forms.CharField(required=False, max_length=20),
        'age_min': forms.IntegerField(
            required=False, min_value=0, max_value=99),
        'age_max': forms.IntegerField(
            required=False, min_value=1, max_value=100),
        'province': forms.CharField(required=False, max_length=20),
        'city': forms.CharField(required=False, max_length=20),
        'county': forms.CharField(required=False, max_length=20),
        'time_graduated': forms.DateField(required=False),
    })
    def create_member_need(self, request, team, **kwargs):
        if check_bad_words(kwargs["title"]) or check_bad_words(kwargs["description"]):
            abort(403, '含有非法词汇')

        team_needs = TeamNeed.objects.filter(team=team, type=0)
        if team_needs.count() == 0:
            team.score += get_score_stage(2)
            team.score_records.create(
                score=get_score_stage(2), type="初始数据",
                description="首次发布团队需求")
            team.save()

        n = team.needs.create(type=0)
        for k in kwargs:
            setattr(n, k, kwargs[k])
        n.save()
        # 发布动态
        action.send_member_need(team, n)
        # 增加积分
        request.user.score += get_score_stage(1)
        request.user.score_records.create(
            score=get_score_stage(1), type="能力",
            description="发布一个团队需求")
        team.score += get_score_stage(1)
        team.score_records.create(
            score=get_score_stage(1), type="活跃度",
            description="发布一个团队需求")
        request.user.save()
        team.save()
        abort(200)

    @validate_args({
        'deadline': forms.DateField(),
        'title': forms.CharField(max_length=20),
        'description': forms.CharField(required=False, max_length=200),
        'number': forms.IntegerField(min_value=1),
        'gender': forms.IntegerField(required=False, min_value=0, max_value=2),
        'field': forms.CharField(required=False, max_length=20),
        'skill': forms.CharField(required=False, max_length=20),
        'major': forms.CharField(required=False, max_length=20),
        'degree': forms.CharField(required=False, max_length=20),
        'age_min': forms.IntegerField(
            required=False, min_value=0, max_value=99),
        'age_max': forms.IntegerField(
            required=False, min_value=1, max_value=100),
        'cost': forms.IntegerField(required=False),
        'cost_unit': forms.CharField(required=False, max_length=1),
        'province': forms.CharField(required=False, max_length=20),
        'city': forms.CharField(required=False, max_length=20),
        'county': forms.CharField(required=False, max_length=20),
        'time_started': forms.DateField(),
        'time_ended': forms.DateField(),
    })
    def create_outsource_need(self, request, team, **kwargs):
        if check_bad_words(kwargs["title"]) or check_bad_words(kwargs["description"]):
            abort(403, '含有非法词汇')

        team_needs = TeamNeed.objects.filter(team=team, type=1)
        if team_needs.count() == 0:
            team.score += get_score_stage(2)
            team.score_records.create(
                score=get_score_stage(2), type="初始数据",
                description="首次发布团队需求")
            team.save()

        n = team.needs.create(type=1)
        for k in kwargs:
            setattr(n, k, kwargs[k])
        n.save()
        # 发布动态
        action.send_member_need(team, n)
        # 增加积分
        request.user.score += get_score_stage(1)
        request.user.score_records.create(
            score=get_score_stage(1), type="能力",
            description="发布一个团队需求")
        team.score += get_score_stage(1)
        team.score_records.create(
            score=get_score_stage(1), type="活跃度",
            description="发布一个团队需求")
        request.user.save()
        team.save()
        abort(200)

    @validate_args({
        'deadline': forms.DateField(),
        'title': forms.CharField(max_length=20),
        'description': forms.CharField(required=False, max_length=200),
        'field': forms.CharField(required=False, max_length=20),
        'skill': forms.CharField(required=False, max_length=20),
        'province': forms.CharField(required=False, max_length=20),
        'city': forms.CharField(required=False, max_length=20),
        'county': forms.CharField(required=False, max_length=20),
        'major': forms.CharField(required=False, max_length=20),
        'cost': forms.IntegerField(required=False),
        'cost_unit': forms.CharField(required=False, max_length=1),
        'time_started': forms.DateField(),
        'time_ended': forms.DateField(),
    })
    def create_undertake_need(self, request, team, **kwargs):
        if check_bad_words(kwargs["title"]) or check_bad_words(kwargs["description"]):
            abort(403, '含有非法词汇')

        team_needs = TeamNeed.objects.filter(team=team, type=2)
        if team_needs.count() == 0:
            team.score += get_score_stage(2)
            team.score_records.create(
                score=get_score_stage(2), type="初始数据",
                description="首次发布团队需求")
            team.save()

        n = team.needs.create(type=2)
        for k in kwargs:
            setattr(n, k, kwargs[k])
        n.save()
        # 发布动态
        action.send_member_need(team, n)
        # 增加积分
        request.user.score += get_score_stage(1)
        request.user.score_records.create(
            score=get_score_stage(1), type="能力",
            description="发布一个团队需求")
        team.score += get_score_stage(1)
        team.score_records.create(
            score=get_score_stage(1), type="活跃度",
            description="发布一个团队需求")
        request.user.save()
        team.save()
        abort(200)


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


class NeedSearch(View):
    @validate_args({
        'offset': forms.IntegerField(required=False, min_value=0),
        'limit': forms.IntegerField(required=False, min_value=0),
        'status': forms.IntegerField(required=False, min_value=0, max_value=2),
        'type': forms.IntegerField(required=False, min_value=0, max_value=2),
        'name': forms.CharField(max_length=20),
    })
    def get(self, request, name, type=None, status=None, offset=0, limit=10):
        """
        搜索发布中的需求列表

        :param offset: 偏移量
        :param name: 标题包含字段
        :param type: 需求的类型，默认为获取全部
        :param status: 需求状态，默认为获取全部
        :return:
            count: 需求总数
            list: 需求列表
                need_id: 需求ID
                team_id: 团队ID
                team_name: 团队名称
                icon_url: 团队头像
                status: 需求状态
                type: 需求类型
                title: 需求标题
                number: 所需人数/团队人数
                degree: 需求学历
                members: 需求的加入者
                time_created: 发布时间
        """
        qs = TeamNeed.objects.filter(title__icontains=name)
        if status is not None:
            # 按需求状态搜索
            qs = qs.filter(status=status)
        if type is not None:
            # 按需求类别搜索
            qs = qs.filter(type=type)
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


class NeedUserList(View):
    ORDERS = (
        'time_created',
        '-time_created',
        'name',
        '-name',
    )

    @fetch_object(TeamNeed.objects, 'need')
    @app_auth
    @validate_args({
        'offset': forms.IntegerField(required=False, min_value=0),
        'limit': forms.IntegerField(required=False, min_value=0),
        'order': forms.IntegerField(required=False, min_value=0, max_value=3),
    })
    def get(self, request, need, offset=0, limit=10, order=1):
        """获取需求的成员列表

        :param offset: 偏移量
        :param order: 排序方式
            0: 成为成员时间升序
            1: 成为成员时间降序（默认值）
            2: 昵称升序
            3: 昵称降序
        :return:
            count: 成员总数
            list: 成员列表
                id: 用户ID
                username:用户名
                name: 用户昵称
                icon_url: 用户头像
                tags: 标签
                gender: 性别
                liker_count: 点赞数
                follower_count: 粉丝数
                visitor_count: 访问数
                time_created: 注册时间
        """
        i, j, k = offset, offset + limit, self.ORDERS[order]
        uids = []
        if need.members:
            ids = need.members.split("|")
            for uid in ids:
                uids.append(int(uid))
            members = User.enabled.filter(id__in=uids)
            c = members.count()
            rs = members.order_by(k)[i:j]
            l = [{'id': r.id,
                  'username': r.username,
                  'name': r.name,
                  'icon_url': r.icon,
                  'tags': [tag.name for tag in r.tags.all()],
                  'gender': r.gender,
                  'liker_count': r.likers.count(),
                  'follower_count': r.followers.count(),
                  'visitor_count': r.visitors.count(),
                  'time_created': r.time_created} for r in rs]
        else:
            c = 0
            l = []
        return JsonResponse({'count': c, 'list': l})


class NeedTeamList(View):
    ORDERS = (
        'time_created',
        '-time_created',
        'name',
        '-name',
    )

    @fetch_object(TeamNeed.objects, 'need')
    @app_auth
    @validate_args({
        'offset': forms.IntegerField(required=False, min_value=0),
        'limit': forms.IntegerField(required=False, min_value=0),
        'order': forms.IntegerField(required=False, min_value=0, max_value=3),
    })
    def get(self, request, need, offset=0, limit=10, order=1):
        """获取需求的成员列表

        :param offset: 偏移量
        :param order: 排序方式
            0: 成为成员时间升序
            1: 成为成员时间降序（默认值）
            2: 昵称升序
            3: 昵称降序
        :return:
            count: 成员总数
            list: 成员列表
                id: 团队ID
                name: 团队昵称
                icon_url: 团队头像
                owner_id: 创建者ID
                liker_count: 点赞数
                visitor_count: 最近7天访问数
                member_count: 团队成员人数
                fields: 所属领域，格式：['field1', 'field2']
                tags: 标签，格式：['tag1', 'tag2', ...]
                time_created: 注册时间
        """
        i, j, k = offset, offset + limit, self.ORDERS[order]
        tids = []
        if need.members:
            ids = need.members.split("|")
            for tid in ids:
                tids.append(int(tid))
            members = Team.enabled.filter(id__in=tids)
            c = members.count()
            rs = members.order_by(k)[i:j]
            l = [{'id': r.id,
                  'name': r.name,
                  'icon_url': r.icon,
                  'owner_id': r.owner.id,
                  'liker_count': r.likers.count(),
                  'visitor_count': r.visitors.count(),
                  'member_count': r.members.count(),
                  'fields': [r.field1, r.field2],
                  'tags': [tag.name for tag in r.tags.all()],
                  'time_created': r.time_created} for r in rs]
        else:
            c = 0
            l = []
        return JsonResponse({'count': c, 'list': l})


class MemberNeedRequestList(View):
    @fetch_object(TeamNeed.objects, 'need')
    @app_auth
    @validate_args({
        'offset': forms.IntegerField(required=False, min_value=0),
        'limit': forms.IntegerField(required=False, min_value=0),
    })
    def get(self, request, need, offset=0, limit=10):
        """获取人员需求的加入申请列表

        :param offset: 偏移量
        :return: request.user 不为团队创始人时，404
        :return: request.user 为团队创始人时
            count: 申请总数
            list: 申请列表
                id: 申请者ID
                username: 申请者用户名
                name: 申请者昵称
                icon_url: 申请者头像
                description: 备注
                time_created: 申请时间
        """
        if request.user == need.team.owner:
            # 拉取人员需求下团队的加入申请信息
            c = need.member_requests.count()
            qs = need.member_requests.all()[offset:offset + limit]

            l = [{'id': r.sender.id,
                  'username': r.sender.username,
                  'name': r.sender.name,
                  'icon_url': r.sender.icon,
                  'description': r.description,
                  'time_created': r.time_created} for r in qs]
            return JsonResponse({'count': c, 'list': l})
        abort(404, '只有队长可以操作')

    @fetch_object(TeamNeed.objects, 'need')
    @require_verification_token
    @validate_args({
        'description': forms.CharField(required=False, max_length=100),
    })
    def post(self, request, need, description=''):
        """向人员需求发出加入申请

        :param description: 附带消息
        """
        if request.user == need.team.owner:
            abort(403, '队长不能操作')

        if need.team.members.filter(user=request.user).exists():
            abort(403, '已经是对方团队成员')

        if need.team.member_requests.filter(user=request.user).exists():
            abort(200)

        if need.team.invitations.filter(user=request.user).exists():
            abort(403, '对方团队已经发送邀请')

        need.member_requests.create(sender=request.user,
                                    description=description)
        abort(200)


class MemberNeedRequest(View):
    @fetch_object(TeamNeed.objects, 'need')
    @fetch_object(User.enabled, 'user')
    @require_verification_token
    def post(self, request, need, user):
        """将目标用户添加为自己的团队成员（对方需发送过人员需求下的加入团队申请）"""

        if request.user != need.team.owner:
            abort(403, '只有队长可以操作')

        if not need.member_requests.filter(sender=user):
            abort(403, '对方未发送申请')

        # 若对方已是团队成员则不做处理
        if need.team.members.filter(user=user).exists():
            abort(200)

        # 在事务中建立关系，并删除对应的加团队申请
        with transaction.atomic():
            need.member_requests.filter(sender=user).delete()
            # 保存需求的加入成员Id
            if len(need.members) > 0:
                need.members = need.members + "|" + str(user.id)
            else:
                need.members = str(user.id)
            need.save()
            need.team.members.create(user=user)
            action.join_team(user, need.team)
            # 积分
            request.user.score += get_score_stage(1)
            request.user.score_records.create(
                score=get_score_stage(1), type="能力", description="加入团队成功")
            need.team.score += get_score_stage(1)
            need.team.score_records.create(
                score=get_score_stage(1), type="能力",
                description="成功招募一个成员")
            request.user.save()
            need.team.save()
        abort(200)

    @fetch_object(TeamNeed.objects, 'need')
    @fetch_object(User.enabled, 'user')
    @require_verification_token
    def delete(self, request, need, user):
        """忽略某用户人员需求下的加团队请求"""

        if request.user != need.team.owner:
            abort(403, '只有队长可以操作')

        qs = need.member_requests.filter(sender=user)
        if not qs.exists():
            abort(404, '申请不存在')
        qs.delete()
        abort(200)


class NeedRequestList(View):
    @fetch_object(TeamNeed.objects, 'need')
    @fetch_object(Team.enabled, 'team')
    @app_auth
    @validate_args({
        'offset': forms.IntegerField(required=False, min_value=0),
        'limit': forms.IntegerField(required=False, min_value=0),
    })
    def get(self, request, need, team, offset=0, limit=10):
        """获取需求的合作申请列表

        :param offset: 偏移量
        :return: request.user 不为团队创始人时，404
        :return: request.user 为团队创始人时
            count: 申请总数
            list: 申请列表
                id: 申请者ID
                team_id: 申请团队ID
                name: 申请团队名称
                icon_url: 申请团队头像
                time_created: 申请时间
        """
        if request.user == need.team.owner and need.team == team:
            # 拉取需求的申请合作信息
            c = need.cooperation_requests.count()
            qs = need.cooperation_requests.all()[offset:offset + limit]

            l = [{'id': r.sender.owner.id,
                  'team_id': r.sender.id,
                  'name': r.sender.name,
                  'icon_url': r.sender.icon,
                  'time_created': r.time_created} for r in qs]
            return JsonResponse({'count': c, 'list': l})
        abort(404, '只有队长可以操作')

    @fetch_object(TeamNeed.objects, 'need')
    @fetch_object(Team.enabled, 'team')
    @require_verification_token
    def post(self, request, need, team):
        """向需求发出合作申请

        """
        if need.cooperation_requests.filter(sender=team).exists():
            abort(404, '合作申请已经发送过')
        if need.cooperation_invitations.filter(invitee=team).exists():
            abort(404, '合作申请已经发送过')
        if request.user == team.owner:
            need.cooperation_requests.create(sender=team)
            abort(200)
        abort(404, '只有队长能操作')


class NeedRequest(View):
    @fetch_object(Team.enabled, 'team')
    @app_auth
    @validate_args({
        'offset': forms.IntegerField(required=False, min_value=0),
        'limit': forms.IntegerField(required=False, min_value=0),
    })
    def get(self, request, team, offset=0, limit=10):
        """获取团队发出的的合作申请列表

        :param offset: 偏移量
        :return: request.user 不为团队创始人时，404
        :return: request.user 为团队创始人时
            count: 申请总数
            list: 申请列表
                team_id: 申请的团队ID
                need_id: 申请的需求ID
                title: 申请的需求标题
                name: 申请团队名称
                icon_url: 申请团队头像
                time_created: 申请时间
        """
        if request.user == team.owner:
            # 拉取申请合作信息
            c = team.cooperation_requests.count()
            qs = team.cooperation_requests.all()[offset:offset + limit]

            l = [{'team_id': r.need.team.id,
                  'id': r.need.id,
                  'name': r.need.team.name,
                  'title': r.need.title,
                  'icon_url': r.need.team.icon,
                  'time_created': r.time_created} for r in qs]
            return JsonResponse({'count': c, 'list': l})
        abort(404, '只有队长能操作')

    @fetch_object(TeamNeed.objects, 'need')
    @fetch_object(Team.enabled, 'team')
    @require_verification_token
    def post(self, request, need, team):
        """同意加入申请并将创始人加入自己团队（对方需发送过合作申请）"""

        if request.user != need.team.owner:
            abort(404, '只有队长能操作')

        if need.cooperation_requests.filter(sender=team).exists():
            # 在事务中建立关系，并删除对应的申请合作
            with transaction.atomic():
                need.cooperation_requests.filter(sender=team).delete()
                if need.team.members.filter(user=team.owner).exists():
                    abort(200)
                # 保存需求的加入团队Id
                if len(need.members) > 0:
                    need.members = need.members + "|" + str(team.id)
                else:
                    need.members = str(team.id)
                need.save()

                need.team.members.create(user=team.owner)
                action.join_team(team.owner, need.team)
                request.user.score += get_score_stage(1)
                request.user.score_records.create(
                    score=get_score_stage(1), type="能力",
                    description="与其他团队合作")
                team.score += get_score_stage(1)
                team.score_records.create(
                    score=get_score_stage(1), type="能力",
                    description="与其他团队合作")
                request.user.save()
                team.save()
            abort(200)
        abort(404, '对方未发送过申请合作')

    @fetch_object(TeamNeed.objects, 'need')
    @fetch_object(Team.enabled, 'team')
    @require_verification_token
    def delete(self, request, need, team):
        """忽略某团队的合作申请"""

        if request.user != need.team.owner:
            abort(403, '只有队长可以操作')

        qs = need.cooperation_requests.filter(sender=team)
        if not qs.exists():
            abort(404, '合作申请不存在')
        qs.delete()
        abort(200)


class NeedInvitationList(View):
    @fetch_object(TeamNeed.objects, 'need')
    @fetch_object(Team.enabled, 'team')
    @app_auth
    @validate_args({
        'offset': forms.IntegerField(required=False, min_value=0),
        'limit': forms.IntegerField(required=False, min_value=0),
    })
    def get(self, request, need, team, offset=0, limit=10):
        """获取需求的合作邀请列表

        :param offset: 偏移量
        :return: request.user 不为团队创始人时，404
        :return: request.user 为团队创始人时
            count: 邀请总数
            list: 邀请列表
                team_id: 被邀请团队ID
                name: 被邀请团队名称
                icon_url: 被邀请团队头像
                time_created: 邀请时间
        """
        if request.user == need.team.owner and need.team == team:
            # 拉取邀请合作信息
            c = need.cooperation_invitations.count()
            qs = need.cooperation_invitations.all()[offset:offset + limit]

            l = [{'team_id': r.invitee.id,
                  'name': r.invitee.name,
                  'icon_url': r.invitee.icon,
                  'time_created': r.time_created} for r in qs]
            return JsonResponse({'count': c, 'list': l})
        abort(404, '只有队长可以操作')

    @fetch_object(TeamNeed.objects, 'need')
    @fetch_object(Team.enabled, 'team')
    @require_verification_token
    def post(self, request, need, team):
        """向团队发出合作邀请

        """
        if need.cooperation_invitations.filter(invitee=team).exists():
            abort(404, '已经发送过合作申请')
        if need.cooperation_requests.filter(sender=team).exists():
            abort(404, '对方已经发送过合作申请')
        if request.user == team.owner:
            need.cooperation_invitations.create(invitee=team)
            abort(200)
        abort(404, '只有队长可以操作')


class NeedInvitation(View):
    @fetch_object(Team.enabled, 'team')
    @app_auth
    @validate_args({
        'offset': forms.IntegerField(required=False, min_value=0),
        'limit': forms.IntegerField(required=False, min_value=0),
    })
    def get(self, request, team, offset=0, limit=10):
        """获取当前团队的需求合作邀请列表

        :param offset: 偏移量
        :return: request.user 不为团队创始人时，404
        :return: request.user 为团队创始人时
            count: 邀请总数
            list: 邀请列表
                team_id: 邀请方团队ID
                need_id: 邀请方需求ID
                title: 邀请方需求标题
                name: 邀请方团队名称
                icon_url: 邀请方团队头像
                time_created: 邀请时间
        """
        if request.user == team.owner:
            # 拉取邀请合作信息
            c = team.cooperation_invitations.count()
            qs = team.cooperation_invitations.all()[offset:offset + limit]

            l = [{'team_id': r.inviter.id,
                  'need_id': r.need.id,
                  'title': r.need.title,
                  'name': r.inviter.name,
                  'icon_url': r.invitee.icon,
                  'time_created': r.time_created} for r in qs]
            return JsonResponse({'count': c, 'list': l})
        abort(404, '只有队长可以操作')

    @fetch_object(TeamNeed.objects, 'need')
    @fetch_object(Team.enabled, 'team')
    @require_verification_token
    def post(self, request, need, team):
        """同意邀请并将加入他人的团队（对方需发送过合作邀请）"""

        if request.user != need.team.owner:
            abort(404, '只有队长可以操作')

        if need.cooperation_invitations.filter(invitee=team).exists():
            # 在事务中建立关系，并删除对应的邀请合作
            with transaction.atomic():
                need.cooperation_invitations.filter(invitee=team).delete()
                if need.team.members.filter(user=team.owner).exists():
                    abort(200)
                # 保存需求的加入团队Id
                if len(need.members) > 0:
                    need.members = need.members + "|" + str(team.id)
                else:
                    need.members = str(team.id)
                need.save()
                need.team.members.create(user=team.owner)
                action.join_team(team.owner, need.team)
                request.user.score += get_score_stage(1)
                request.user.score_records.create(
                    score=get_score_stage(1), type="能力",
                    description="与其他团队合作")
                team.score += get_score_stage(1)
                team.score_records.create(
                    score=get_score_stage(1), type="能力",
                    description="与其他团队合作")
                request.user.save()
                team.save()
            abort(200)
        abort(404, '邀请合作不存在')

    @fetch_object(TeamNeed.objects, 'need')
    @fetch_object(Team.enabled, 'team')
    @require_verification_token
    def delete(self, request, need, team):
        """忽略某来自需求的合作邀请"""

        if request.user != team.owner:
            abort(403, '只有队长可以操作')

        qs = need.cooperation_invitations.filter(invitee=team)
        if not qs.exists():
            abort(404, '合作邀请不存在')
        qs.delete()
        abort(200)