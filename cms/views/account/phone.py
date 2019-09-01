from django import forms

from admin.models import AdminUser
from main.models import UserValidationCode
from util.auth import generate_token
from util.base.view import BaseView
from util.decorator.auth import cms_auth
from util.decorator.param import validate_args
from util.message import send_message


class ChangePhone(BaseView):

    @cms_auth
    @validate_args({
        'phone': forms.CharField(max_length=11, min_length=11)
    })
    def get(self, request, phone, **kwargs):
        """
        未绑定的，是绑定手机号
        已绑定的，则是更换手机号
        :param request:
        :param phone:
        :param kwargs:
        :return:
        """
        if not phone.isdigit():
            return self.fail(1, '手机号码格式不正确')
        user = request.user
        if user.phone_number and user.phone_number != phone:
            return self.fail(2, '您输入的手机号与当前用户手机号不符，请确认')
        # 发送验证码
        code = UserValidationCode.generate(phone)
        tpl_value = "#code#=" + code
        send_message(phone, tpl_value)
        return self.success()

    @cms_auth
    @validate_args({
        'phone_number': forms.CharField(max_length=11, min_length=11),
        'validation_code': forms.CharField(min_length=6, max_length=6),
    })
    def post(self, request, phone_number, validation_code, **kwargs):
        """
        绑定或更换手机号
        :param request:
        :param phone_number:
        :param validation_code:
        :param kwargs:
        :return:
        """
        if not phone_number.isdigit():
            return self.fail(1, '新手机号码格式不正确')
        user = request.user
        # 如果 user.phone_number 不为空，则是则更换手机号，需要验证原手机号和验证码
        # 如果 user.phone_number 为空，则是绑定手机，需验证新手机号和验证码
        if not UserValidationCode.verify(user.phone_number or phone_number, validation_code):
            return self.fail(1, '验证码错误')
        if AdminUser.objects.filter(phone_number=phone_number).exists() \
                or AdminUser.objects.filter(username=phone_number).exists():
            return self.fail(2, '手机号已被绑定')
        update_params = {
            'phone_number': phone_number,
            'token': generate_token(user.password),
        }
        # 一般人的用户名和手机号都是相同的
        # 但超管的 username 是 admin
        if user.username == user.phone_number:
            update_params['username'] = phone_number
        AdminUser.objects.filter(id=user.id).update(**update_params)
        return self.success()
