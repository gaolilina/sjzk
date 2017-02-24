from django import forms
from django.core.urlresolvers import reverse
from django.db import IntegrityError, transaction
from django.http import HttpResponse, HttpResponseRedirect, HttpResponseBadRequest, HttpResponseForbidden
from django.template import loader, Context
from django.views.generic import View

from main.utils.decorators import validate_args
from admin.models import OperationLog
from admin.utils.decorators import *

class OpLog(View):
    @require_cookie
    def get(self, request):
        template = loader.get_template("op_log.html")
        context = Context({'list': OperationLog.objects.filter(), 'user': request.user})
        return HttpResponse(template.render(context))