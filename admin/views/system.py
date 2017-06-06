from django import forms
from django.core.urlresolvers import reverse
from django.db import IntegrityError, transaction
from django.http import HttpResponse, HttpResponseRedirect, HttpResponseBadRequest, HttpResponseForbidden
from django.template import loader, Context
from django.views.generic import View

from main.utils.decorators import validate_args
from main.models import System as SystemModel, SystemNotification
from admin.utils.decorators import *

class Setting(View):
    @require_cookie
    @require_role('yz')
    def get(self, request):
        template = loader.get_template("system.html")
        context = Context({'m': SystemModel.objects.get(id=1), 'user': request.user})
        return HttpResponse(template.render(context))

    @require_cookie
    @require_role('yz')
    @validate_args({
        'version_number': forms.FloatField(required=False),
        'score_value_one': forms.IntegerField(required=False),
        'score_value_two': forms.IntegerField(required=False),
        'score_value_three': forms.IntegerField(required=False),
        'score_value_four': forms.IntegerField(required=False),
        'score_value_five': forms.IntegerField(required=False),
        'max_reported': forms.IntegerField(required=False),
    })
    def post(self, request, **kwargs):
        model = SystemModel.objects.get(id=1)
        for k in kwargs:
            setattr(model, k.upper(), kwargs[k])
        model.save()
        template = loader.get_template("system.html")
        context = Context({'m': model, 'msg': '保存成功', 'user': request.user})
        return HttpResponse(template.render(context))

class Notification(View):
    @require_cookie
    @require_role('yz')
    def get(self, request):
        template = loader.get_template("notification.html")
        context = Context({'user': request.user})
        return HttpResponse(template.render(context))

    @require_cookie
    @require_role('yz')
    @validate_args({
        'content': forms.CharField(max_length=500),
    })
    def post(self, request, content):
        n = SystemNotification(content=content)
        n.save()

        template = loader.get_template("notification.html")
        context = Context({'msg': '发送成功', 'user': request.user})
        return HttpResponse(template.render(context))
