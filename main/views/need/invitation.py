from django import forms
from django.db import transaction
from django.http import JsonResponse
from django.views.generic import View

from main.models import Team
from main.models.need import TeamNeed
from main.utils import abort, action, get_score_stage
from main.utils.decorators import require_verification_token
from util.decorator.auth import app_auth
from util.decorator.param import fetch_object, validate_args


class NeedInvitationList(View):
    @fetch_object(TeamNeed.objects, 'need')
    @fetch_object(Team.enabled, 'team')
    @app_auth
    @validate_args({
        'offset': forms.IntegerField(required=False, min_value=0),
        'limit': forms.IntegerField(required=False, min_value=0),
    })
    def get(self, request, need, team, offset=0, limit=10):
        """获取需求的合作邀请列表

        :param offset: 偏移量
        :return: request.user 不为团队创始人时，404
        :return: request.user 为团队创始人时
            count: 邀请总数
            list: 邀请列表
                team_id: 被邀请团队ID
                name: 被邀请团队名称
                icon_url: 被邀请团队头像
                time_created: 邀请时间
        """
        if request.user == need.team.owner and need.team == team:
            # 拉取邀请合作信息
            c = need.cooperation_invitations.count()
            qs = need.cooperation_invitations.all()[offset:offset + limit]

            l = [{'team_id': r.invitee.id,
                  'name': r.invitee.name,
                  'icon_url': r.invitee.icon,
                  'time_created': r.time_created} for r in qs]
            return JsonResponse({'count': c, 'list': l})
        abort(404, '只有队长可以操作')

    @fetch_object(TeamNeed.objects, 'need')
    @fetch_object(Team.enabled, 'team')
    @require_verification_token
    def post(self, request, need, team):
        """向团队发出合作邀请

        """
        if need.cooperation_invitations.filter(invitee=team).exists():
            abort(404, '已经发送过合作申请')
        if need.cooperation_requests.filter(sender=team).exists():
            abort(404, '对方已经发送过合作申请')
        if request.user == team.owner:
            need.cooperation_invitations.create(invitee=team)
            abort(200)
        abort(404, '只有队长可以操作')


class TeamInvitationList(View):
    @fetch_object(Team.enabled, 'team')
    @app_auth
    @validate_args({
        'offset': forms.IntegerField(required=False, min_value=0),
        'limit': forms.IntegerField(required=False, min_value=0),
    })
    def get(self, request, team, offset=0, limit=10):
        """获取当前团队的受邀列表

        :param offset: 偏移量
        :return: request.user 不为团队创始人时，404
        :return: request.user 为团队创始人时
            count: 邀请总数
            list: 邀请列表
                team_id: 邀请方团队ID
                need_id: 邀请方需求ID
                title: 邀请方需求标题
                name: 邀请方团队名称
                icon_url: 邀请方团队头像
                time_created: 邀请时间
        """
        if request.user == team.owner:
            # 拉取邀请合作信息
            c = team.cooperation_invitations.count()
            qs = team.cooperation_invitations.all()[offset:offset + limit]

            l = [{'team_id': r.inviter.id,
                  'need_id': r.need.id,
                  'title': r.need.title,
                  'name': r.inviter.name,
                  'icon_url': r.invitee.icon,
                  'time_created': r.time_created} for r in qs]
            return JsonResponse({'count': c, 'list': l})
        abort(404, '只有队长可以操作')


class NeedInvitation(View):

    @fetch_object(TeamNeed.objects, 'need')
    @fetch_object(Team.enabled, 'team')
    @require_verification_token
    def post(self, request, need, team):
        """同意邀请并将加入他人的团队（对方需发送过合作邀请）"""

        if request.user != need.team.owner:
            abort(404, '只有队长可以操作')

        if need.cooperation_invitations.filter(invitee=team).exists():
            # 在事务中建立关系，并删除对应的邀请合作
            with transaction.atomic():
                need.cooperation_invitations.filter(invitee=team).delete()
                if need.team.members.filter(user=team.owner).exists():
                    abort(200)
                # 保存需求的加入团队Id
                if len(need.members) > 0:
                    need.members = need.members + "|" + str(team.id)
                else:
                    need.members = str(team.id)
                need.save()
                need.team.members.create(user=team.owner)
                action.join_team(team.owner, need.team)
                request.user.score += get_score_stage(1)
                request.user.score_records.create(
                    score=get_score_stage(1), type="能力",
                    description="与其他团队合作")
                team.score += get_score_stage(1)
                team.score_records.create(
                    score=get_score_stage(1), type="能力",
                    description="与其他团队合作")
                request.user.save()
                team.save()
            abort(200)
        abort(404, '邀请合作不存在')

    @fetch_object(TeamNeed.objects, 'need')
    @fetch_object(Team.enabled, 'team')
    @require_verification_token
    def delete(self, request, need, team):
        """忽略某来自需求的合作邀请"""

        if request.user != team.owner:
            abort(403, '只有队长可以操作')

        qs = need.cooperation_invitations.filter(invitee=team)
        if not qs.exists():
            abort(404, '合作邀请不存在')
        qs.delete()
        abort(200)
