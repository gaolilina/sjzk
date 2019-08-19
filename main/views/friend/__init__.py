#!usr/bin/env python3
# -*- coding:utf-8 _*-
# noinspection PyClassHasNoInit
from django import forms
from django.http import JsonResponse
from django.views.generic.base import View

from main.models import User
from main.utils import *
from main.utils.decorators import *
from util.decorator.auth import app_auth
from util.decorator.param import fetch_object, validate_args


class FriendCheck(View):
    @app_auth
    @fetch_object(User.enabled, 'user')
    @fetch_object(User.enabled, 'other_user')
    def get(self, request, other_user, user=None):
        """检查两个用户是否为好友关系"""

        user = user or request.user

        if user.friends.filter(other_user=other_user).exists():
            abort(200)
        abort(404, '非好友关系')


class FriendAction(FriendCheck):
    """
    对好友进行操作，加好友，删除好友
    """

    @require_verification_token
    @fetch_object(User.enabled, 'other_user')
    def post(self, request, other_user):
        """将目标用户添加为自己的好友（对方需发送过好友请求）"""

        if not request.user.friend_requests.filter(other_user=other_user) \
                .exists():
            abort(403, '对方未发送过申请')

        if request.user.friends.filter(other_user=other_user).exists():
            abort(403, '已经是好友')

        request.user.friends.create(other_user=other_user)
        other_user.friends.create(other_user=request.user)
        request.user.friend_requests.filter(other_user=other_user).delete()
        # 积分相关
        request.user.score += get_score_stage(1)
        request.user.score_records.create(
            score=get_score_stage(1), type="受欢迎度", description="添加一个好友")
        other_user.score += get_score_stage(1)
        other_user.score_records.create(
            score=get_score_stage(1), type="受欢迎度", description="添加一个好友")
        request.user.save()
        other_user.save()
        abort(200)

    @fetch_object(User.enabled, 'other_user')
    @require_verification_token
    def delete(self, request, other_user):
        """删除好友"""

        if not request.user.friends.filter(other_user=other_user).exists():
            abort(404, '好友不存在')

        from ..models import UserFriend
        UserFriend.objects.filter(user=request.user, other_user=other_user) \
            .delete()
        UserFriend.objects.filter(user=other_user, other_user=request.user) \
            .delete()
        # 积分相关
        request.user.score -= get_score_stage(1)
        request.user.score_records.create(
            score=-get_score_stage(1), type="受欢迎度", description="删除一个好友")
        other_user.score -= get_score_stage(1)
        other_user.score_records.create(
            score=-get_score_stage(1), type="受欢迎度", description="删除一个好友")
        request.user.save()
        other_user.save()
        abort(200)


class MyFriendList(View):
    ORDERS = (
        'time_created', '-time_created',
        'friend__name', '-friend__name',
    )

    @app_auth
    @validate_args({
        'offset': forms.IntegerField(required=False, min_value=0),
        'limit': forms.IntegerField(required=False, min_value=0),
        'order': forms.IntegerField(required=False, min_value=0, max_value=3),
    })
    def get(self, request, offset=0, limit=10, order=1):
        """
        获取用户的好友列表

        :param offset: 偏移量
        :param limit: 数量上限
        :param order: 排序方式
            0: 成为好友时间升序
            1: 成为好友时间降序（默认值）
            2: 昵称升序
            3: 昵称降序
        :return:
            count: 好友总数
            list: 好友列表
                id: 用户ID
                username: 用户名
                name: 用户名称，实名认证的要使用真实姓名，否则使用昵称
                icon_url: 用户头像
                time_created: 成为好友时间
        """
        user = request.user

        c = user.friends.count()
        qs = user.friends.order_by(self.ORDERS[order])[offset:offset + limit]
        l = [{'id': r.other_user.id,
              'username': r.other_user.username,
              'name': r.other_user.real_name if r.other_user.is_verified == 2 else r.other_user.name,
              'icon_url': r.other_user.icon,
              'time_created': r.time_created} for r in qs]
        return JsonResponse({'count': c, 'list': l})
