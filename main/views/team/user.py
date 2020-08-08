from django import forms
from django.http import JsonResponse
from django.views.generic import View

from util.decorator.auth import app_auth
from util.decorator.param import validate_args


class RelatedTeamList(View):
    ORDERS = ('team__time_created', '-team__time_created',
              'team__name', '-team__name')

    # noinspection PyUnusedLocal
    @app_auth
    @validate_args({
        'offset': forms.IntegerField(required=False, min_value=0),
        'limit': forms.IntegerField(required=False, min_value=0),
        'order': forms.IntegerField(required=False, min_value=0, max_value=3),
    })
    def get(self, request, offset=0, limit=10, order=1):
        """获取当前用户参与的团队列表

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
        c = request.user.teams.count()
        teams = request.user.teams.order_by(k)[i:j]
        l = [{'id': t.team.id,
              'name': t.team.name,
              'icon_url': t.team.icon,
              'owner_id': t.team.owner.id,
              'liker_count': t.team.likers.count(),
              'visitor_count': t.team.visitors.count(),
              'member_count': t.team.members.count(),
              'fields': [t.team.field1, t.team.field2],
              'tags': [tag.name for tag in t.team.tags.all()],
              'time_created': t.team.time_created} for t in teams]
        return JsonResponse({'count': c, 'list': l, 'code': 0})


class OwnedTeamList(View):
    ORDERS = ('time_created', '-time_created', 'name', '-name')

    # noinspection PyUnusedLocal
    @app_auth
    @validate_args({
        'offset': forms.IntegerField(required=False, min_value=0),
        'limit': forms.IntegerField(required=False, min_value=0),
        'order': forms.IntegerField(required=False, min_value=0, max_value=3),
    })
    def get(self, request, offset=0, limit=10, order=1):
        """获取当前用户创建的团队列表

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
        c = request.user.owned_teams.count()
        teams = request.user.owned_teams.order_by(k)[i:j]
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
        return JsonResponse({'count': c, 'list': l, 'code': 0})