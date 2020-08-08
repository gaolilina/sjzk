from django import forms
from django.http import JsonResponse
from django.views.generic import View

from main.models import UserExperience, User
from main.utils import abort, get_score_stage
from main.utils.dfa import check_bad_words
from util.decorator.auth import app_auth
from util.decorator.param import fetch_object, validate_args


class Experience(View):
    @fetch_object(UserExperience.objects, 'exp')
    @app_auth
    @validate_args({
        'description': forms.CharField(max_length=100),
        'unit': forms.CharField(max_length=20),
        'profession': forms.CharField(required=False, max_length=20),
        'degree': forms.CharField(required=False, max_length=20),
        'time_in': forms.DateField(required=False),
        'time_out': forms.DateField(required=False),
    })
    def post(self, request, exp, **kwargs):
        """修改用户的某条经历"""

        if check_bad_words(kwargs["description"]):
            abort(400, '含有非法词汇')
        if exp.user != request.user:
            abort(403, '只能修改自己的经历')
        for k in kwargs:
            setattr(exp, k, kwargs[k])
        exp.save()
        abort(200)

    @fetch_object(UserExperience.objects, 'exp')
    @app_auth
    def delete(self, request, exp):
        """删除用户的某条经历"""

        if exp.user != request.user:
            abort(403, '只能删除自己的经历')
        exp.delete()
        abort(200)


class ExperienceList(View):
    @app_auth
    @fetch_object(User.enabled, 'user', force=False)
    def get(self, request, type, user=None):
        """获取用户的某类经历

        :return:
            count: 经历总数
            list: 经历列表
                id: 该记录的ID
                description: 经历描述
                unit: 学校或公司
                profession: 专业或职业
                degree: 学历
                time_in:
                time_out:
        """
        user = user or request.user

        c = user.experiences.filter(type=type).count()
        l = [{
            'id': e.id,
            'description': e.description,
            'unit': e.unit,
            'profession': e.profession,
            'degree': e.degree,
            'time_in': e.time_in,
            'time_out': e.time_out,
            'count_liker': e.likers.count(),
            'is_like': e.likers.filter(id=request.user.id).exists(),
        } for e in user.experiences.filter(type=type)]
        return JsonResponse({'count': c, 'list': l, 'code': 0})

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
            abort(400, '含有非法词汇')
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
