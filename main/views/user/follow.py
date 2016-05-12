from django import forms
from django.http import JsonResponse
from django.views.generic import View

from main.decorators import check_object_id, require_token, validate_input
from main.models import User, Team
from main.models.follow import UserFollower, TeamFollower
from main.responses import *


# todo: test following-related
class Fans(View):
    get_dict = {
        'offset': forms.IntegerField(required=False, min_value=0),
        'limit': forms.IntegerField(required=False, min_value=0),
        'order': forms.IntegerField(required=False, min_value=0, max_value=3),
    }
    available_orders = [
        'create_time', '-create_time',
        'follower__name', '-follower__name',
    ]

    @check_object_id(User.enabled, 'user')
    @require_token
    @validate_input(get_dict)
    def get(self, request, user=None, offset=0, limit=10, order=1):
        """
        获取粉丝列表

        :param offset: 偏移量
        :param limit: 数量上限
        :param order: 排序方式
            0: 关注时间升序
            1: 关注时间降序（默认值）
            2: 昵称升序
            3: 昵称降序
        :return:
            count: 粉丝总数
            list: 粉丝列表
                id: 用户ID
                username: 用户名
                name: 用户昵称
                icon_url: 用户头像URL
                create_time: 关注时间
        """
        user = user or request.user

        i, j, k = offset, offset + limit, self.available_orders[order]
        c = user.follower_records.count()
        qs = user.follower_records.order_by(k)[i:j]
        l = [{'id': r.follower.id,
              'username': r.follower.username,
              'name': r.follower.name,
              'icon_url': r.follower.icon_url,
              'create_time': r.create_time} for r in qs]
        return JsonResponse({'count': c, 'list': l})


class Fan(View):
    @check_object_id(User.enabled, 'user')
    @check_object_id(User.enabled, 'other_user')
    def get(self, request, other_user, user=None):
        """
        判断other_user是否为user的粉丝

        """
        user = user or request.user

        return Http200() if UserFollower.exist(user, other_user) \
            else Http404()


class FollowedUsers(View):
    get_dict = {
        'offset': forms.IntegerField(required=False, min_value=0),
        'limit': forms.IntegerField(required=False, min_value=0),
        'order': forms.IntegerField(required=False, min_value=0, max_value=3),
    }
    available_orders = [
        'create_time', '-create_time',
        'followed__name', '-followed__name',
    ]

    @check_object_id(User.enabled, 'user')
    @require_token
    @validate_input(get_dict)
    def get(self, request, user=None, offset=0, limit=10, order=1):
        """
        获取用户的关注用户列表

        :param offset: 偏移量
        :param limit: 数量上限
        :param order: 排序方式
            0: 关注时间升序
            1: 关注时间降序（默认值）
            2: 昵称升序
            3: 昵称降序
        :return:
            count: 关注的用户总数
            list: 关注的用户列表
                id: 用户ID
                username: 用户名
                name: 用户昵称
                icon_url: 用户头像URL
                create_time: 关注时间
        """
        user = user or request.user

        i, j, k = offset, offset + limit, self.available_orders[order]
        c = user.followed_user_records.count()
        qs = user.followed_user_records.order_by(k)[i:j]
        l = [{'id': r.followed.id,
              'username': r.followed.username,
              'name': r.followed.name,
              'icon_url': r.followed.icon_url,
              'create_time': r.create_time} for r in qs]
        return JsonResponse({'count': c, 'list': l})


class FollowedUser(View):
    @check_object_id(User.enabled, 'user')
    @check_object_id(User.enabled, 'other_user')
    def get(self, request, other_user, user=None):
        """
        判断user是否关注了other_user

        """
        user = user or request.user

        return Http200() if UserFollower.exist(other_user, user) \
            else Http404()


class FollowedUserSelf(FollowedUser):
    @check_object_id(User.enabled, 'other_user')
    def post(self, request, other_user):
        """
        令当前用户关注other_user

        """
        # 若已关注返回403
        if UserFollower.exist(other_user, request.user):
            return Http403('already followed the object')

        other_user.follower_records.create(follower=request.user)
        return Http200()

    @check_object_id(User.enabled, 'other_user')
    def delete(self, request, other_user):
        """
        令当前用户取消关注other_user

        """
        if not UserFollower.exist(other_user, request.user):
            return Http403('not followed the object')
        qs = other_user.follower_records.filter(follower=request.user)
        qs.delete()
        return Http200()


class FollowedTeams(View):
    get_dict = {
        'offset': forms.IntegerField(required=False, min_value=0),
        'limit': forms.IntegerField(required=False, min_value=0),
        'order': forms.IntegerField(required=False, min_value=0, max_value=3),
    }
    available_orders = [
        'create_time', '-create_time',
        'followed__name', '-followed__name',
    ]

    @check_object_id(User.enabled, 'user')
    @check_object_id(Team.enabled, 'team')
    @require_token
    @validate_input(get_dict)
    def get(self, request, team, user=None, offset=0, limit=10, order=1):
        """
        获取用户的关注团队列表

        :param offset: 偏移量
        :param limit: 数量上限
        :param order: 排序方式
            0: 关注时间升序
            1: 关注时间降序（默认值）
            2: 团队名称升序
            3: 团队名称降序
        :return:
            count: 关注的团队总数
            list: 关注的用户列表
                id: 团队ID
                name: 团队昵称
                icon_url: 团队图标URL
                create_time: 关注时间
        """
        user = user or request.user

        i, j, k = offset, offset + limit, self.available_orders[order]
        c = user.followed_team_records.count()
        qs = user.followed_team_records.order_by(k)[i:j]
        l = [{'id': r.followed.id,
              'name': r.followed.name,
              'icon_url': r.followed.icon_url,
              'create_time': r.create_time} for r in qs]
        return JsonResponse({'count': c, 'list': l})


class FollowedTeam(View):
    @check_object_id(User.enabled, 'user')
    @check_object_id(Team.enabled, 'team')
    def get(self, request, team, user=None):
        """
        判断user是否关注了team

        """
        user = user or request.user

        return Http200() if TeamFollower.exist(team, user) \
            else Http404()


class FollowedTeamSelf(FollowedTeam):
    @check_object_id(Team.enabled, 'team')
    @require_token
    def post(self, request, team):
        """
        令当前用户关注team

        """
        # 若已关注返回403
        if TeamFollower.exist(team, request.user):
            return Http403('already followed the object')

        team.follower_records.create(follower=request.user)
        return Http200()

    @check_object_id(Team.enabled, 'team')
    @require_token
    def delete(self, request, team):
        """
        令当前用户取消关注team

        """
        if not TeamFollower.exist(team, request.user):
            return Http403('not followed the object')
        qs = team.follower_records.filter(follower=request.user)
        qs.delete()
        return Http200()
