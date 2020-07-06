from django import forms
from django.http import JsonResponse
from django.views.generic import View

from main.models import Competition, Team, CompetitionTeamParticipator
from main.utils import abort
from main.utils.decorators import require_verification_token
from util.decorator.auth import app_auth
from util.decorator.param import fetch_object, validate_args


class TeamParticipatorList(View):
    ORDERS = ('time_created', '-time_created', 'name', '-name', '-score')

    @fetch_object(Competition.enabled, 'competition')
    @app_auth
    @validate_args({
        'offset': forms.IntegerField(required=False, min_value=0),
        'limit': forms.IntegerField(required=False, min_value=0),
        'order': forms.IntegerField(required=False, min_value=0, max_value=3),
        'final': forms.BooleanField(required=False),
    })
    def get(self, request, competition, offset=0, limit=10, order=1, final=True):
        """获取报名团队列表"""

        k = self.ORDERS[order]
        c = competition.team_participators.filter(final=final).count()
        qs = competition.team_participators.filter(final=final).all().order_by(
            k)[offset: offset + limit]
        l = [{'id': p.team.id,
              'name': p.team.name,
              'icon_url': p.team.icon,
              'score': p.score,
              'participator_id': p.id,
              'final': p.final} for p in qs]
        return JsonResponse({'count': c, 'list': l})

    @require_verification_token
    @validate_args({
        'team_id': forms.IntegerField(),
        'competition_id': forms.IntegerField(),
    })
    @fetch_object(Competition.enabled, 'competition')
    @fetch_object(Team.enabled, 'team')
    def post(self, request, competition, team, **kwargs):
        """报名"""

        if competition.status != 1:
            abort(403, '非报名阶段')
        c = competition.team_participators.count()
        if competition.allow_team != 0 and c >= competition.allow_team:
            abort(403, '参赛者已满')
        if team.owner != request.user:
            abort(403, '只有队长才能报名')
        if CompetitionTeamParticipator.objects.filter(team__owner=request.user, final=True).exists():
            abort(403, '队长只能带领一支队伍参赛')
        for m in team.members.all():
            if m.user.is_verified not in [2, 4]:
                abort(403, '团队成员未实名认证')
            if competition.user_type != 0:
                if competition.user_type == 1 and m.user.role != "学生":
                    abort(403, '团队成员角色不符')
                elif competition.user_type == 2 and m.user.role != "教师":
                    abort(403, '团队成员角色不符')
                elif competition.user_type == 3 and m.user.role == "":
                    abort(403, '团队成员角色不符')
        if not competition.team_participators.filter(team=team).exists():
            competition.team_participators.create(team=team)
        abort(200)
