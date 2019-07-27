#!usr/bin/env python3
# -*- coding:utf-8 _*-
# noinspection PyClassHasNoInit
from django import forms
from django.http import JsonResponse
from django.views.generic.base import View

from main.models import User
from main.utils import *
from main.utils.decorators import *
from main.utils.http import *
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


# noinspection PyClassHasNoInit
class FriendRequestList(View):
    """
    好友请求和列表
    """

    @app_auth
    @validate_args({
        'offset': forms.IntegerField(required=False),
        'limit': forms.IntegerField(required=False, min_value=0),
    })
    def get(self, request, offset=0, limit=10):
        """按请求时间逆序获取当前用户收到的的好友请求信息，
        拉取后的请求标记为已读

        :return:
            count: 请求的总条数
            list: 好友请求信息列表
                id: 用户ID
                username: 用户名
                request_id: 申请ID
                name: 用户昵称
                icon_url: 用户头像
                description: 附带消息
                time_created: 请求发出的时间
        """
        # 拉取好友请求信息
        c = request.user.friend_requests.count()
        qs = request.user.friend_requests.all()[offset:offset + limit]

        l = [{'id': r.other_user.id,
              'request_id': r.id,
              'username': r.other_user.username,
              'name': r.other_user.name,
              'icon_url': r.other_user.icon,
              'description': r.description,
              'time_created': r.time_created} for r in qs]
        return JsonResponse({'count': c, 'list': l})

    # post_dict = {'description': forms.CharField(required=False, max_length=100)}
    @require_verification_token
    @validate_args({
        'description': forms.CharField(required=False, max_length=100)
    })
    @fetch_object(User.enabled, 'user')
    def post(self, request, user, description=''):
        """向目标用户发出好友申请

        :param description: 附带消息
        """
        if user == request.user:
            abort(403, '不能给自己发送好友申请')

        if user.friends.filter(other_user=request.user).exists():
            abort(403, '已经是好友了')

        if user.friend_requests.filter(other_user=request.user).exists():
            abort(200)

        user.friend_requests.create(other_user=request.user,
                                    description=description)

        notify_user(user, json.dumps({
            'type': 'friend_request'
        }))
        abort(200)


class FriendRequestAction(View):
    """
    处理好友请求
    """

    @require_verification_token
    def delete(self, request, req_id):
        """忽略某条好友请求"""

        request.user.friend_requests.filter(pk=req_id).delete()
        abort(200)


class FriendList(View):
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
    @fetch_object(User.enabled, 'user')
    def get(self, request, user=None, offset=0, limit=10, order=1):
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
        user = user or request.user

        c = user.friends.count()
        qs = user.friends.order_by(self.ORDERS[order])[offset:offset + limit]
        l = [{'id': r.other_user.id,
              'username': r.other_user.username,
              'name': r.other_user.real_name if r.other_user.is_verified == 2 else r.other_user.name,
              'icon_url': r.other_user.icon,
              'time_created': r.time_created} for r in qs]
        return JsonResponse({'count': c, 'list': l})
