from functools import wraps

from django.http import JsonResponse

from cms.util.role import compare_role
from util.code import error


def cms_permission_role(role_param='role'):
    '''
    操作角色的权限
    只有当前角色的上级角色能操作当前角色
    '''

    def decorator(function):
        @wraps(function)
        def inner(self, request, *args, **kwargs):
            child = kwargs[role_param]
            parent = request.user.system_role
            has_permission = compare_role(parent, child)
            if has_permission:
                return function(self, request, *args, **kwargs)
            else:
                return JsonResponse({
                    'code': error.NO_PERMISSION
                })

        return inner

    return decorator


def cms_permission_user(user_param='user'):
    '''
    操作角色的权限
    只有用户角色的上级角色能操作下级角色用户
    '''

    def decorator(function):
        @wraps(function)
        def inner(self, request, *args, **kwargs):
            child = kwargs[user_param].system_role
            parent = request.user.system_role
            has_permission = compare_role(parent, child)
            if has_permission:
                return function(self, request, *args, **kwargs)
            else:
                return JsonResponse({
                    'code': error.NO_PERMISSION
                })

        return inner

    return decorator


def cms_permission_role_function(function_param='function'):
    '''
    操作功能的权限
    只有操作者拥有这项功能，才能将该功能赋予别人
    '''

    def decorator(function):
        @wraps(function)
        def inner(self, request, *args, **kwargs):
            f = kwargs[function_param]
            role = request.user.system_role
            if not role.is_admin() and not role.functions.contains(f):
                return JsonResponse({
                    'code': 1,
                    'msg': '当前用户没有这个功能，所以不能对该功能进行操作'
                })
            return function(self, request, *args, **kwargs)

        return inner

    return decorator
