from django import forms
from django.db import transaction
from django.http import JsonResponse
from django.views.generic import View

from ChuangYi.settings import DEFAULT_ICON_URL
from im.huanxin import register_to_huanxin
from main.models import User, UserValidationCode
from main.utils import abort, get_score_stage
from util.base.view import BaseView
from util.decorator.param import validate_args


class Account(View):
    @validate_args({
        'method': forms.CharField(max_length=20),
        'username': forms.RegexField(r'^[a-zA-Z0-9_]{4,15}$', strip=True, required=False),
        'password': forms.CharField(min_length=6, max_length=20, strip=False, required=False),
        'wechatid': forms.CharField(min_length=28, max_length=28, required=False)
    })
    def get(self, request, method, username=None, password=None, wechatid=None, **kwargs):
        if method == 'phone':
            try:
                if username.isdigit():
                    user = User.objects.get(phone_number=username)
                else:
                    user = User.objects.get(username=username.lower())
            except User.DoesNotExist:
                abort(401, '用户不存在')
            if not user.check_password(password):
                abort(401, '密码错误')
        elif method == 'wechat':
            users = User.objects.filter(wechat_id=wechatid)
            if users.count() == 1:
                user = users.first()
            else:
                users.update(wechat_id=None)
                abort(401, '用户不存在')
        else:
            abort(400)
            return
        # 查找到用户
        if not user.is_enabled:
            abort(403, '用户已删除')
        # user.update_token()
        # user.save()
        return JsonResponse({
            'token': user.token,
            'psd': user.password,
        })

    @validate_args({
        'phone_number': forms.CharField(min_length=11, max_length=11),
        'password': forms.CharField(min_length=6, max_length=32),
        'validation_code': forms.CharField(min_length=6, max_length=6),
        'invitation_code': forms.CharField(required=False),
        'wechatid': forms.CharField(max_length=28, min_length=28, required=False),
        'nickname': forms.CharField(max_length=15, required=False),
        'gender': forms.IntegerField(required=False, min_value=0, max_value=2),
        'province': forms.CharField(required=False, max_length=20),
        'city': forms.CharField(required=False, max_length=20),
        'icon': forms.CharField(required=False, max_length=500)
    })
    def post(self, request, method, phone_number, password, validation_code,
             invitation_code=None, icon=DEFAULT_ICON_URL,
             wechatid=None, nickname=None, gender=0, province=None, city=None):
        """注册，若成功返回用户令牌"""

        if method == 'phone':
            if User.objects.filter(phone_number=phone_number).count() > 0:
                abort(403, '用户已经注册')
                return
        elif method == 'wechat':
            if wechatid is None or nickname is None:
                abort(400, 'wechatid 或昵称不能为空')
                return
            # 防止绑定过微信的用户重复绑定
            if User.objects.filter(wechat_id=wechatid).count() > 0:
                abort(403, '用户已经注册')
                return
            user = User.objects.filter(phone_number=phone_number).first()
            if user is not None:
                # 绑定已经使用手机号注册的账户
                User.objects.filter(phone_number=phone_number).update(wechat_id=wechatid)
                return JsonResponse({'token': user.token})
        else:
            abort(400)
            return
        if not UserValidationCode.verify(phone_number, validation_code):
            abort(400, '验证码错误')

        with transaction.atomic():
            try:
                user = User(phone_number=phone_number, wechat_id=wechatid, city=city, province=province,
                            gender=gender, icon=icon)
                user.set_password(password)
                user.generate_info(phone_number)
                user.save()
                code, desc = register_to_huanxin(phone_number, user.password, user.name)
                if code != 200:
                    raise RuntimeError(desc)
                if invitation_code:
                    self.__add_invited_users(request.user, invitation_code.split(','))
                # 加积分
                user.score += get_score_stage(3)
                user.score_records.create(
                    score=get_score_stage(3), type="初始数据",
                    description="首次手机号注册")
                return JsonResponse({'token': user.token})
            except RuntimeError as e:
                print(e)
                abort(403, str(e) or '创建用户失败')

    def __add_invited_users(self, user, codes):
        for c in codes:
            u = User.enabled.filter(invitation_code=c)
            if not u:
                abort(404, '推荐码错误')
            user.invited.add(u)
            u.score_records.create(
                score=get_score_stage(4), type="活跃度",
                description="邀请码被使用")


class AccountCheck(BaseView):

    @validate_args({
        'phone': forms.CharField(max_length=11)
    })
    def get(self, request, phone):
        return self.success({
            'exists': User.objects.filter(phone_number=phone).exists()
        })
