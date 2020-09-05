from django.http import HttpResponse
from django.template import loader, Context
from django.views.generic import View

from admin.models import OperationLog
from util.decorator.auth import admin_auth


class OpLog(View):
    @admin_auth
    def get(self, request):
        template = loader.get_template("op_log.html")
        context = Context({'list': OperationLog.objects.filter(), 'user': request.user})
        return HttpResponse(template.render(context))
