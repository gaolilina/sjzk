from django import forms

from main.models import CompetitionFile, CompetitionTeamParticipator
from util.base.view import BaseView
from util.decorator.auth import client_auth
from util.decorator.param import validate_args, fetch_object


class FileScore(BaseView):
    @client_auth
    @validate_args({
        'file_id': forms.IntegerField(min_value=0),
        'score': forms.IntegerField(min_value=0),
    })
    @fetch_object(CompetitionFile.objects, 'file')
    def post(self, request, file, score, **kwargs):
        part = CompetitionTeamParticipator.objects.filter(team=file.team, competition=file.competition).first()
        if part is None or part.rater != request.user:
            return self.fail(1, '您不是评委')
        CompetitionFile.objects.filter(id=file.id).update(score=score)
        return self.success()


class FinalTeamScore(BaseView):
    @validate_args({
        'part_id': forms.IntegerField(),
        'score': forms.IntegerField(),
    })
    @fetch_object(CompetitionTeamParticipator.objects, 'part')
    def post(self, request, part, score, **kwargs):
        pass
