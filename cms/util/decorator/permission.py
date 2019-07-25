from functools import wraps

from django.http import JsonResponse


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
            # 向上递归找，被操作角色是不是操作者角色的子孙
            while child is not None:
                # 先判断级别，限制同级或越级修改（也包括超管的权限不允许被修改
                if parent.level >= child.level:
                    return JsonResponse({
                        'code': -5
                    })
                # 判断父子关系
                if child.parent_role == parent:
                    return function(self, request, *args, **kwargs)
                child = child.parent_role
            return JsonResponse({
                'code': -5
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
