from django import forms
from django.core.urlresolvers import reverse
from django.db import IntegrityError, transaction
from django.http import HttpResponse, HttpResponseRedirect, HttpResponseBadRequest, HttpResponseForbidden
from django.template import loader, Context
from django.views.generic import View

from admin.models.admin_user import AdminUser
from admin.utils.decorators import *
from main.utils.decorators import validate_args
from util.decorator.auth import admin_auth


class Main(View):
    def get(self, request):
        return HttpResponseRedirect(reverse("admin:admin_users:info"))


class Login(View):
    def get(self, request):
        template = loader.get_template("login.html")
        context = Context()
        return HttpResponse(template.render(context))

    @validate_args({
        'username': forms.CharField(max_length=20),
        'password': forms.CharField(min_length=6, max_length=20, strip=False),
    })
    def post(self, request, username, password):
        try:
            user = AdminUser.enabled.get(username=username)
            if user.check_password(password):
                user.update_token()
                response = HttpResponseRedirect(reverse("admin:admin_users:info"))
                response.set_cookie("token", user.token)
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
    @admin_auth
    @require_role('xyz')
    def get(self, request):
        template = loader.get_template("register.html")
        context = Context({'user': request.user})
        return HttpResponse(template.render(context))

    @admin_auth
    @require_role('xyz')
    @validate_args({
        'username': forms.CharField(),
        'password': forms.CharField(min_length=6, max_length=20, strip=False),
        'phone_number': forms.CharField(max_length=11),
        'role': forms.CharField()
    })
    def post(self, request, username, password, phone_number, role):
        with transaction.atomic():
            try:
                user = AdminUser(username=username)
                user.set_password(password)
                user.phone_number = phone_number
                user.role = role
                user.save_and_generate_name()

                response = HttpResponseRedirect(reverse("admin:admin_users:info"))
                # response.set_cookie("usr", username)
                # response.set_cookie("pwd", user.password[:6])
                return response
            except IntegrityError as err:
                print(err)
                template = loader.get_template("register.html")
                context = Context({'msg': '用户名已存在', 'user': request.user})
                return HttpResponseBadRequest(template.render(context))
