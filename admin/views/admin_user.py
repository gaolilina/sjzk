from django import forms
from django.http import HttpResponse
from django.template import loader, Context
from django.views.generic import View

from main.utils.decorators import validate_args

from admin.utils.decorators import require_cookie

class AdminUsersInfo(View):
    @require_cookie
    def get(self, request):
        template = loader.get_template("user/info.html")
        context = Context({'u': request.user})
        return HttpResponse(template.render(context))

    @require_cookie
    @validate_args({
        'name': forms.CharField(max_length=15, required=False),
        'gender': forms.CharField(max_length=1, required=False),
        'phone_number': forms.CharField(max_length=11, required=False),
        'email': forms.CharField(required=False),
        'description': forms.CharField(max_length=100, required=False),
    })
    def post(self, request, **kwargs):
        user = request.user
        for k in kwargs:
            setattr(user, k, kwargs[k])
        user.save()

        template = loader.get_template("user/info.html")
        context = Context({'u': user, 'msg': '保存成功'})
        return HttpResponse(template.render(context))
