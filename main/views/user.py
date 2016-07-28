from django import forms
from django.db import IntegrityError
from django.http import JsonResponse, HttpResponseRedirect
from django.views.generic import View

from ChuangYi.settings import UPLOADED_URL
from ..utils import abort
from ..utils.decorators import *
from ..models import User, UserVisitor


__all__ = ['List', 'Token', 'Icon', 'Profile']


class List(View):
    ORDERS = ('time_created', '-time_created', 'name', '-name')

    @require_token
    @validate_args({
        'offset': forms.IntegerField(required=False, min_value=0),
        'order': forms.IntegerField(required=False, min_value=0, max_value=3),
    })
    def get(self, request, offset=0, limit=10, order=1):
        """获取用户列表

        :param offset: 偏移量
        :param order: 排序方式
            0: 注册时间升序
            1: 注册时间降序（默认值）
            2: 昵称升序
            3: 昵称降序
        :return:
            count: 用户总数
            list: 用户列表
                id: 用户ID
                time_created: 注册时间
                username: 用户名
                name: 用户昵称
                tags: 标签
                gender: 性别
                liker_count: 点赞数
                follower_count: 粉丝数
                visitor_count: 访问数
        """
        c = User.enabled.count()
        users = User.enabled.order_by(self.ORDERS[order])[offset:offset + limit]
        l = [{'id': u.id,
              'time_created': u.time_created,
              'username': u.username,
              'name': u.name,
              'tags': u.tags.values_list('name', flat=True),
              'gender': u.gender,
              'liker_count': u.likers.count(),
              'follower_count': u.followers.count(),
              'visitor_count': u.visitor.count()} for u in users]
        return JsonResponse({'count': c, 'list': l})

    @validate_args({
        'phone_number': forms.CharField(min_length=11, max_length=11),
        'password': forms.CharField(min_length=6, max_length=32),
    })
    def post(self, request, phone_number, password):
        """注册，若成功返回用户令牌"""

        try:
            user = User(phone_number=phone_number)
            user.set_password(password)
            user.update_token()
            user.save_and_generate_name()
            return JsonResponse({'token': user.token})
        except IntegrityError:
            abort(403)


class Token(View):
    @validate_args({
        'username': forms.RegexField(r'^[a-zA-Z0-9_]{4,15}$', strip=True),
        'password': forms.CharField(min_length=6, max_length=20, strip=False),
    })
    def post(self, request, username, password):
        """更新并返回用户令牌，纯数字用户名视为手机号"""

        try:
            if username.isdigit():
                user = User.objects.get(phone_number=username)
            else:
                user = User.objects.get(username=username.lower())
        except User.DoesNotExist:
            abort(401)
        else:
            if not user.is_enabled:
                abort(403)
            if not user.check_password(password):
                abort(401)
            user.update_token()
            return JsonResponse({'token': user.token})


class Icon(View):
    @fetch_object(User, 'user')
    @require_token
    def get(self, request, user=None):
        """获取用户头像"""

        user = user or request.user
        if user.icon:
            return HttpResponseRedirect(UPLOADED_URL + user.icon)
        abort(404)


class Profile(View):
    @fetch_object(User, 'user')
    @require_token
    def get(self, request, user=None):
        """获取用户的基本资料

        :return:
            id: 用户ID
            username: 用户名
            name: 昵称
            time_created: 注册时间
            description: 个人简介
            qq:
            wechat:
            email: 电子邮箱
            gender: 性别（0-保密，1-男，2-女）
            birthday: 生日
            province:
            city:
            county:
            tags: 标签，格式：['tag1', 'tag2', ...]
            x_counts 各种计数
                x: follower | followed | friend | liker | visitor
            is_verified:
            real_name:
            is_role_verified
            role:
            unit1:
            unit2:
            profession:
        """
        user = user or request.user

        # 更新访客记录
        if user != request.user:
            UserVisitor.objects \
                .update_or_create(visited=user, visitor=request.user)

        r = {'id': user.id,
             'time_created': user.time_created,
             'username': user.username,
             'name': user.name,
             'description': user.description,
             'email': user.email,
             'gender': user.gender,
             'birthday': user.birthday,
             'province': user.province,
             'city': user.city,
             'county': user.county,
             'tags': user.tags.values_list('name', flat=True),
             'follower_count': user.followers.count(),
             'followed_count': user.followed_users.count()
                               + user.follower_teams.count(),
             'friend_count': user.friends.count(),
             'liker_count': user.likers.count(),
             'visitor_count': user.visitors.count(),
             'is_verified': user.is_verified,
             'real_name': user.real_name,
             'is_role_verified': user.is_role_verified,
             'role': user.role,
             'unit1': user.unit1,
             'unit2': user.unit2,
             'profession': user.profession}
        return JsonResponse(r)
