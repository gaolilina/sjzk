from django import forms
from django.core.urlresolvers import reverse
from django.db import IntegrityError, transaction
from django.http import HttpResponse, HttpResponseRedirect, HttpResponseBadRequest, HttpResponseForbidden
from django.template import loader, Context
from django.views.generic import View

from main.utils.decorators import validate_args

from admin.models.admin_user import AdminUser

class Login(View):
    def get(self, request):
        template = loader.get_template("login.html")
        context = Context()
        return HttpResponse(template.render(context))

    @validate_args({
        'username': forms.CharField(),
        'password': forms.CharField(min_length=6, max_length=20, strip=False),
    })
    def post(self, request, username, password):
        try:
            user = AdminUser.enabled.get(username=username)
            if user.check_password(password):
                response = HttpResponseRedirect(reverse("admin:admin_user:info"))
                response.set_cookie("usr", username)
                response.set_cookie("pwd", user.password[:6])
                return response
            else:
                template = loader.get_template("login.html")
                context = Context({'msg': '用户名或密码错误'})
                return HttpResponseForbidden(template.render(context))
        except AdminUser.DoesNotExist:
            template = loader.get_template("login.html")
            context = Context({'msg': '无此用户'})
            return HttpResponseForbidden(template.render(context))

class Register(View):
    def get(self, request):
        template = loader.get_template("register.html")
        context = Context()
        return HttpResponse(template.render(context))

    @validate_args({
        'username': forms.CharField(),
        'password': forms.CharField(min_length=6, max_length=20, strip=False),
    })
    def post(self, request, username, password):
        with transaction.atomic():
            try:
                user = AdminUser(username=username)
                user.set_password(password)
                user.save_and_generate_name()

                response = HttpResponseRedirect(reverse("admin:admin_user:info"))
                response.set_cookie("usr", username)
                response.set_cookie("pwd", user.password[:6])
                return response
            except IntegrityError:
                template = loader.get_template("register.html")
                context = Context({'msg': '用户名已存在'})
                return HttpResponseBadRequest(template.render(context))