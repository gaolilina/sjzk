from django import forms
from django.http import JsonResponse
from django.views import View

from ..models import Activity, Team
from ..utils import abort
from ..utils.decorators import *


__all__ = ['List', 'Detail', 'UserParticipatorList', 'TeamParticipatorList']


class List(View):
    @require_token
    @validate_args({'offset': forms.IntegerField(required=False, min_value=0)})
    def get(self, request, offset=0, limit=10):
        """获取活动列表"""

        c = Activity.enabled.count()
        qs = Activity.enabled.all()[offset: offset + limit]
        l = [{'id': a.id,
              'name': a.name,
              'time_started': a.time_started,
              'time_ended': a.time_ended,
              'deadline': a.deadline,
              'user_participator_count': a.user_participators.count(),
              'team_participator_count': a.team_participators.count(),
              'time_created': a.time_created} for a in qs]
        return JsonResponse({'count': c, 'list': l})


class Detail(View):
    @fetch_object(Activity, 'activity')
    @require_token
    def get(self, request, activity):
        """获取活动详情"""

        return JsonResponse({
            'id': activity.id,
            'name': activity.name,
            'content': activity.content,
            'time_started': activity.time_started,
            'time_ended': activity.time_ended,
            'deadline': activity.deadline,
            'allow_user': activity.allow_user,
            'allow_team': activity.allow_team,
            'user_participator_count': activity.user_participators.count(),
            'team_participator_count': activity.team_participators.count(),
            'time_created': activity.time_created,
        })


class UserParticipatorList(View):
    @fetch_object(Activity, 'activity')
    @require_token
    @validate_args({'offset': forms.IntegerField(required=False, min_value=0)})
    def get(self, request, activity, offset=0, limit=10):
        """获取报名用户列表"""

        c = activity.user_participators.count()
        qs = activity.user_participators.all()[offset: offset + limit]
        l = [{'id': p.user.id,
              'name': p.user.name,
              'username': p.user.username} for p in qs]
        return JsonResponse({'count': c, 'list': l})

    @fetch_object(Activity, 'activity')
    @require_token
    def post(self, request, activity):
        """报名"""

        if not activity.allow_user:
            abort(403)

        if not activity.user_participators.filter(user=request.user).exists():
            activity.user_participators.create(user=request.user)
        abort(200)


class TeamParticipatorList(View):
    @fetch_object(Activity, 'activity')
    @require_token
    @validate_args({'offset': forms.IntegerField(required=False, min_value=0)})
    def get(self, request, activity, offset=0, limit=10):
        """获取报名团队列表"""

        c = activity.team_participators.count()
        qs = activity.team_participators.all()[offset: offset + limit]
        l = [{'id': p.team.id,
              'name': p.team.name} for p in qs]
        return JsonResponse({'count': c, 'list': l})

    @fetch_object(Activity, 'activity')
    @validate_args({'team_id': forms.IntegerField()})
    @require_token
    def post(self, request, activity, team_id):
        """报名"""

        if not activity.allow_team:
            abort(403)

        try:
            team = Team.enabled.get(id=team_id)
        except Team.DoesNotExist:
            abort(400)
        else:
            if not activity.team_participators.filter(team=team).exists():
                activity.team_participators.create(team=team)
            abort(200)
