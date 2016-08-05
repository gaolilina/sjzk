from django import forms
from django.db import transaction
from django.http import HttpResponseRedirect
from django.http import JsonResponse
from django.views import View

from ChuangYi.settings import UPLOADED_URL
from ..models import Team, User, TeamAchievement
from ..utils import abort, action, save_uploaded_image
from ..utils.decorators import *

__all__ = ('List', 'Profile', 'Icon', 'MemberList', 'Member',
           'MemberRequestList', 'MemberRequest', 'Invitation',
           'AllAchievementList', 'AllAchievement', 'AchievementList')


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

        team.members.create(user=request.user)

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


class MemberList(View):
    ORDERS = (
        'time_created',
        '-time_created',
        'user__name',
        '-user__name',
    )

    @fetch_object(Team, 'team')
    @require_token
    @validate_args({
        'offset': forms.IntegerField(required=False, min_value=0),
        'order': forms.IntegerField(required=False, min_value=0, max_value=3),

    })
    def get(self, request, team, offset=0, limit=10, order=1):
        """获取团队的成员列表

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
                username: 用户名
                name: 用户昵称
                time_created: 成为团队成员时间
        """

        i, j, k = offset, offset + limit, self.ORDERS[order]
        c = team.members.count()
        rs = team.members.order_by(k)[i:j]
        l = [{'id': r.user.id,
              'username': r.user.username,
              'name': r.user.name,
              'time_created': r.time_created} for r in rs]
        return JsonResponse({'count': c, 'list': l})


class Member(View):
    @fetch_object(Team, 'team')
    @fetch_object(User, 'user')
    @require_token
    def get(self, request, team, user):
        """检查用户是否为团队成员"""

        if team.members.filter(user=user).exists():
            abort(200)
        abort(404)

    @fetch_object(Team, 'team')
    @fetch_object(User, 'user')
    @require_token
    def post(self, request, team, user):
        """将目标用户添加为自己的团队成员（对方需发送过加入团队申请）"""

        if request.user != team.owner:
            abort(403)

        if not team.member_requests.filter(user=user):
            abort(403)

        # 若对方已是团队成员则不做处理
        if team.members.filter(user=user).exists():
            abort(200)

        # 在事务中建立关系，并删除对应的加团队申请
        with transaction.atomic():
            team.member_requests.filter(user=user).delete()
            team.members.create(user=user)
            action.join_team(user, team)
        abort(200)

    @fetch_object(Team, 'team')
    @fetch_object(User, 'user')
    @require_token
    def delete(self, request, team, user):
        """退出团队(默认)/删除成员"""
        if request.user != team.owner:
            abort(403)

        if user != request.user or user == team.owner:
            abort(403)

        qs = team.members.filter(user=user)
        if qs.exists():
            qs.delete()
            abort(200)
        abort(404)


class MemberRequestList(View):
    @fetch_object(Team, 'team')
    @validate_args({'offset': forms.IntegerField(required=False)})
    @require_token
    def get(self, request, team, offset=0, limit=10):
        """获取团队的加入申请列表

        * 若当前用户为团队创始人时，按请求时间逆序获取收到的加团队申请信息，
          拉取后的申请 标记为已读
        * 若不为团队创始人时，检查当前用户是否已经发送过加团队请求，
          并且该请求未被处理（接收或忽略）

        :param limit: 拉取的数量上限
        :return: request.user 为团队创始人时，200 | 404
        :return: request.user 不为团队创始人时
            count: 申请总条数
            list: 加入团队请求信息列表
                id: 用户ID
                username: 用户名
                name: 用户昵称
                description: 附带消息
                time_created: 请求发出的时间
        """
        if request.user == team.owner:
            # 拉取团队的加入申请信息
            c = team.member_requests.count()
            qs = team.member_requests.all()[offset:offset + limit]

            l = [{'id': r.sender.id,
                  'username': r.sender.username,
                  'name': r.sender.name,
                  'description': r.description,
                  'time_created': r.time_created} for r in qs]
            return JsonResponse({'count': c, 'list': l})

        if team.member_requests.filter(user=request.user).exists():
            abort(200)
        abort(404)

    @fetch_object(Team, 'team')
    @require_token
    @validate_args({
        'description': forms.CharField(required=False, max_length=100)
    })
    def post(self, request, team, description=''):
        """向团队发出加入申请

        :param description: 附带消息
        """
        if request.user == team.owner:
            abort(403)

        if team.members.exist(user=request.user):
            abort(403)

        if team.member_requests.filter(user=request.user).exists():
            abort(200)

        if team.invitations.filter(user=request.user).exists():
            abort(403)

        team.member_requests.create(user=request.user, description=description)
        abort(200)


class MemberRequest(View):
    @fetch_object(Team, 'team')
    @fetch_object(User, 'user')
    @require_token
    def delete(self, request, team, user):
        """忽略某用户的加团队请求"""

        if request.user != team.owner:
            abort(403)

        qs = team.member_requests.filter(user=user)
        if not qs.exists():
            abort(404)
        qs.delete()
        abort(200)


class Invitation(View):
    @fetch_object(Team, 'team')
    @fetch_object(User, 'user')
    @require_token
    @validate_args({
        'description': forms.CharField(required=False, max_length=100)
    })
    def post(self, request, team, user, description=''):
        """向用户发出加入团队邀请

        :param description: 附带消息
        """
        if request.user != team.owner:
            abort(403)

        if user == team.owner:
            abort(403)

        if team.members.filter(user=user).exists():
            abort(403)

        if team.invitations.filter(user=user).exists():
            abort(200)

        if team.member_requests.filter(user=user).exists():
            abort(403)

        team.invitations.create(user=user, description=description)
        abort(200)


class AllAchievementList(View):
    ORDERS = ('time_created', '-time_created')

    @require_token
    @validate_args({
        'offset': forms.IntegerField(required=False, min_value=0),
        'order': forms.IntegerField(required=False, min_value=0, max_value=3),
    })
    def get(self, request, offset=0, limit=10, order=1):
        """获取所有团队发布的成果

        :param offset: 偏移量
        :param limit: 数量上限
        :param order: 排序方式
            0: 发布时间升序
            1: 发布时间降序（默认值）
        :return:
            count: 成果总数
            list: 成果列表
                id: 成果ID
                team_id: 团队ID
                team_name: 团队名称
                description: 成果描述
                picture_url: 图片URL
                time_created: 发布时间
        """
        i, j, k = offset, offset + limit, self.ORDERS[order]
        c = TeamAchievement.objects.count()
        achievements = TeamAchievement.objects.order_by(k)[i:j]
        l = [{'id': a.id,
              'team_id': a.team.id,
              'team_name': a.team.name,
              'description': a.description,
              'picture_url': a.picture_url,
              'time_created': a.time_created} for a in achievements]
        return JsonResponse({'count': c, 'list': l})


class AllAchievement(View):
    @fetch_object(TeamAchievement, 'achievement')
    @require_token
    def delete(self, request, team, achievement):
        """删除成果"""

        if request.user != achievement.team.owner:
            abort(403)
        achievement.delete()
        abort(200)


class AchievementList(View):
    ORDERS = ('time_created', '-time_created')

    @fetch_object(Team, 'team')
    @require_token
    @validate_args({
        'offset': forms.IntegerField(required=False, min_value=0),
        'order': forms.IntegerField(required=False, min_value=0, max_value=3),
    })
    def get(self, request, team, offset=0, limit=10, order=1):
        """获取团队发布的成果

        :param offset: 偏移量
        :param limit: 数量上限
        :param order: 排序方式
            0: 发布时间升序
            1: 发布时间降序（默认值）
        :return:
            count: 成果总数
            list: 成果列表
                id: 成果ID
                description: 成果描述
                picture_url: 图片URL
                time_created: 发布时间
        """
        i, j, k = offset, offset + limit, self.ORDERS[order]
        c = team.achievements.count()
        achievements = team.achievements.order_by(k)[i:j]
        l = [{'id': a.id,
              'description': a.description,
              'picture_url': a.picture_url,
              'time_created': a.time_created} for a in achievements]
        return JsonResponse({'count': c, 'list': l})

    @fetch_object(Team, 'team')
    @require_token
    @validate_args({
        'description': forms.CharField(min_length=1, max_length=100),
    })
    def post(self, request, team, description):
        """发布成果

        :param description: 成果描述
        :return: achievement_id: 成果id
        """
        if request.user != team.owner:
            abort(403)

        achievement = TeamAchievement(team=team, description=description)
        picture = request.FILES.get('image')
        if picture:
            filename = save_uploaded_image(picture)
            if filename:
                achievement.picture = filename
        achievement.save()
        return JsonResponse({'achievement_id': achievement.id})

