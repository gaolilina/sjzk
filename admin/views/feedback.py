from django import forms
from django.http import HttpResponse, HttpResponseForbidden
from django.template import loader, Context
from django.views.generic import View

from main.models.report import Report as ReportModel
from main.models.user import UserFeedback

from admin.utils.decorators import *

class Feedback(View):
    @require_cookie
    @require_role('yz')
    def get(self, request):
        template = loader.get_template("feedback/feedback.html")
        context = Context({'list': UserFeedback.objects.all(), 'user': request.user})
        return HttpResponse(template.render(context))

class Report(View):
    @require_cookie
    @require_role('yz')
    def get(self, request):
        template = loader.get_template("feedback/report.html")
        context = Context({'list': ReportModel.objects.all(), 'user': request.user})
        return HttpResponse(template.render(context))
