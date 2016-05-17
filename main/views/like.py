from django import forms
from django.http import JsonResponse
from django.views.generic import View

from main.decorators import validate_input, require_token, check_object_id
from main.models import User, Team
from main.responses import *


# todo: like-related test cases
class Likers(View):
    get_dict = {
        'offset': forms.IntegerField(required=False, min_value=0),
        'limit': forms.IntegerField(required=False, min_value=0),
        'order': forms.IntegerField(required=False, min_value=0, max_value=3),
    }
    available_orders = (
        'create_time', '-create_time',
        'follower__name', '-follower__name',
    )

    @validate_input(get_dict)
    def get(self, request, obj, offset=0, limit=10, order=1):
        """
        获取对象的点赞者列表
        :param offset: 偏移量
        :param limit: 数量上限
        :param order: 排序方式
            0: 点赞时间升序
            1: 点赞时间降序（默认值）
            2: 昵称升序
            3: 昵称降序
        :return:
            count: 总点赞量
            list: 点赞者列表
                id: 用户ID
                username: 用户名
                name: 用户昵称
                icon_url: 用户头像URL
                create_time: 点赞时间
        """
        i, j, k = offset, offset + limit, self.available_orders[order]
        c = obj.liker_records.count()
        qs = obj.liker_records.order_by(k)[i:j]
        l = [{'id': r.liker.id,
              'username': r.liker.username,
              'name': r.liker.name,
              'icon_url': r.liker.icon_url,
              'create_time': r.create_time} for r in qs]
        return JsonResponse({'count': c, 'list': l})


# noinspection PyMethodOverriding
class UserLikers(Likers):
    @require_token
    @check_object_id(User.enabled, 'user')
    def get(self, request, user=None):
        user = user or request.user
        return super(UserLikers, self).get(request, user)


# noinspection PyMethodOverriding
class TeamLikers(Likers):
    @require_token
    @check_object_id(Team.enabled, 'team')
    def get(self, request, team):
        return super(TeamLikers, self).get(request, team)


class Liker(View):
    def get(self, request, obj, other_user):
        """
        判断other_user是否对obj点过赞

        """
        return Http200() if obj.liker_records.filter(
            liker=other_user).exists() else Http400()


class UserLiker(Liker):
    @check_object_id(User.enabled, 'user')
    @check_object_id(User.enabled, 'other_user')
    @require_token
    def get(self, request, other_user, user=None):
        user = user or request.user
        return super(UserLiker, self).get(request, user, other_user)


class TeamLiker(Liker):
    @check_object_id(Team.enabled, 'team')
    @check_object_id(User.enabled, 'other_user')
    @require_token
    def get(self, request, team, other_user):
        return super(TeamLiker, self).get(request, team, other_user)


class LikedObject(View):
    """
    与当前用户点赞行为相关的View类

    """
    @require_token
    def get(self, request, obj):
        """
        判断当前用户是否对某个对象点过赞

        """
        return Http200() if obj.liker_records.filter(
            liker=request.user).exists() else Http400()

    @require_token
    def post(self, request, obj):
        """
        对某个对象点赞

        """
        if obj.liker_records.filter(liker=request.user).exists():
            return Http403('already liked the object')

        obj.liker_records.create(liker=obj)
        return Http200()

    @require_token
    def delete(self, request, obj):
        """
        对某个对象取消点赞

        """
        if not obj.liker_records.filter(liker=request.user).exists():
            return Http403('not liked the object')

        obj.liker_records.filter(liker=request.user).delete()
        return Http200()


# noinspection PyMethodOverriding
class LikedUser(LikedObject):
    @check_object_id(User.enabled, 'user')
    def get(self, request, user):
        return super(LikedUser, self).get(request, user)

    @check_object_id(User.enabled, 'user')
    def post(self, request, user):
        return super(LikedUser, self).post(request, user)

    @check_object_id(User.enabled, 'user')
    def delete(self, request, user):
        return super(LikedUser, self).delete(request, user)


# noinspection PyMethodOverriding
class LikedTeam(LikedObject):
    @check_object_id(Team.enabled, 'team')
    def get(self, request, team):
        return super(LikedTeam, self).get(request, team)

    @check_object_id(Team.enabled, 'team')
    def post(self, request, team):
        return super(LikedTeam, self).post(request, team)

    @check_object_id(Team.enabled, 'team')
    def delete(self, request, team):
        return super(LikedTeam, self).delete(request, team)
