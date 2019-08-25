from django import forms

from admin.models import AdminUser
from util.base.view import BaseView
from util.decorator.auth import cms_auth
from util.decorator.param import validate_args


class UserInfo(BaseView):

    @cms_auth
    def get(self, request):
        user = request.user
        return self.success({
            'is_enabled': user.is_enabled,
            'username': user.username,
            'role': user.system_role.name if user.system_role is not None else None,
            'name': user.name,
            'gender': user.gender
        })

    @cms_auth
    @validate_args({
        'name': forms.CharField(max_length=100, required=False),
        'gender': forms.IntegerField(required=False)
    })
    def post(self, request, **kwargs):
        update_param_list = ['name', 'gender']
        update_param = {}
        for k in update_param_list:
            if k in kwargs:
                update_param[k] = kwargs[k]
        if len(update_param) > 0:
            AdminUser.objects.filter(id=request.user.id).update(**update_param)
        return self.success()
