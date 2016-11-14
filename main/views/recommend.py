from django import forms
from django.http import JsonResponse, HttpResponseRedirect
from django.utils import timezone
from django.views.generic import View

from ChuangYi.settings import UPLOADED_URL
from main.models import Team, User, TeamNeed
from ..utils import abort
from main.utils.decorators import *

__all__ = ('UserRecommend', 'TeamRecommend', 'OutsourceNeedTeamRecommend',
           'UndertakeNeedTeamRecommend')


class UserRecommend(View):
    ORDERS = ('time_created', '-time_created', 'name', '-name')

    @require_token
    @validate_args({
        'offset': forms.IntegerField(required=False, min_value=0),
        'limit': forms.IntegerField(required=False, min_value=0),
        'order': forms.IntegerField(required=False, min_value=0, max_value=3),
    })
    def get(self, request, offset=0, limit=10, order=1):
        """
        为用户推荐用户

        :param offset: 偏移量
        :param limit: 数量上限
        :param order: 排序方式
            0: 注册时间升序
            1: 注册时间降序（默认值）
            2: 昵称升序
            3: 昵称降序
        :return:
            count: 用户总数
            list: 用户列表
                id: 用户ID
                username: 用户名
                name: 用户昵称
                icon_url: 用户头像
                gender: 性别
                like_count: 点赞数
                fan_count: 粉丝数
                visitor_count: 访问数
                tags: 标签
                time_created: 注册时间
        """
        i, j, k = offset, offset + limit, self.ORDERS[order]
        user_tags = request.user.tags
        user_dic = {}
        for tag in user_tags:
            users_tmp = User.enabled.filter(tags__name=tag).order_by(k)
            for user in users_tmp:
                if user in user_dic:
                    user_dic[user] += 1
                else:
                    user_dic[user] = 1

        user_dic = sorted(user_dic.items(), key=lambda x: x[1], reverse=True)
        users = []
        for user_list in user_dic:
            users.append(user_list[0])
        c = len(users)
        l = [{'id': u.id,
              'username': u.username,
              'name': u.name,
              'icon_url': HttpResponseRedirect(
                  UPLOADED_URL + u.icon) if u.icon else '',
              'gender': u.profile.gender,
              'like_count': u.like_count,
              'fan_count': u.fan_count,
              'visitor_count': u.visitor_count,
              'tags': u.tags.values_list('name', flat=True),
              'time_created': u.time_created} for u in users[i:j]]
        return JsonResponse({'count': c, 'list': l})


class TeamRecommend(View):
    ORDERS = ('time_created', '-time_created', 'name', '-name')

    @require_token
    @validate_args({
        'offset': forms.IntegerField(required=False, min_value=0),
        'limit': forms.IntegerField(required=False, min_value=0),
        'order': forms.IntegerField(required=False, min_value=0, max_value=3),
    })
    def get(self, request, offset=0, limit=10, order=1):
        """为用户推荐团队
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
        team_tags = request.user.tags
        team_dic = {}
        for tag in team_tags:
            teams_tmp = Team.enabled.filter(tags__name=tag).order_by(k)
            for team in teams_tmp:
                if team in team_dic:
                    team_dic[team] += 1
                else:
                    team_dic[team] = 1

        team_dic = sorted(team_dic.items(), key=lambda x: x[1], reverse=True)
        teams = []
        for team_list in team_dic:
            teams.append(team_list[0])
        c = len(teams)
        l = [{'id': t.id,
              'name': t.name,
              'icon_url': HttpResponseRedirect(
                  UPLOADED_URL + t.icon) if t.icon else '',
              'owner_id': t.owner.id,
              'liker_count': t.likers.count(),
              'visitor_count': t.visitors.count(),
              'member_count': t.members.count(),
              'fields': [t.field1, t.field2],
              'tags': t.tags.values_list('name', flat=True),
              'time_created': t.time_created} for t in teams[i:j]]
        return JsonResponse({'count': c, 'list': l})


class OutsourceNeedTeamRecommend(View):
    ORDERS = ('time_created', '-time_created', 'name', '-name')

    @require_token
    @fetch_object(TeamNeed.objects, 'need')
    @validate_args({
        'offset': forms.IntegerField(required=False, min_value=0),
        'limit': forms.IntegerField(required=False, min_value=0),
        'order': forms.IntegerField(required=False, min_value=0, max_value=3),
    })
    def get(self, request, need, offset=0, limit=10, order=1):
        """为外包需求推荐团队
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
        if need.team.owner != request.user:
            abort(403)
        i, j, k = offset, offset + limit, self.ORDERS[order]
        field = need.field
        # 找出符合条件的承接需求(领域、类型、截至日期和起止时间)
        undertake_needs = TeamNeed.objects.filter(
            field=field,
            type=2,
            status=0,
            deadline__lt=timezone.now(),
            time_ended__lt=need.time_started)

        team_dic = {}
        # 对团队按指定条件增加在队列中的权值
        for undertake_need in undertake_needs:
            team = undertake_need.team
            if team in team_dic:
                team_dic[team] += 1
            else:
                team_dic[team] = 1
            if need.time_started >= undertake_need.time_started:
                team_dic[team] += 1
            if need.time_ended <= undertake_need.time_ended:
                team.dic[team] += 1

        team_dic = sorted(team_dic.items(), key=lambda x: x[1], reverse=True)
        teams = []
        for team_list in team_dic:
            teams.append(team_list[0])
        c = len(teams)
        l = [{'id': t.id,
              'name': t.name,
              'icon_url': HttpResponseRedirect(
                  UPLOADED_URL + t.icon) if t.icon else '',
              'owner_id': t.owner.id,
              'liker_count': t.likers.count(),
              'visitor_count': t.visitors.count(),
              'member_count': t.members.count(),
              'fields': [t.field1, t.field2],
              'tags': t.tags.values_list('name', flat=True),
              'time_created': t.time_created} for t in teams[i:j]]
        return JsonResponse({'count': c, 'list': l})


class UndertakeNeedTeamRecommend(View):
    ORDERS = ('time_created', '-time_created', 'name', '-name')

    @require_token
    @fetch_object(TeamNeed.objects, 'need')
    @validate_args({
        'offset': forms.IntegerField(required=False, min_value=0),
        'limit': forms.IntegerField(required=False, min_value=0),
        'order': forms.IntegerField(required=False, min_value=0, max_value=3),
    })
    def get(self, request, need, offset=0, limit=10, order=1):
        """为承接需求推荐团队
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
        if need.team.owner != request.user:
            abort(403)
        i, j, k = offset, offset + limit, self.ORDERS[order]
        field = need.field
        # 找出符合条件外包接需求(领域、类型、截至日期和起止时间)
        outsource_needs = TeamNeed.objects.filter(
            field=field,
            status=0,
            type=1,
            deadline__lt=timezone.now(),
            time_ended__lt=need.time_started)

        team_dic = {}
        # 对团队按指定条件增加在队列中的权值
        for outsource_need in outsource_needs:
            team = outsource_need.team
            if team in team_dic:
                team_dic[team] += 1
            else:
                team_dic[team] = 1
            if need.time_started >= outsource_need.time_started:
                team_dic[team] += 1
            if need.time_ended <= outsource_need.time_ended:
                team.dic[team] += 1

        team_dic = sorted(team_dic.items(), key=lambda x: x[1], reverse=True)
        teams = []
        for team_list in team_dic:
            teams.append(team_list[0])
        c = len(teams)
        l = [{'id': t.id,
              'name': t.name,
              'icon_url': HttpResponseRedirect(
                  UPLOADED_URL + t.icon) if t.icon else '',
              'owner_id': t.owner.id,
              'liker_count': t.likers.count(),
              'visitor_count': t.visitors.count(),
              'member_count': t.members.count(),
              'fields': [t.field1, t.field2],
              'tags': t.tags.values_list('name', flat=True),
              'time_created': t.time_created} for t in teams[i:j]]
        return JsonResponse({'count': c, 'list': l})
