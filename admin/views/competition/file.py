from django import forms
from django.http import HttpResponse
from django.template import loader, Context
from django.views.generic import View

from admin.utils.decorators import fetch_record, require_role
from main.models import Competition, CompetitionTeamParticipator, CompetitionFile, Team, User
from main.utils import abort
from util.decorator.auth import admin_auth
from util.decorator.param import fetch_object, validate_args


class AdminCompetitionFilesView(View):
    @fetch_record(Competition.enabled, 'model', 'id')
    @admin_auth
    @require_role('axyz')
    def get(self, request, model, status):
        # if len(CompetitionOwner.objects.filter(competition=model, user=request.user)) == 0:
        #    return HttpResponseForbidden()

        template = loader.get_template("admin_competition/file.html")
        context = Context({'model': model, 'user': request.user,
                           'files': [{
                               'team': file.team,
                               'file': file.file,
                               'id': file.id,
                               'time_created': file.time_created,
                               'participator': CompetitionTeamParticipator.objects.filter(competition=model,
                                                                                          team=file.team).get(),
                               'type': file.type,
                               'score': file.score,
                               'comment': file.comment,
                           } for file in CompetitionFile.objects.filter(competition=model, status=status)],
                           'teams': CompetitionTeamParticipator.objects.filter(competition=model, final=True).all()})
        return HttpResponse(template.render(context))


class AdminCompetitionExcelView(View):
    @fetch_record(Competition.enabled, 'model', 'id')
    @admin_auth
    @require_role('axyz')
    def get(self, request, model):
        # if len(CompetitionOwner.objects.filter(competition=model, user=request.user)) == 0:
        #    return HttpResponseForbidden()

        template = loader.get_template("admin_competition/excel.html")
        context = Context({'model': model})
        return HttpResponse(template.render(context),
                            content_type="text/csv")


class CompetitionFileExpert(View):
    @fetch_object(Competition.enabled, 'competition')
    @fetch_object(Team.enabled, 'team')
    @admin_auth
    @validate_args({
        'expert_id': forms.IntegerField(),
    })
    def post(self, request, competition, team, expert_id):
        expert = User.objects.filter(pk=expert_id).get()
        CompetitionTeamParticipator.objects.filter(
            competition=competition,
            team=team,
        ).update(rater=expert)
        abort(200)