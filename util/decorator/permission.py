from functools import wraps

from django.core.urlresolvers import reverse
from django.http import JsonResponse, HttpResponseRedirect

from modellib.models import CMSFunction
from util.code import error


def cms_permission(function_name):
    def decorator(function):
        @wraps(function)
        def inner(self, request, *args, **kwargs):
            # 超级管理员不限权限
            user = getattr(request, 'user')
            role = getattr(user, 'system_role')
            if user is not None and role is not None and role.is_admin():
                return function(self, request, *args, **kwargs)
            # 函数未上线，认为没有权限
            if CMSFunction.objects.filter(id=function_name).count() <= 0:
                return JsonResponse({
                    'code': error.NO_PERMISSION
                })
            cms_function = CMSFunction.objects.get(id=function_name)
            # 没登录
            if cms_function.needVerify and user is None:
                return JsonResponse({
                    'code': error.NO_USER
                })

            if cms_function.needVerify:
                # 未分配角色，或（不是超管且未授予权限），则没有权限
                if not role or role.functions.filter(id=cms_function.id).count() <= 0:
                    return JsonResponse({
                        'code': error.NO_PERMISSION
                    })
            # 不需要验证，或有权限，允许访问
            return function(self, request, *args, **kwargs)

        return inner

    return decorator


def admin_permission(function_name):
    def decorator(function):
        @wraps(function)
        def inner(self, request, *args, **kwargs):
            # 超级管理员不限权限
            user = getattr(request, 'user')
            role = getattr(user, 'system_role')
            if user is not None and role is not None and role.is_admin():
                return function(self, request, *args, **kwargs)
            # 函数未上线，认为没有权限
            if CMSFunction.objects.filter(id=function_name).count() <= 0:
                return HttpResponseRedirect('/static/permission_deny.html')
            cms_function = CMSFunction.objects.get(id=function_name)
            # 没登录
            if cms_function.needVerify and user is None:
                return HttpResponseRedirect(reverse("admin:login"))

            if cms_function.needVerify:
                # 未分配角色，或（不是超管且未授予权限），则没有权限
                if not role or role.functions.filter(id=cms_function.id).count() <= 0:
                    return HttpResponseRedirect('/static/permission_deny.html')
            # 不需要验证，或有权限，允许访问
            return function(self, request, *args, **kwargs)

        return inner

    return decorator
