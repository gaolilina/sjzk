from django import forms
from django.views.generic import View

from main.models import Team
from main.models.need import TeamNeed
from main.utils import abort, get_score_stage, action
from main.utils.decorators import require_verification_token
from main.utils.dfa import check_bad_words
from main.views.search.need import NeedSearch
from util.decorator.param import fetch_object, validate_args


class CreateNeed(View):
    @fetch_object(Team.enabled, 'team')
    def get(self, request, **kwargs):
        """
        当前方法被迁移到 NeedSearch
        :param request:
        :param kwargs:
        :return:
        """
        return NeedSearch().get(request, kwargs)

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
            abort(500,'需求类型错误')

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
            abort(400, '含有非法词汇')

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
            abort(400, '含有非法词汇')

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
            abort(400, '含有非法词汇')

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