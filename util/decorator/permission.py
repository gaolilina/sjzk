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
            functions = CMSFunction.objects.filter(id=function_name)
            if not functions.exists():
                return JsonResponse({
                    'code': error.NO_PERMISSION
                })
            cms_function = functions.first()
            # 不需要验证，直接访问
            if not cms_function.needVerify:
                return function(self, request, *args, **kwargs)
            # 没登录
            if user is None:
                return JsonResponse({
                    'code': error.NO_USER
                })
            # 未分配角色，或（不是超管且未授予权限），则没有权限
            if not role or not role.functions.filter(id=cms_function.id).exists():
                return JsonResponse({
                    'code': error.NO_PERMISSION
                })
            # 有权限，允许访问
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
            fs = CMSFunction.objects.filter(id=function_name)
            if not fs.exists():
                return HttpResponseRedirect('/static/permission_deny.html')
            cms_function = fs.first()
            # 不需要验证，直接访问
            if not cms_function.needVerify:
                return function(self, request, *args, **kwargs)
            # 没登录
            if user is None:
                return HttpResponseRedirect(reverse("admin:login"))
            # 未分配角色，或（不是超管且未授予权限），则没有权限
            if not role or not role.functions.filter(id=cms_function.id).exists():
                return HttpResponseRedirect('/static/permission_deny.html')
            # 不需要验证，或有权限，允许访问
            return function(self, request, *args, **kwargs)

        return inner

    return decorator
