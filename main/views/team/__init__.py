from django import forms
from django.db import transaction
from django.db.models import Q
from django.http import JsonResponse
from django.views.generic import View

from main.models import Team
from main.utils import abort, action, get_score_stage
from main.utils.decorators import *
from main.utils.dfa import check_bad_words
from main.utils.recommender import calculate_ranking_score
from util.decorator.param import validate_args

__all__ = ('TeamCreate', 'Screen')


class TeamCreate(View):
    ORDERS = ('time_created', '-time_created', 'name', '-name')

    @require_verification_token
    @validate_args({
        'name': forms.CharField(max_length=20),
        'description': forms.CharField(required=False, max_length=100),
        'url': forms.CharField(required=False, max_length=100),
        'province': forms.CharField(required=False, max_length=20),
        'city': forms.CharField(required=False, max_length=20),
        'county': forms.CharField(required=False, max_length=20),
        'fields': forms.CharField(required=False, max_length=100),
        'tags': forms.CharField(required=False, max_length=100),
    })
    def post(self, request, **kwargs):
        """新建团队，同时调用融云接口为该团队创建一个对应的群聊

        :param kwargs:
            name: 团队名称
            description: 团队描述
            url: 团队链接
            province:
            city:
            county:
            fields: 团队领域，格式:'field1|field2'
            tags: 标签，格式：'tag1|tag2|tag3|...'
        :return: team_id: 团队id
        """
        name = kwargs.pop('name')
        fields = kwargs.pop('fields', None)
        tags = kwargs.pop('tags', None)

        # 昵称唯一性验证
        if Team.enabled.filter(name=name).count() != 0:
            abort(403, '团队名已被注册')
        # 昵称非法词验证
        if check_bad_words(name):
            abort(403, '团队名含非法词汇')

        team = Team(owner=request.user, name=name)
        team.save()

        for k in kwargs:
            setattr(team, k, kwargs[k])
        fields = fields.split('|')[:2] if fields is not None else ('', '')
        team.field1, team.field2 = fields[0].strip(), fields[1].strip()

        if tags:
            tags = tags.split('|')[:5]
            with transaction.atomic():
                team.tags.all().delete()
                order = 0
                for tag in tags:
                    tag = tag.strip()
                    if tag:
                        team.tags.create(name=tag, order=order)
                        order += 1
        team.save()

        action.create_team(request.user, team)
        request.user.score += get_score_stage(2)
        request.user.score_records.create(
            score=get_score_stage(2), type="能力", description="成功创建一个团队")
        request.user.save()
        return JsonResponse({'team_id': team.id})


class Screen(View):
    ORDERS = ('time_created', '-time_created', 'name', '-name')

    @validate_args({
        'offset': forms.IntegerField(required=False, min_value=0),
        'limit': forms.IntegerField(required=False, min_value=0),
        'order': forms.IntegerField(required=False, min_value=0, max_value=3),
        'name': forms.CharField(required=False, max_length=20),
        'province': forms.CharField(required=False, max_length=20),
        'city': forms.CharField(required=False, max_length=20),
        'county': forms.CharField(required=False, max_length=20),
        'field': forms.CharField(required=False, max_length=10),
    })
    def get(self, request, offset=0, limit=10, order=None, **kwargs):
        """
        筛选团队

        :param offset: 偏移量
        :param limit: 数量上限
        :param order: 排序方式（若无则进行个性化排序）
            0: 注册时间升序
            1: 注册时间降序
            2: 昵称升序
            3: 昵称降序
        :param kwargs: 搜索条件
            name: 团队名包含字段
            province: 省
            city: 市
            county: 区/县
            field: 领域

        :return:
            count: 团队总数
            list: 团队列表
                id: 团队ID
                name: 团队名
                icon_url: 头像
                owner_id: 创建者ID
                liker_count: 点赞数
                visitor_count: 最近7天访问数
                member_count: 团队成员人数
                fields: 所属领域，格式：['field1', 'field2']
                tags: 标签，格式：['tag1', 'tag2', ...]
                time_created: 注册时间
        """
        teams = Team.enabled

        i, j = offset, offset + limit
        name = kwargs.pop('name', '')
        if name:
            # 按用户昵称段检索
            teams = teams.filter(name__icontains=name)

        province = kwargs.pop('province', '')
        if province:
            # 按省会筛选
            teams = teams.filter(province=province)
        city = kwargs.pop('city', '')
        if city:
            # 按城市筛选
            teams = teams.filter(city=city)
        county = kwargs.pop('county', '')
        if county:
            # 按区/县筛选
            teams = teams.filter(county=county)
        field = kwargs.pop('field', '')
        if field:
            # 按领域筛选
            teams = teams.filter(Q(field1=field) | Q(field2=field))

        teams = teams.all()
        c = teams.count()
        if order is not None:
            teams = teams.order_by(self.ORDERS[order])[i:j]
        else:
            # 将结果进行个性化排序
            team_list = list()
            for t in teams:
                if fetch_user_by_token(request):
                    team_list.append((t, calculate_ranking_score(request.user, t)))
                else:
                    team_list.append((t, 0))
            team_list = sorted(team_list, key=lambda x: x[1], reverse=True)
            teams = (t[0] for t in team_list[i:j])
        l = [{'id': t.id,
              'name': t.name,
              'icon_url': t.icon,
              'owner_id': t.owner.id,
              'liker_count': t.likers.count(),
              'visitor_count': t.visitors.count(),
              'member_count': t.members.count(),
              'fields': [t.field1, t.field2],
              'tags': [tag.name for tag in t.tags.all()],
              'time_created': t.time_created} for t in teams]
        return JsonResponse({'count': c, 'list': l})
