from django import forms

from main.utils import abort, get_score_stage
from main.utils.dfa import check_bad_words
from main.views.user import ExperienceList as ExperienceList_
from util.decorator.auth import app_auth
from util.decorator.param import validate_args


class ExperienceList(ExperienceList_):
    @app_auth
    @validate_args({
        'description': forms.CharField(max_length=100),
        'unit': forms.CharField(max_length=20),
        'profession': forms.CharField(required=False, max_length=20),
        'degree': forms.CharField(required=False, max_length=20),
        'time_in': forms.DateField(required=False),
        'time_out': forms.DateField(required=False),
    })
    def post(self, request, type, **kwargs):
        """增加一条经历"""

        if check_bad_words(kwargs['description']):
            abort(403, '含有非法词汇')
        request.user.experiences.create(
            type=type, description=kwargs['description'], unit=kwargs['unit'],
            profession=kwargs['profession'], degree=kwargs['degree'],
            time_in=kwargs['time_in'], time_out=kwargs['time_out']
        )
        request.user.score += get_score_stage(3)
        request.user.score_records.create(
            score=get_score_stage(3), type="活跃度", description="增加一条经历")
        request.user.save()
        abort(200)

    @app_auth
    def delete(self, request, type):
        """删除当前用户某类的所有经历"""

        request.user.experiences.filter(type=type).delete()
        abort(200)