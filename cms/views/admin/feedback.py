from django import forms
from django.http import HttpResponse
from django.template import loader, Context
from django.views.generic import View

from admin.utils.decorators import *
from main.models.report import Report as ReportModel
from main.models.system import System
from main.models.user import User, UserFeedback
from util.decorator.auth import admin_auth
from util.decorator.param import old_validate_args
from util.base.view import BaseView


class Feedback(BaseView):
    @admin_auth
    @require_role('xyz')
    def get(self, request):
        context = Context({'list': UserFeedback.objects.all(), 'user': request.user})
        return self.success(data=context)


class Report(BaseView):
    @admin_auth
    @require_role('xyz')
    def get(self, request):
        context = Context({'list': ReportModel.enabled.all(), 'user': request.user})
        return self.success(data=context)


class ReportDeal(BaseView):
    @fetch_record(ReportModel.enabled, 'model', 'id')
    @admin_auth
    @require_role('xyz')
    @old_validate_args({
        'ban': forms.CharField(),
    })
    def post(self, request, **kwargs):
        model = kwargs["model"]
        if model.type == "user":
            if kwargs['ban'] == 'true':
                user = User.objects.filter(id=model.object_id)[0]
                user.reported_count = user.reported_count + 1
                if user.reported_count >= System.objects.get(id=1).MAX_REPORTED:
                    user.is_enabled = False
                user.save()
        model.is_enabled = False
        model.save()
        return self.success()
