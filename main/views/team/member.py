from django import forms
from django.db import transaction
from django.http import JsonResponse
from django.views.generic import View

from main.decorators import require_token, check_object_id, validate_input
from main.models.user import User
from main.models.team import Team
from main.models.team.member import TeamMember, TeamMemberRequest,\
    TeamInvitation
from main.responses import *


class Members(View):
    get_dict = {
        'offset': forms.IntegerField(required=False, min_value=0),
        'limit': forms.IntegerField(required=False, min_value=0),
        'order': forms.IntegerField(required=False, min_value=0, max_value=3),
    }
    available_orders = (
        'create_time', '-create_time',
        'member__name', '-member__name',
    )

    @check_object_id(Team.enabled, 'team')
    @require_token
    @validate_input(get_dict)
    def get(self, request, team, offset=0, limit=10, order=1):
        """
        获取团队的成员列表

        :param team_id: 团队ID
        :param offset: 偏移量
        :param limit: 数量上限
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
                name: 用户昵称
                icon_url: 用户头像URL
                create_time: 成为团队成员时间
        """

        i, j, k = offset, offset + limit, self.available_orders[order]
        c = TeamMember.enabled.filter(team=team).count()
        rs = TeamMember.enabled.filter(team=team).order_by(k)[i:j]
        l = [{'id': r.member.id,
              'username': r.member.username,
              'name': r.member.name,
              'icon_url': r.member.icon_url,
              'create_time': r.create_time} for r in rs]
        return JsonResponse({'count': c, 'list': l})


class Member(View):
    get_dict = {'user_id': forms.IntegerField(required=False)}

    @check_object_id(Team.enabled, 'team')
    @validate_input(get_dict)
    @require_token
    def get(self, request, team, user_id=None):
        """
        检查用户是否为团队成员

        :param team_id 团队ID
        :param user_id 用户ID（默认为当前用户）
        """
        if user_id:
            try:
                user = User.enabled.get(id=user_id)
            except ValueError:
                return Http404('user is not enabled')
        else:
            user = request.user

        return Http200() if TeamMember.exist(user, team) else Http404()


class MemberSelf(Member):
    @check_object_id(Team.enabled, 'team')
    @check_object_id(User.enabled, 'user')
    @require_token
    def post(self, request, team, user):
        """
        将目标用户添加为自己的团队成员（对方需发送过加入团队申请）

        """
        if request.user != team.owner:
            return Http403('recent user has no authority')

        if not TeamMemberRequest.exist(user, team):
            return Http403('related member request not exists')

        # 若对方已是团队成员则不做处理
        if TeamMember.exist(user, team):
            return Http403('already been member')

        # 在事务中建立关系，并删除对应的加团队申请
        with transaction.atomic():
            team.member_requests.get(sender=user).delete()
            team.member_records.create(member=user)
        return Http200()

    @check_object_id(Team.enabled, 'team')
    @check_object_id(User.enabled, 'user')
    @require_token
    def delete(self, request, team, user):
        """
        删除成员

        :param team_id: 团队ID
        :param user_id: 用户ID
        """
        user = user or request.user

        if not TeamMember.exist(user, team):
            return Http404('not team\'s member')

        # 删除团队成员关系
        tm = TeamMember.enabled.filter(team=team, member=user)
        tm.delete()
        return Http200()


class MemberRequests(View):
    get_dict = {'limit': forms.IntegerField(required=False, min_value=10)}

    @check_object_id(Team.enabled, 'team')
    @require_token
    @validate_input(get_dict)
    def get(self, request, team, limit=10):
        """
        获取团队的加入申请列表
        * 若当前用户为团队创始人时，按请求时间逆序获取收到的加团队申请信息，
          拉取后的申请 标记为已读
        * 若不为团队创始人时，检查当前用户是否已经发送过加团队请求，
          并且该请求未被处理（接收或忽略）

        :param limit: 拉取的数量上限
        :return: request.user 为团队创始人时，200 | 404
        :return: request.user 不为团队创始人时
            count: 剩余未拉取（未读）的请求条数
            list: 加入团队请求信息列表
                id: 用户ID
                username: 用户名
                name: 用户昵称
                icon_url: 用户头像URL
                description: 附带消息
                create_time: 请求发出的时间
        """
        if request.user == team.owner:
            # 拉取团队的加入申请信息
            qs = TeamMemberRequest.enabled.filter(receiver=team, is_read=False)
            qs = qs[:limit]

            l = [{'id': r.sender.id,
                  'username': r.sender.username,
                  'name': r.sender.name,
                  'icon_url': r.sender.icon_url,
                  'description': r.description,
                  'create_time': r.create_time} for r in qs]
            # 更新拉取的加入团队信息为已读
            ids = qs.values('id')
            TeamMemberRequest.enabled.filter(receiver=team, id__in=ids).\
                update(is_read=True)
            c = TeamMemberRequest.enabled.filter(receiver=team, is_read=False).\
                count()
            return JsonResponse({'count': c, 'list': l})
        else:
            # 判断是否对团队创始人发送过加入团队请求，且暂未被处理
            return Http200() if TeamMemberRequest.exist(request.user, team) \
                else Http404()

    post_dict = {'description': forms.CharField(required=False, max_length=100)}

    @check_object_id(Team.enabled, 'team')
    @require_token
    @validate_input(post_dict)
    def post(self, request, team, description=''):
        """
        向团队发出加入申请，若已发出申请且未被处理则返回403，否则返回200

        :param team_id: 团队ID
        :param description: 附带消息

        """
        if request.user == team.owner:
            return Http400('cannot send member request to self')

        if TeamMember.exist(request.user, team):
            return Http403('already been member')

        if TeamMemberRequest.exist(request.user, team):
            return Http403('already sent a member request')

        if TeamInvitation.exist(team, request.user):
            return Http403('the team has already sent a invitation')

        req = team.member_requests.model(
            sender=request.user, receiver=team, description=description)
        req.save()
        return Http200()


class MemberRequest(View):
    @check_object_id(Team.enabled, 'team')
    @check_object_id(User.enabled, 'user')
    @require_token
    def delete(self, request, team, user):
        """
        忽略某用户的加团队请求

        :param team_id: 团队ID
        :param user_id: 用户ID
        """
        if request.user != team.owner:
            return Http403('recent user has no authority')

        if not TeamMemberRequest.exist(user, team):
            return Http403('related member request not exists')

        team.member_requests.get(sender=user).delete()
        return Http200()


class Invitations(View):
    get_dict = {'limit': forms.IntegerField(required=False, min_value=10)}

    @require_token
    @validate_input(get_dict)
    def get(self, request, limit=10):
        """
        获取用户的加入团队邀请列表
        * 按邀请时间逆序获取收到的加团队邀请信息，拉取后的邀请 标记为已读

        :param limit: 拉取的数量上限
        :return:
            count: 剩余未拉取（未读）的邀请条数
            list: 加入团队邀请信息列表
                id: 团队ID
                name: 团队名称
                icon_url: 团队头像URL
                description: 附带消息
                create_time: 邀请发出的时间
        """
        # 拉取团队的加入申请信息
        qs = TeamInvitation.enabled.filter(receiver=request.user, is_read=False)
        qs = qs[:limit]

        l = [{'id': r.sender.id,
              'name': r.sender.name,
              'icon_url': r.sender.icon_url,
              'description': r.description,
              'create_time': r.create_time} for r in qs]
        # 更新拉取的加入团队邀请信息为已读
        ids = qs.values('id')
        TeamInvitation.enabled.filter(
                receiver=request.user, id__in=ids).update(is_read=True)
        c = TeamInvitation.enabled.filter(
                receiver=request.user, is_read=False).count()
        return JsonResponse({'count': c, 'list': l})


class Invitation(View):
    post_dict = {'description': forms.CharField(required=False, max_length=100)}

    @check_object_id(Team.enabled, 'team')
    @check_object_id(User.enabled, 'user')
    @require_token
    @validate_input(post_dict)
    def post(self, request, team, user, description=''):
        """
        向用户发出加入团队邀请，若已发出申请且未被处理则返回403，否则返回200

        :param team_id: 团队ID
        :param user_id: 用户ID
        :param description: 附带消息

        """
        if request.user != team.owner:
            return Http403('recent user has no authority')

        if user == team.owner:
            return Http400('cannot send invitation to self')

        if TeamMember.exist(user, team):
            return Http403('already been member')

        if TeamInvitation.exist(team, user):
            return Http403('already sent a invitation')

        if TeamMemberRequest.exist(user, team):
            return Http403('the user has already sent a member request')

        invitation = team.invitations.model(
                sender=team, receiver=user, description=description)
        invitation.save()
        return Http200()


class InvitationSelf(View):
    @check_object_id(Team.enabled, 'team')
    @require_token
    def post(self, request, team):
        """
        同意团队的加入邀请并成为团队成员（需收到过加入团队邀请）

        """
        if not TeamInvitation.exist(team, request.user):
            return Http403('related invitation not exists')

        # 若已是团队成员则不做处理
        if TeamMember.exist(request.user, team):
            return Http403('already been member')

        # 在事务中建立关系，并删除对应的加团队邀请
        with transaction.atomic():
            team.invitations.get(sender=team).delete()
            team.member_records.create(member=request.user)
        return Http200()

    @check_object_id(Team.enabled, 'team')
    @require_token
    def delete(self, request, team):
        """
        忽略某团队的加团队邀请

        :param team_id: 团队ID
        """
        if not TeamInvitation.exist(team, request.user):
            return Http403('related team invitation not exists')

        request.user.invitations.get(sender=team).delete()
        return Http200()
