#! /usr/bin/env python3
# -*- coding: utf-8 -*-

from functools import wraps

from django.core.urlresolvers import reverse
from django.http import JsonResponse, HttpResponseRedirect

from admin.models import AdminUser
from main.models import User, System
from main.models.role import Role
from main.utils import abort
from util.code import error


def cms_auth(function):
    """
    管理端用户认证
    """

    @wraps(function)
    def decorator(self, request, *args, **kwargs):
        if getattr(request, 'user', None) is not None:
            return function(self, request, *args, **kwargs)
        token = request.META.get('HTTP_X_USER_TOKEN')
        if not token or AdminUser.objects.filter(token=token).count() <= 0:
            return JsonResponse({
                'code': error.NO_USER
            })
        user = AdminUser.objects.get(token=token)
        if not user.is_enabled:
            return JsonResponse({
                'code': error.USER_DISABLED
            })
        # 用户正常
        request.user = user
        return function(self, request, *args, **kwargs)

    return decorator


def admin_auth(function):
    """验证cookie，对非登陆用户跳转到登陆页面
    """

    @wraps(function)
    def decorator(self, request, *args, **kwargs):
        if getattr(request, 'user', None) is not None:
            return function(self, request, *args, **kwargs)
        token = request.COOKIES.get('token')
        if not token or AdminUser.objects.filter(token=token).count() <= 0:
            return HttpResponseRedirect(reverse("admin:login"))
        user = AdminUser.objects.get(token=token)
        if not user.is_enabled:
            return HttpResponseRedirect(reverse("admin:login"))
        # 用户验证通过
        request.user = user
        return function(self, request, *args, **kwargs)

    return decorator


def app_auth(function):
    """
    旧的用户认证
    """

    @wraps(function)
    def decorator(self, request, *args, **kwargs):
        if getattr(request, 'user', None) is not None:
            return function(self, request, *args, **kwargs)
        token = request.META.get('HTTP_X_USER_TOKEN')
        if not token:
            abort(401, '缺少参数token')
        try:
            user = User.objects.get(token=token)
            if user.is_enabled:
                request.user = user
                request.param = System.objects.get(
                    role__name=user.role if user.role else Role.objects.get(name__isnull=True).name)
                return function(self, request, *args, **kwargs)
            abort(403, '用户已删除')
        except User.DoesNotExist:
            abort(404, '用户不存在')

    return decorator


def client_auth(function):
    """
    客户端用户认证
    """

    @wraps(function)
    def decorator(self, request, *args, **kwargs):
        if getattr(request, 'user', None) is not None:
            return function(self, request, *args, **kwargs)
        token = request.META.get('HTTP_X_USER_TOKEN')
        if not token or User.objects.filter(token=token).count() <= 0:
            return JsonResponse({
                'code': error.NO_USER
            })
        user = User.objects.get(token=token)
        if not user.is_enabled:
            return JsonResponse({
                'code': error.USER_DISABLED
            })
        # 用户正常
        request.user = user
        return function(self, request, *args, **kwargs)

    return decorator
