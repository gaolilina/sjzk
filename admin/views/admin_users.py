from django import forms
from django.http import HttpResponse, HttpResponseForbidden
from django.template import loader, Context
from django.views.generic import View

from main.utils.decorators import validate_args
from main.utils import save_uploaded_image
from main.models import UserValidationCode

from util.decorator.auth import admin_auth


class AdminUsersInfo(View):
    @admin_auth
    def get(self, request):
        template = loader.get_template("admin_user/info.html")
        context = Context({'u': request.user, 'user': request.user})
        return HttpResponse(template.render(context))

    @admin_auth
    @validate_args({
        'name': forms.CharField(max_length=15, required=False),
        'gender': forms.CharField(max_length=1, required=False),
        'email': forms.CharField(required=False),
        'qq': forms.CharField(required=False),
        'wechat': forms.CharField(required=False),
    })
    def post(self, request, **kwargs):
        user = request.user
        for k in kwargs:
            setattr(user, k, kwargs[k])
        user.save()

        template = loader.get_template("admin_user/info.html")
        context = Context({'u': user, 'msg': '保存成功', 'user': request.user})
        return HttpResponse(template.render(context))


class AdminUsersIcon(View):
    @admin_auth
    def post(self, request):
        """上传用户头像"""

        icon = request.FILES.get('image')
        if not icon:
            HttpResponseForbidden()

        filename = save_uploaded_image(icon)
        if filename:
            request.user.icon = filename
            request.user.save()

            template = loader.get_template("admin_user/info.html")
            context = Context({'u': request.user, 'msg': '上传成功', 'user': request.user})
            return HttpResponse(template.render(context))
        HttpResponseForbidden()


class AdminUsersIndentify(View):
    @admin_auth
    def get(self, request):
        template = loader.get_template("admin_user/identify.html")
        context = Context({'u': request.user, 'user': request.user})
        return HttpResponse(template.render(context))

    @admin_auth
    @validate_args({
        'phone_number': forms.CharField(max_length=11),
        'old_pass': forms.CharField(min_length=6, max_length=20, strip=False),
        'new_pass': forms.CharField(min_length=6, max_length=20, strip=False, required=False),
        'valid_code': forms.CharField(required=False),
    })
    def post(self, request, phone_number, old_pass, new_pass, valid_code):
        if request.user.check_password(old_pass):
            if not UserValidationCode.verify(phone_number, valid_code):
                return HttpResponseForbidden('验证码与手机不匹配')
            request.user.phone_number = phone_number
            if new_pass != '':
                request.user.set_password(new_pass)
            request.user.save()
            template = loader.get_template("admin_user/identify.html")
            context = Context({'u': request.user, 'msg': '保存成功', 'user': request.user})
            return HttpResponse(template.render(context))
        return HttpResponseForbidden('旧密码错误')
