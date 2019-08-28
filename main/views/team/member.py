import json

from django import forms
from django.db import transaction
from django.http import JsonResponse
from django.views.generic import View

from main.models import Team, User
from main.utils import abort, action
from main.utils.decorators import require_verification_token
from main.utils.http import notify_user
from util.decorator.auth import app_auth
from util.decorator.param import fetch_object, validate_args


class MemberList(View):
    ORDERS = (
        'time_created',
        '-time_created',
        'user__name',
        '-user__name',
    )

    @fetch_object(Team.enabled, 'team')
    @app_auth
    @validate_args({
        'offset': forms.IntegerField(required=False, min_value=0),
        'limit': forms.IntegerField(required=False, min_value=0),
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
                icon_url: 头像
                name: 用户昵称
                time_created: 成为团队成员时间
        """

        i, j, k = offset, offset + limit, self.ORDERS[order]
        c = team.members.count()
        rs = team.members.order_by(k)[i:j]
        l = [{'id': r.user.id,
              'username': r.user.username,
              'icon_url': r.user.icon,
              'name': r.user.name,
              'time_created': r.time_created} for r in rs]
        return JsonResponse({'count': c, 'list': l})


class Member(View):
    @fetch_object(Team.enabled, 'team')
    @fetch_object(User.enabled, 'user')
    @app_auth
    def get(self, request, team, user):
        """检查用户是否为团队成员"""

        if team.members.filter(user=user).exists():
            abort(200)
        abort(404, '非团队成员')

    @fetch_object(Team.enabled, 'team')
    @fetch_object(User.enabled, 'user')
    @require_verification_token
    def post(self, request, team, user):
        """将目标用户添加为自己的团队成员（对方需发送过加入团队申请）"""

        if request.user != team.owner:
            abort(403, '只有队长能操作')

        if not team.member_requests.filter(user=user):
            abort(403, '该用户未发送过请求')

        # 若对方已是团队成员则不做处理
        if team.members.filter(user=user).exists():
            abort(200)

        # 在事务中建立关系，并删除对应的加团队申请
        with transaction.atomic():
            team.member_requests.filter(user=user).delete()
            team.members.create(user=user)
            action.join_team(user, team)
        abort(200)

    @fetch_object(Team.enabled, 'team')
    @fetch_object(User.enabled, 'user')
    @require_verification_token
    def delete(self, request, team, user):
        """退出团队(默认)/删除成员"""
        if user == team.owner:
            abort(403, "队长不能退出")

        qs = team.members.filter(user=user)
        if qs.exists():
            qs.delete()
            abort(200)
        abort(404, '成员不存在')


class MemberRequestList(View):
    @fetch_object(Team.enabled, 'team')
    @validate_args({
        'offset': forms.IntegerField(required=False),
        'limit': forms.IntegerField(required=False, min_value=0),
    })
    @app_auth
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
                icon_url: 用户头像
                description: 附带消息
                time_created: 请求发出的时间
        """
        if request.user == team.owner:
            # 拉取团队的加入申请信息
            c = team.member_requests.count()
            qs = team.member_requests.all()[offset:offset + limit]

            l = [{'id': r.user.id,
                  'username': r.user.username,
                  'name': r.user.name,
                  'icon_url': r.user.icon,
                  'description': r.description,
                  'time_created': r.time_created} for r in qs]
            return JsonResponse({'count': c, 'list': l})

    @fetch_object(Team.enabled, 'team')
    @require_verification_token
    @validate_args({
        'description': forms.CharField(required=False, max_length=100),
    })
    def post(self, request, team, description=''):
        """向团队发出加入申请

        :param description: 附带消息
        """
        if request.user == team.owner:
            abort(403, '队长不能申请')

        if team.members.filter(user=request.user).exists():
            abort(403, '已经发送过申请')

        if team.member_requests.filter(user=request.user).exists():
            abort(200)

        if team.invitations.filter(user=request.user).exists():
            abort(403, '团队已经发送过邀请')

        for need in team.needs.all():
            if need.member_requests.filter(sender=request.user).exists():
                abort(403, '已经发送过申请')

        team.member_requests.create(user=request.user, description=description)
        abort(200)


class MemberRequest(View):
    @fetch_object(Team.enabled, 'team')
    @fetch_object(User.enabled, 'user')
    @app_auth
    def delete(self, request, team, user):
        """忽略某用户的加团队请求"""

        if request.user != team.owner:
            abort(403, '只有队长可以操作')

        qs = team.member_requests.filter(user=user)
        if not qs.exists():
            abort(404, '申请不存在')
        qs.delete()
        abort(200)


class Invitation(View):
    @fetch_object(Team.enabled, 'team')
    @fetch_object(User.enabled, 'user')
    @require_verification_token
    @validate_args({
        'description': forms.CharField(required=False, max_length=100),
    })
    def post(self, request, team, user, description=''):
        """向用户发出加入团队邀请

        :param description: 附带消息
        """
        if request.user != team.owner:
            abort(403, '只有队长可以操作')

        if user == team.owner:
            abort(403, '对方是本团队队长')

        if team.members.filter(user=user).exists():
            abort(403, '对方已经是团队成员')

        if team.invitations.filter(user=user).exists():
            abort(200)

        if team.member_requests.filter(user=user).exists():
            abort(403, '对方已经发送过申请')

        for need in team.needs.all():
            if need.member_requests.filter(sender=request.user).exists():
                abort(403, '对方已经发送过申请')

        team.invitations.create(user=user, description=description)
        notify_user(user, json.dumps({
            'type': 'invitation'
        }))
        abort(200)
