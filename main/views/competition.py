from django import forms
from django.http import JsonResponse
from django.views.generic import View

from ..models import Competition, Team
from ..utils import abort
from ..utils.decorators import *


__all__ = ['List', 'Detail', 'CompetitionStage', 'TeamParticipatorList',
           'Search']


class List(View):
    ORDERS = ('time_created', '-time_created', 'name', '-name')

    @require_token
    @validate_args({
        'offset': forms.IntegerField(required=False, min_value=0),
        'limit': forms.IntegerField(required=False, min_value=0),
        'order': forms.IntegerField(required=False, min_value=0, max_value=3),
    })
    def get(self, request, offset=0, limit=10, order=1):
        """获取竞赛列表

        :param offset: 偏移量
        :param limit: 数量上限
        :param order: 排序方式
            0: 注册时间升序
            1: 注册时间降序（默认值）
            2: 昵称升序
            3: 昵称降序

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
        """

        k = self.ORDERS[order]
        c = Competition.enabled.count()
        qs = Competition.enabled.all().order_by(k)[offset: offset + limit]
        l = [{'id': a.id,
              'name': a.name,
              'liker_count': a.likers.count(),
              'time_started': a.time_started,
              'time_ended': a.time_ended,
              'deadline': a.deadline,
              'team_participator_count': a.team_participators.count(),
              'time_created': a.time_created} for a in qs]
        return JsonResponse({'count': c, 'list': l})


class Detail(View):
    @fetch_object(Competition.enabled, 'competition')
    @require_token
    def get(self, request, competition):
        """获取竞赛详情
        :return:
            id: 竞赛ID
            name: 竞赛名
            liker_count: 点赞数
            time_started: 开始时间
            time_ended: 结束时间
            deadline: 截止时间
            allow_team: 允许报名团队数
            team_participator_count: 已报名数
            status: 竞赛当前阶段
            province: 省
            city: 城市
            unit: 机构
            user_type: 参与人员身份
            time_created: 创建时间
        """

        return JsonResponse({
            'id': competition.id,
            'name': competition.name,
            'content': competition.content,
            'liker_count': competition.likers.count(),
            'time_started': competition.time_started,
            'time_ended': competition.time_ended,
            'deadline': competition.deadline,
            'allow_team': competition.allow_team,
            'team_participator_count': competition.team_participators.count(),
            'status': competition.status,
            'province': competition.province,
            'city': competition.city,
            'unit': competition.unit,
            'user_type': competition.user_type,
            'time_created': competition.time_created,
        })


class CompetitionStage(View):
    @fetch_object(Competition.enabled, 'competition')
    @require_token
    @validate_args({
        'offset': forms.IntegerField(required=False, min_value=0),
        'limit': forms.IntegerField(required=False, min_value=0),
    })
    def get(self, request, competition, offset=0, limit=10):
        """获取竞赛的阶段列表
        :param offset: 偏移量
        :param limit: 数量上限
        :param order: 排序方式
            0: 注册时间升序
            1: 注册时间降序（默认值）
            2: 昵称升序
            3: 昵称降序

        :return:
            count: 阶段总数
            list: 阶段列表
                id: 阶段ID
                stage: 阶段名称:0:前期宣传, 1:报名, 2:结束
                time_started: 开始时间
                time_ended: 结束时间
                time_created: 创建时间
        """

        c = competition.stages.count()
        qs = competition.stages.all().order_by("status")[offset: offset + limit]
        l = [{'id': p.id,
              'status': p.status,
              'time_started': p.time_started,
              'time_ended': p.time_ended,
              'time_created': p.time_created} for p in qs]
        return JsonResponse({'count': c, 'list': l})


class TeamParticipatorList(View):
    ORDERS = ('time_created', '-time_created', 'name', '-name')

    @fetch_object(Competition.enabled, 'competition')
    @require_token
    @validate_args({
        'offset': forms.IntegerField(required=False, min_value=0),
        'limit': forms.IntegerField(required=False, min_value=0),
        'order': forms.IntegerField(required=False, min_value=0, max_value=3),
    })
    def get(self, request, competition, offset=0, limit=10, order=1):
        """获取报名团队列表"""

        k = self.ORDERS[order]
        c = competition.team_participators.count()
        qs = competition.team_participators.all().order_by(
            k)[offset: offset + limit]
        l = [{'id': p.team.id,
              'name': p.team.name,
              'icon_url': p.team.icon} for p in qs]
        return JsonResponse({'count': c, 'list': l})

    @fetch_object(Competition.enabled, 'competition')
    @validate_args({'team_id': forms.IntegerField()})
    @require_token
    def post(self, request, competition, team_id):
        """报名"""

        if competition.status != 1:
            abort(403, 'not on the stage of signing up')
        c = competition.team_participators.count()
        if competition.allow_team != 0 and c >= competition.allow_team:
            abort(403, 'participators are enough')

        try:
            team = Team.enabled.get(id=team_id)
        except Team.DoesNotExist:
            abort(400)
        else:
            if not competition.team_participators.filter(team=team).exists():
                competition.team_participators.create(team=team)
            if competition.province and competition.province != team.province:
                abort(403, 'location limited')
            if competition.province and competition.city != team.city:
                abort(403, 'location limited')
            for m in team.member:
                if m.user.is_verified != 2:
                    abort(403, 'team member must verified')
            abort(200)


class Search(View):
    ORDERS = ('time_created', '-time_created', 'name', '-name')

    @require_token
    @validate_args({
        'offset': forms.IntegerField(required=False, min_value=0),
        'limit': forms.IntegerField(required=False, min_value=0),
        'order': forms.IntegerField(required=False, min_value=0, max_value=3),
        'name': forms.CharField(max_length=20),
    })
    def get(self, request, offset=0, limit=10, order=1, **kwargs):
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
        """
        i, j, k = offset, offset + limit, self.ORDERS[order]
        qs = Competition.enabled.filter(name__contains=kwargs['name'])
        c = qs.count()
        l = [{'id': a.id,
              'name': a.name,
              'liker_count': a.likers.count(),
              'time_started': a.time_started,
              'time_ended': a.time_ended,
              'deadline': a.deadline,
              'team_participator_count': a.team_participators.count(),
              'time_created': a.time_created} for a in qs.order_by(k)[i:j]]
        return JsonResponse({'count': c, 'list': l})
