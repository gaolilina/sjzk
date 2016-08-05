from django import forms
from django.db import transaction
from django.http import HttpResponseRedirect
from django.http import JsonResponse
from django.views import View

from ChuangYi.settings import UPLOADED_URL
from ..models import Team
from ..utils import abort, action, save_uploaded_image
from ..utils.decorators import *

__all__ = ['List', 'Profile', 'Icon']


class List(View):
    ORDERS = ('time_created', '-time_created', 'name', '-name')

    # noinspection PyUnusedLocal
    @require_token
    @validate_args({
        'offset': forms.IntegerField(required=False, min_value=0),
        'order': forms.IntegerField(required=False, min_value=0, max_value=3),
    })
    def get(self, request, offset=0, limit=10, order=1):
        """获取团队列表

        :param offset: 偏移量
        :param limit: 数量上限
        :param order: 排序方式
            0: 注册时间升序
            1: 注册时间降序（默认值）
            2: 昵称升序
            3: 昵称降序
        :return:
            count: 团队总数
            list: 团队列表
                id: 团队ID
                name: 团队名
                owner_id: 创建者ID
                liker_count: 点赞数
                visitor_count: 最近7天访问数
                member_count: 团队成员人数
                fields: 所属领域，格式：['field1', 'field2']
                tags: 标签，格式：['tag1', 'tag2', ...]
                time_created: 注册时间
        """
        i, j, k = offset, offset + limit, self.ORDERS[order]
        c = Team.enabled.count()
        teams = Team.enabled.order_by(k)[i:j]
        l = [{'id': t.id,
              'name': t.name,
              'owner_id': t.owner.id,
              'liker_count': t.likers.count(),
              'visitor_count': t.visitors.count(),
              'member_count': t.members.count(),
              'fields': [t.field1, t.field2],
              'tags': t.tags.values_list('name', flat=True),
              'time_created': t.time_created} for t in teams]
        return JsonResponse({'count': c, 'list': l})

    @require_token
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
        """新建团队

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

        team = Team(owner=request.user, name=name)

        for k in kwargs:
            setattr(team, k, kwargs[k])

        if fields:
            fields = fields.split('|')[:2]
        if len(fields) < 2:
            fields.append('')
        team.field1, team.field2 = fields[0].strip(), fields[1].strip()
        team.save()

        if tags:
            tags = tags.split('|')[:5]
        with transaction.atomic():
            request.user.tags.delete()
            order = 0
            for tag in tags:
                tag = tag.strip()
                if tag:
                    request.user.tags.create(name=tag, order=order)
                    order += 1

        action.create_team(request.user, team)
        return JsonResponse({'team_id': team.id})


class Profile(View):
    @fetch_object(Team, 'team')
    @require_token
    def get(self, request, team):
        """获取团队的基本资料

        :param: team_id : 团队ID
        :return:
            id: 团队ID
            name: 团队名
            owner_id: 创始人id
            time_created: 注册时间
            is_recruiting：是否招募新成员
            description: 团队简介
            url: 团队链接
            liker_count: 点赞数
            fan_count: 粉丝数
            visitor_count: 最近访客数
            province:
            city:
            county:
            fields: 所属领域，格式：['field1', 'field2']
            tags: 标签，格式：['tag1', 'tag2', ...]
        """
        if team.owner != request.user:
            team.visotors.update_or_create(visitor=request.user)

        r = dict()
        r['id'] = team.id
        r['name'] = team.name
        r['owner_id'] = team.owner.id
        r['time_created'] = team.time_created
        r['is_recruiting'] = team.is_recruiting
        r['description'] = team.description
        r['url'] = team.url
        r['liker_count'] = team.likers.count()
        r['fan_count'] = team.followers.count()
        r['visitor_count'] = team.visitors.count()
        r['fields'] = [team.fields1, team.field2]
        r['province'] = team.province
        r['city'] = team.city
        r['county'] = team.county
        r['tags'] = team.tags.values_list('name', flat=True)

        return JsonResponse(r)

    @fetch_object(Team, 'team')
    @require_token
    @validate_args({
        'name': forms.CharField(max_length=20),
        'description': forms.CharField(required=False, max_length=100),
        'is_recruiting': forms.BooleanField(required=False),
        'url': forms.CharField(required=False, max_length=100),
        'province': forms.CharField(required=False, max_length=20),
        'city': forms.CharField(required=False, max_length=20),
        'county': forms.CharField(required=False, max_length=20),
        'fields': forms.CharField(required=False, max_length=100),
        'tags': forms.CharField(required=False, max_length=100),
    })
    def post(self, request, team, **kwargs):
        """修改团队资料

        :param team: 团队ID
        :param kwargs:
            name: 团队名
            description: 团队简介
            is_recruiting：是否招募新成员
            url: 团队链接
            province:
            city:
            county:
            fields: 团队领域，格式:'field1|field2'
            tags: 标签，格式：'tag1|tag2|tag3|...'
        """
        if request.user != team.owner:
            abort(403)

        fields = kwargs.pop('fields', None)
        tags = kwargs.pop('tags', None)

        for k in kwargs:
            setattr(team, k, kwargs[k])

        if fields:
            fields = fields.split('|')[:2]
        if len(fields) < 2:
            fields.append('')
        team.field1, team.field2 = fields[0].strip(), fields[1].strip()

        team.save()

        if tags:
            tags = tags.split('|')[:5]
        with transaction.atomic():
            request.user.tags.delete()
            order = 0
            for tag in tags:
                tag = tag.strip()
                if tag:
                    request.user.tags.create(name=tag, order=order)
                    order += 1

        abort(200)


class Icon(View):
    @fetch_object(Team, 'team')
    @require_token
    def get(self, request, team):
        """获取团队头像"""

        if team.icon:
            return HttpResponseRedirect(UPLOADED_URL + team.icon)
        abort(404)

    @fetch_object(Team, 'team')
    @require_token
    def post(self, request, team):
        """设置团队的头像"""

        if request.user != team.owner:
            abort(403)

        icon = request.FILES.get('image')
        if not icon:
            abort(400)

        filename = save_uploaded_image(icon)
        if filename:
            team.icon = filename
            team.save()
            abort(200)
        abort(400)
