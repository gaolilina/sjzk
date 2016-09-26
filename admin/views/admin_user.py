from django.template import loader, Context
from django.http import HttpResponse
from django.views.generic import View

class AdminUsers(View):
    def get(self, request):
        template = loader.get_template("user/info.html")
        context = Context()
        return HttpResponse(template.render(context))
