import json

from django import forms
from django.http import JsonResponse
from django.views.generic import View

from main.models import User
from main.utils import abort
from main.utils.decorators import require_verification_token
from main.utils.http import notify_user
from util.decorator.auth import app_auth
from util.decorator.param import validate_args, fetch_object


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
        return JsonResponse({'count': c, 'list': l, 'code': 0})

    # post_dict = {'description': forms.CharField(required=False, max_length=100)}
    @require_verification_token
    @validate_args({
        'user_id': forms.IntegerField(),
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
