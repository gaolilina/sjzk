from django import forms
from django.db import IntegrityError
from django.db import transaction
from django.http import JsonResponse
from django.views.generic import View

from ..utils import abort, save_uploaded_image
from ..utils.decorators import *
from ..views.user import Icon as Icon_, Profile as Profile_


__all__ = ['Username', 'Password', 'Icon', 'IDCard', 'OtherCard', 'Profile']


class Username(View):
    @require_token
    def get(self, request):
        """获取当前用户的用户名"""

        return JsonResponse({'username': request.user.username})

    @require_token
    @validate_args({
        'username': forms.RegexField(r'^[a-zA-Z0-9_]{4,15}$', strip=True)
    })
    def post(self, request, username):
        """设置当前用户的用户名，存储时字母转换成小写，只能设置一次"""

        if request.user.username:
            abort(403, 'username is already set')

        if username.isdigit():
            abort(400)

        try:
            request.user.username = username.lower()
            request.user.save()
            return JsonResponse({'username': request.user.username})
        except IntegrityError:
            abort(403, 'username is used')


class Password(View):
    @require_token
    @validate_args({
        'new_password': forms.CharField(min_length=6, max_length=20),
        'old_password': forms.CharField(min_length=6, max_length=20),
    })
    def post(self, request, old_password, new_password):
        """修改密码

        :param old_password: 旧密码
        :param new_password: 新密码（6-20位）

        """
        if request.user.check_password(old_password):
            request.user.set_password(new_password)
            request.user.save()
            abort(200)
        abort(403)


# noinspection PyClassHasNoInit
class Icon(Icon_):
    @require_token
    def post(self, request):
        """上传用户头像"""

        icon = request.FILES.get('image')
        if not icon:
            abort(400)

        filename = save_uploaded_image(icon)
        if filename:
            request.user.icon = filename
            request.user.save()
            abort(200)
        abort(400)


class IDCard(View):
    @require_token
    def get(self, request):
        """检查是否已上传身份证照片"""

        if request.user.id_card:
            abort(200)
        abort(404)

    @require_token
    def post(self, request):
        """上传身份证照片"""

        if request.user.is_verified:
            abort(403)

        id_card = request.FILES.get('image')
        if not id_card:
            abort(400)

        filename = save_uploaded_image(id_card, is_private=True)
        if filename:
            request.user.id_card = filename
            request.user.save()
            abort(200)
        abort(400)


class OtherCard(View):
    @require_token
    def get(self, request):
        """检查是否已上传其他证件照片"""

        if request.user.other_card:
            abort(200)
        abort(404)

    @require_token
    def post(self, request):
        """上传其他证件照片"""

        if request.user.is_role_verified:
            abort(403)

        other_card = request.FILES.get('image')
        if not other_card:
            abort(400)

        filename = save_uploaded_image(other_card, is_private=True)
        if filename:
            request.user.other_card = filename
            request.user.save()
            abort(200)
        abort(400)


# noinspection PyClassHasNoInit
class Profile(Profile_):
    @require_token
    @validate_args({
        'name': forms.CharField(required=False, min_length=1, max_length=15),
        'description': forms.CharField(required=False, max_length=100),
        'qq': forms.CharField(required=False, max_length=20),
        'wechat': forms.CharField(required=False, max_length=20),
        'email': forms.EmailField(required=False),
        'gender': forms.IntegerField(required=False, min_value=0, max_value=2),
        'birthday': forms.DateField(required=False),
        'province': forms.CharField(required=False, max_length=20),
        'city': forms.CharField(required=False, max_length=20),
        'county': forms.CharField(required=False, max_length=20),
        'tags': forms.CharField(required=False, max_length=100),
        'real_name': forms.CharField(required=False, max_length=20),
        'id_number': forms.CharField(
            required=False, min_length=18, max_length=18),
        'role': forms.CharField(required=False, max_length=20),
        'unit1': forms.CharField(required=False, max_length=20),
        'unit2': forms.CharField(required=False, max_length=20),
        'profession': forms.CharField(required=False, max_length=20),
    })
    def post(self, request, **kwargs):
        """修改用户资料

        :param kwargs:
            name: 昵称
            description: 个人简介
            qq:
            wechat:
            email: 电子邮箱
            gender: 性别
            birthday: 生日
            province:
            city:
            county:
            tags: 标签，格式：'tag1|tag2|...'，最多5个
            real_name:
            id_number:
            role:
            other_number:
            unit1:
            unit2:
            profession:
        """

        name = kwargs.pop('name', None)
        if name:
            request.user.name = name
        normal_keys = ('description', 'qq', 'wechat', 'email', 'gender',
                       'birthday', 'province', 'city', 'county')
        for k in normal_keys:
            setattr(request.user, k, kwargs[k])

        tags = kwargs.pop('tags', None)
        if tags:
            tags = tags.split('|')[:5]
        with transaction.atomic():
            request.user.tags.delete()
            order = 0
            for tag in tags:
                tag = tag.strip()
                if tag:
                    request.user.tags.create(name=tag, order=order)
                    order += 1

        id_keys = ('real_name', 'id_number')
        if not request.user.is_verified:
            for k in id_keys:
                setattr(request.user, k, kwargs[k])

        role_keys = ('role', 'other_number', 'unit1', 'unit2', 'profession')
        if not request.user.is_role_verified:
            for k in role_keys:
                setattr(request.user, k, kwargs[k])

        abort(200)