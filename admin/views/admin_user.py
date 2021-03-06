# Auto generated by admin_user.py
from django import forms
from django.http import HttpResponse
from django.template import loader, Context
from django.views.generic import View

from admin.models.admin_user import *

from admin.utils.decorators import *
from util.decorator.auth import admin_auth
from util.decorator.param import old_validate_args


class AdminUserView(View):
    @fetch_record(AdminUser.objects, 'mod', 'id')
    @admin_auth
    @require_role('yz')
    def get(self, request, mod):
        template = loader.get_template("admin_user/admin_user.html")
        context = Context({'mod': mod, 'user': request.user})
        return HttpResponse(template.render(context))

    @fetch_record(AdminUser.objects, 'mod', 'id')
    @admin_auth
    @require_role('z')
    @old_validate_args({
        'is_enabled': forms.BooleanField(required=False),
        'username': forms.CharField(max_length=20, ),
        'password': forms.CharField(max_length=128, ),
        'time_created': forms.DateTimeField(required=False, ),
        'role': forms.CharField(max_length=26, required=False, ),
        'name': forms.CharField(max_length=15, required=False, ),
        'description': forms.CharField(max_length=100, required=False, ),
        'icon': forms.CharField(max_length=100, required=False, ),
        'gender': forms.CharField(max_length=1, required=False, ),
        'email': forms.CharField(max_length=254, required=False, ),
        'phone_number': forms.CharField(max_length=11, required=False, ),
        'is_verified': forms.BooleanField(required=False),
        'real_name': forms.CharField(max_length=20, required=False, ),
        'id_number': forms.CharField(max_length=18, required=False, ),
    })
    def post(self, request, mod, **kwargs):
        for k in kwargs:
            setattr(mod, k, kwargs[k])
        mod.save()

        admin_log("admin_user", mod.id, 1, request.user)

        template = loader.get_template("admin_user/admin_user.html")
        context = Context({'mod': mod, 'msg': '保存成功', 'user': request.user})
        return HttpResponse(template.render(context))


class AdminUserList(View):
    @admin_auth
    @require_role('yz')
    @old_validate_args({
        'page': forms.IntegerField(required=False, min_value=0),
    })
    def get(self, request, page=0, **kwargs):
        if kwargs["id"] is not None:
            list = AdminUser.objects.filter(admin_user_id=kwargs["id"])
            template = loader.get_template("admin_user/admin_user_list.html")
            context = Context(
                {'page': page, 'list': list, 'redir': 'admin:admin_user:admin_user', 'user': request.user})
            return HttpResponse(template.render(context))
        elif request.GET.get("name") is not None:
            name = request.GET.get("name")
            template = loader.get_template("admin_user/index.html")
            if AdminUser == AdminUser:
                redir = 'admin:admin_user:admin_user'
            else:
                redir = 'admin:admin_user:admin_user_list'
            context = Context({'name': name, 'list': AdminUser.objects.filter(name__contains=name), 'redir': redir,
                               'rb': 'admin_user', 'user': request.user})
            return HttpResponse(template.render(context))
        else:
            template = loader.get_template("admin_user/index.html")
            context = Context({'rb': 'admin_user', 'user': request.user})
            return HttpResponse(template.render(context))
