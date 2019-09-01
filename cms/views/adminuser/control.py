from admin.models import AdminUser
from cms.util.decorator.permission import cms_permission_user
from util.auth import generate_psd, generate_token
from util.base.view import BaseView
from util.decorator.auth import cms_auth
from util.decorator.param import fetch_object
from util.decorator.permission import cms_permission


class ResetPassword(BaseView):

    @cms_auth
    @cms_permission('resetPassword')
    @fetch_object(AdminUser.objects, 'user')
    @cms_permission_user()
    def post(self, request, user, **kwargs):
        psd = user.phone_numer[-6:] if user.phone_numer else '123456'
        psd = generate_psd(psd)
        token = generate_token(psd)
        AdminUser.objects.filter(id=user.id).update(password=psd, token=token)
        return self.success()


class EnableControl(BaseView):

    @cms_auth
    @cms_permission('enableManager')
    @fetch_object(AdminUser.objects, 'user')
    @cms_permission_user()
    def post(self, request, user, **kwargs):
        if not user.is_enabled:
            AdminUser.objects.filter(id=user.id).update(is_enabled=True)
        return self.success()

    @cms_auth
    @cms_permission('disableManager')
    @fetch_object(AdminUser.objects, 'user')
    @cms_permission_user()
    def delete(self, request, user, **kwargs):
        if user.is_enabled:
            AdminUser.objects.filter(id=user.id).update(is_enabled=False)
        return self.success()
