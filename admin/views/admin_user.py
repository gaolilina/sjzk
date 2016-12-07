from django import forms
from django.http import HttpResponse, HttpResponseForbidden
from django.template import loader, Context
from django.views.generic import View

from main.utils.decorators import validate_args
from main.utils import identity_verify, save_uploaded_image

from admin.utils.decorators import require_cookie

class AdminUsersInfo(View):
    @require_cookie
    def get(self, request):
        template = loader.get_template("admin_user/info.html")
        context = Context({'u': request.user, 'user': request.user})
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

        template = loader.get_template("admin_user/info.html")
        context = Context({'u': user, 'msg': '保存成功', 'user': request.user})
        return HttpResponse(template.render(context))

class AdminUsersIcon(View):
    @require_cookie
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
    @require_cookie
    def get(self, request):
        template = loader.get_template("admin_user/identify.html")
        context = Context({'u': request.user, 'user': request.user})
        return HttpResponse(template.render(context))

    @require_cookie
    @validate_args({
        'real_name': forms.CharField(max_length=20, required=False),
        'id_number': forms.CharField(max_length=18, required=False),
    })
    def post(self, request, **kwargs):
        # 调用第三方接口验证身份证的正确性
        res = identity_verify(kwargs['id_number'])
        error_code = res["error_code"]
        if error_code != 0:
            HttpResponseForbidden(res["reason"])
        
        user = request.user
        if not user.is_verified:
            for k in id_keys:
                setattr(user, k, kwargs[k])
            user.save()

        template = loader.get_template("admin_user/identify.html")
        context = Context({'u': user, 'msg': '保存成功', 'user': request.user})
        return HttpResponse(template.render(context))
