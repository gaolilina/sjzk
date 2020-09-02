from django.http import HttpResponse
from django.template import loader, Context
from django.views.generic import View

from admin.utils.decorators import fetch_record, require_role
from main.models import Competition
from util.decorator.auth import admin_auth
from util.base.view import BaseView


class AdminCompetitionExcelView(BaseView):
    @fetch_record(Competition.enabled, 'model', 'id')
    @admin_auth
    @require_role('axyz')
    def get(self, request, model):
        # if len(CompetitionOwner.objects.filter(competition=model, user=request.user)) == 0:
        #    return HttpResponseForbidden()

        context = Context({'model': model})
        return HttpResponse(context, content_type="text/csv")
