from django import forms
from django.http import HttpResponse
from django.template import loader, Context
from django.views.generic import View

from admin.models import CompetitionOwner
from admin.utils.decorators import require_role, fetch_record, admin_log
from main.models import Competition, CompetitionStage
from util.decorator.auth import admin_auth
from util.decorator.param import old_validate_args
from util.decorator.permission import admin_permission


class AdminCompetitionList(View):
    @admin_auth
    @admin_permission('competition_list')
    def get(self, request):
        try:
            filter_param = {}  # TODO: same with activity
            if not request.user.can_x():
                filter_param['user'] = request.user
            template = loader.get_template("admin_competition/list.html")
            context = Context({'list': CompetitionOwner.objects.filter(**filter_param), 'user': request.user})
            return HttpResponse(template.render(context))
        except CompetitionOwner.DoesNotExist:
            template = loader.get_template("admin_competition/add.html")
            context = Context({'user': request.user})
            return HttpResponse(template.render(context))


class AdminCompetitionView(View):
    @admin_auth
    @admin_permission('competition_detail')
    @fetch_record(Competition.enabled, 'model', 'id')
    def get(self, request, model):
        # if len(CompetitionOwner.objects.filter(competition=model, user=request.user)) == 0:
        #    return HttpResponseForbidden()

        template = loader.get_template("admin_competition/view.html")
        context = Context(
            {'model': model, 'user': request.user, 'stages': CompetitionStage.objects.filter(competition=model)})
        return HttpResponse(template.render(context))


## 弃用
class CompetitionView(View):
    @fetch_record(Competition.objects, 'mod', 'id')
    @admin_auth
    @require_role('yz')
    def get(self, request, mod):
        template = loader.get_template("competition/competition.html")
        context = Context({'mod': mod, 'user': request.user})
        return HttpResponse(template.render(context))

    @fetch_record(Competition.objects, 'mod', 'id')
    @admin_auth
    @require_role('yz')
    @old_validate_args({
        'name': forms.CharField(max_length=50, ), 'status': forms.IntegerField(required=False, ),
        'content': forms.CharField(max_length=1000, ), 'deadline': forms.DateTimeField(required=False, ),
        'time_started': forms.DateTimeField(required=False, ), 'time_ended': forms.DateTimeField(required=False, ),
        'time_created': forms.DateTimeField(required=False, ), 'allow_team': forms.IntegerField(required=False, ),
        'province': forms.CharField(max_length=20, required=False, ),
        'city': forms.CharField(max_length=20, required=False, ), 'min_member': forms.IntegerField(required=False, ),
        'max_member': forms.IntegerField(required=False, ), 'unit': forms.CharField(max_length=20, required=False, ),
        'user_type': forms.IntegerField(required=False, ), 'is_enabled': forms.BooleanField(required=False),
    })
    def post(self, request, mod, **kwargs):
        for k in kwargs:
            setattr(mod, k, kwargs[k])
        mod.save()

        admin_log("competition", mod.id, 1, request.user)

        template = loader.get_template("competition/competition.html")
        context = Context({'mod': mod, 'msg': '保存成功', 'user': request.user})
        return HttpResponse(template.render(context))


class CompetitionList(View):
    @admin_auth
    @require_role('yz')
    @old_validate_args({
        'page': forms.IntegerField(required=False, min_value=0),
    })
    def get(self, request, page=0, **kwargs):
        if kwargs["id"] is not None:
            list = Competition.objects.filter(competition_id=kwargs["id"])
            template = loader.get_template("competition/competition_list.html")
            context = Context(
                {'page': page, 'list': list, 'redir': 'admin:competition:competition', 'user': request.user})
            return HttpResponse(template.render(context))
        elif request.GET.get("name") is not None:
            name = request.GET.get("name")
            content = request.GET.get("content")
            unit = request.GET.get("unit")
            province = request.GET.get("province")
            city = request.GET.get("city")

            template = loader.get_template("competition/index.html")
            if Competition == Competition:
                redir = 'admin:competition:competition'
            else:
                redir = 'admin:competition:competition_list'
            context = Context({
                'name': name,
                'content': content,
                'unit': unit,
                'province': province,
                'city': city,
                'list': Competition.objects.filter(
                    name__contains=name,
                    content__contains=content,
                    unit__contains=unit,
                    province__contains=province,
                    city__contains=city), 'redir': redir, 'rb': 'competition', 'user': request.user})
            return HttpResponse(template.render(context))
        else:
            template = loader.get_template("competition/index.html")
            context = Context({'rb': 'competition', 'user': request.user})
            return HttpResponse(template.render(context))
