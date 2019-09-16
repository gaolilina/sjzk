from django import forms
from django.db import transaction
from django.http import JsonResponse
from django.views.generic import View

from main.models import action, TeamInvitation
from main.utils import abort, get_score_stage
from main.utils.decorators import require_verification_token
from util.decorator.auth import app_auth
from util.decorator.param import validate_args, fetch_object


class InvitationList(View):
    @app_auth
    @validate_args({
        'offset': forms.IntegerField(required=False),
        'limit': forms.IntegerField(required=False, min_value=0),
    })
    def get(self, request, offset=0, limit=10):
        """获取当前用户的团队邀请列表

        :param limit: 拉取的数量上限
        :return:
            count: 邀请的总条数
            list:
                id: 团队ID
                name: 团队名称
                icon_url: 团队头像
                description: 附带消息
                time_created: 邀请发出的时间
        """
        # 拉取来自团队的邀请信息
        c = TeamInvitation.objects.filter(user=request.user).count()
        qs = TeamInvitation.objects.filter(
            user=request.user)[offset:offset + limit]

        l = [{'id': r.team.id,
              'invitation_id': r.id,
              'name': r.team.name,
              'icon_url': r.team.icon,
              'description': r.description,
              'time_created': r.time_created} for r in qs]
        return JsonResponse({'count': c, 'list': l})


class Invitation(View):

    @fetch_object(TeamInvitation.objects, 'invitation')
    @require_verification_token
    def post(self, request, invitation):
        """同意团队的加入邀请并成为团队成员（需收到过加入团队邀请）"""

        if invitation.user != request.user:
            abort(403, '未收到过邀请')

        # 若已是团队成员则不做处理
        if invitation.team.members.filter(user=request.user).exists():
            invitation.delete()
            abort(200)

        # 在事务中建立关系，并删除对应的加团队邀请
        with transaction.atomic():
            invitation.team.members.create(user=request.user)
            # 发布用户加入团队动态
            action.join_team(request.user, invitation.team)
            invitation.delete()
            request.user.score += get_score_stage(1)
            request.user.score_records.create(
                score=get_score_stage(1), type="能力",
                description="成功加入一个团队")
            invitation.team.score += get_score_stage(1)
            invitation.team.score_records.create(
                score=get_score_stage(1), type="能力",
                description="成功招募队员")
            request.user.save()
            invitation.team.save()
        abort(200)

    @fetch_object(TeamInvitation.objects, 'invitation')
    @require_verification_token
    def delete(self, request, invitation):
        """忽略某邀请"""

        if invitation.user != request.user:
            abort(403, '未收到过邀请')

        invitation.delete()
        abort(200)
