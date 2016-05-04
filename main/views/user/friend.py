from django import forms
from django.db import transaction
from django.db.models import Q
from django.http import JsonResponse
from django.views.generic import View

from main.decorators import check_object_id, require_token, validate_input
from main.models import User, UserFriendRelation, UserFriendRequest
from main.responses import *


# todo: test
class Friends(View):
    get_dict = {
        'offset': forms.IntegerField(required=False, min_value=0),
        'limit': forms.IntegerField(required=False, min_value=0),
        'order': forms.IntegerField(required=False, min_value=0, max_value=3),
    }
    available_orders = [
        'create_time', '-create_time',
        'friend__profile__name', '-friend__profile__name',
    ]

    @check_object_id(User.enabled, 'user')
    @require_token
    @validate_input(get_dict)
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
                name: 用户昵称
                icon_url: 用户头像URL
                create_time: 成为好友时间
        """
        if not user:
            user = request.user

        i, j, k = offset, offset + limit, self.available_orders[order]
        c = user.friend_relations.count()
        qs = user.friend_relations.order_by(k)[i:j]
        l = [{'id': r.friend.id,
              'username': r.friend.username,
              'name': r.friend.profile.name,
              'icon_url': r.friend.profile.icon.url
              if r.friend.profile.icon else None,
              'create_time': r.create_time} for r in qs]
        return JsonResponse({'count': c, 'list': l})


# todo: test
class Friend(View):
    @check_object_id(User.enabled, 'user')
    @check_object_id(User.enabled, 'other_user')
    @require_token
    def get(self, request, other_user, user=None):
        """
        检查两个用户是否为好友关系

        :return:  200 | 404

        """
        if not user:
            user = request.user

        return Http200() if UserFriendRelation.exist(user, other_user) \
            else Http404()


# todo: test
class FriendSelf(Friend):
    @check_object_id(User.enabled, 'user')
    @require_token
    def post(self, request, user):
        """
        将目标用户添加为自己的好友（对方需发送过好友请求）

        """
        if not UserFriendRequest.exist(user, request.user):
            return Http403('related friend request not exists')

        # 若双方已是好友则不做处理
        if UserFriendRelation.exist(request.user, user):
            return Http403('already been friends')

        # 在事务中建立双向关系，并删除对应的好友请求
        with transaction.atomic():
            request.user.friend_requests.get(sender=user).delete()
            request.user.friend_relations.create(friend=user)
            user.friend_relations.create(friend=request.user)
        return Http200()

    @check_object_id(User.enabled, 'user')
    @require_token
    def delete(self, request, user):
        """
        删除好友

        """
        if not UserFriendRelation.exist(request.user, user):
            return Http404('not user\'s friend')

        # 删除双向好友关系
        qs = UserFriendRelation.enabled.filter(
            Q(user=request.user, friend=user) |
            Q(user=user, friend=request.user))
        qs.delete()
        return Http200()


# todo: test
class FriendRequests(View):
    get_dict = {'limit': forms.IntegerField(required=False, min_value=10)}

    @check_object_id(User.enabled, 'user')
    @require_token
    @validate_input(get_dict)
    def get(self, request, user=None, limit=10):
        """
        * 当user为当前用户时，按请求时间逆序获取当前用户收到的的好友请求信息，
          拉取后的请求 标记为已读
        * 当user为其他用户时，检查当前用户是否对某个用户已经发送过
          好友请求，并且该请求未被处理（接收或忽略）

        :param limit: 拉取的数量上限
        :return: user == request.user 时，200 | 404
        :return: user != request.user 时
            count: 剩余未拉取（未读）的请求条数
            list: 好友请求信息列表
                id: 用户ID
                username: 用户名
                name: 用户昵称
                icon_url: 用户头像URL
                description: 附带消息
                create_time: 请求发出的时间
        """
        if not user or user.id == request.user.id:
            # 拉取好友请求信息
            qs = request.user.friend_requests.filter(is_read=False)[:limit]
            qs.update(is_read=True)
            l = [{'id': r.sender.id,
                  'username': r.sender.username,
                  'name': r.sender.profile.name,
                  'icon_url': r.sender.profile.icon.url
                  if r.sender.profile.icon else None,
                  'description': r.description,
                  'create_time': r.create_time} for r in qs]
            c = request.user.friend_requests.filter(is_read=False).count()
            return JsonResponse({'count': c, 'list': l})
        else:
            # 判断是否对目标用户发送过好友请求，且暂未被对方处理
            return Http200() if UserFriendRequest.exist(request.user, user) \
                else Http404()

    post_dict = {'description': forms.CharField(required=False, max_length=100)}

    @check_object_id(User.enabled, 'user')
    @require_token
    @validate_input(post_dict)
    def post(self, request, user, description=''):
        """
        向目标用户发出好友申请，若已发出申请且未被处理则返回403，否则返回200

        :param description: 附带消息

        """
        if user == request.user:
            return Http400('cannot send friend request to self')

        if UserFriendRelation.exist(request.user, user):
            return Http403('already been friends')

        if UserFriendRequest.exist(request.user, user):
            return Http403('already sent a friend request')

        req = user.friend_requests.model(
            sender=request.user, receiver=user, description=description)
        req.save()
        return Http200()


# todo: test
class FriendRequest(View):
    @check_object_id(User.enabled, 'user')
    @require_token
    def delete(self, request, user):
        """
        忽略某条好友请求

        """
        if not UserFriendRequest.exist(user, request.user):
            return Http403('related friend request not exists')

        request.user.friend_requests.get(sender=user).delete()
