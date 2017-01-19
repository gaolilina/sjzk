from django import forms
from django.core.urlresolvers import reverse
from django.db import IntegrityError, transaction
from django.http import HttpResponse, HttpResponseRedirect, HttpResponseBadRequest, HttpResponseForbidden
from django.template import loader, Context
from django.views.generic import View

from main.utils.decorators import validate_args
from main.models import System as SystemModel
from admin.utils.decorators import *

class Setting(View):
    @require_cookie
    def get(self, request):
        template = loader.get_template("system.html")
        context = Context({'m': SystemModel.objects.get(id=1)})
        return HttpResponse(template.render(context))

    @require_cookie
    @validate_args({
        'version_number': forms.FloatField(required=False),
        'recent_visitor_time': forms.IntegerField(required=False),
        'score_stage_one': forms.IntegerField(required=False),
        'score_stage_two': forms.IntegerField(required=False),
        'score_stage_three': forms.IntegerField(required=False),
        'score_stage_four': forms.IntegerField(required=False),
        'score_stage_five': forms.IntegerField(required=False),
    })
    def post(self, request, **kwargs):
        model = SystemModel.objects.get(id=1)
        for k in kwargs:
            setattr(model, k.upper(), kwargs[k])
        model.save()
        template = loader.get_template("system.html")
        context = Context({'m': model, 'msg': '保存成功'})
        return HttpResponse(template.render(context))
