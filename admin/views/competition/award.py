import json

from django import forms
from django.http import HttpResponse
from django.template import loader, Context
from django.views.generic import View

from admin.utils.decorators import fetch_record, require_role
from main.models import Competition, Team, CompetitionStage
from util.decorator.auth import admin_auth
from util.decorator.param import old_validate_args
from util.decorator.permission import admin_permission


class AdminCompetitionAwardEdit(View):
    @fetch_record(Competition.enabled, 'model', 'id')
    @admin_auth
    @require_role('axyz')
    def get(self, request, model):
        # if len(CompetitionOwner.objects.filter(competition=model, user=request.user)) == 0:
        #    return HttpResponseForbidden()

        template = loader.get_template("admin_competition/award.html")
        context = Context({'model': model, 'user': request.user})
        return HttpResponse(template.render(context))

    @admin_auth
    @admin_permission('award_team_in_competition')
    @old_validate_args({
        'awards': forms.CharField(),
    })
    @fetch_record(Competition.enabled, 'model', 'id')
    def post(self, request, model, **kwargs):
        awards = json.loads(kwargs['awards'])
        for a in awards:
            for id in awards[a]:
                model.awards.create(award=a, team=Team.objects.filter(id=int(id))[0])
        Competition.enabled.filter(id=model.id).update(status=CompetitionStage.STAGE_END)
        template = loader.get_template("admin_competition/award.html")
        context = Context({'model': model, 'msg': '保存成功，竞赛已自动设为结束状态', 'user': request.user})
        return HttpResponse(template.render(context))
