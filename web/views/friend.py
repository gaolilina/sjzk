import json

from django import forms

from main.models import User
from main.utils.http import notify_user
from util.base.view import BaseView
from util.decorator.auth import client_auth
from util.decorator.param import validate_args, fetch_object


class FriendRequestList(BaseView):

    @client_auth
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
            return self.fail(1, '不能给自己发送好友申请')

        if user.friends.filter(other_user=request.user).exists():
            return self.fail(2, '已经是好友了')

        if user.friend_requests.filter(other_user=request.user).exists():
            return self.success()

        user.friend_requests.create(other_user=request.user, description=description)

        notify_user(user, json.dumps({
            'type': 'friend_request'
        }))
        return self.success()
