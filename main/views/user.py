from django import forms
from django.db import IntegrityError
from django.http import JsonResponse, HttpResponseRedirect
from django.db import transaction
from django.views.generic import View
from rongcloud import RongCloud

from ChuangYi.settings import UPLOADED_URL
from ..utils import abort
from ..utils.decorators import *
from ..models import User, UserVisitor, UserExperience, UserValidationCode


__all__ = ['List', 'Token', 'Icon', 'Profile', 'ExperienceList', 'Experience',
           'FriendList', 'Friend', 'FriendRequestList', 'Search',
           'ValidationCode']


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
              'tags':
                  list(u.tags.get_queryset().values_list('name', flat=True)),
              'gender': u.gender,
              'liker_count': u.likers.count(),
              'follower_count': u.followers.count(),
              'visitor_count': u.visitors.count()} for u in users]
        return JsonResponse({'count': c, 'list': l})

    @validate_args({
        'phone_number': forms.CharField(min_length=11, max_length=11),
        'password': forms.CharField(min_length=6, max_length=32),
        'validation_code': forms.CharField(min_length=6, max_length=6),
    })
    def post(self, request, phone_number, password, validation_code):
        """注册，若成功返回用户令牌"""

        if not UserValidationCode.verify(phone_number, validation_code):
            abort(400)

        with transaction.atomic():
            try:
                user = User(phone_number=phone_number)
                user.set_password(password)
                # user.update_token()
                user.save_and_generate_name()
                # 注册成功后给融云服务器发送请求获取Token
                rcloud = RongCloud()
                r = rcloud.User.getToken(
                    userId=user.id, name=user.name,
                    portraitUri='http://www.rongcloud.cn/images/logo.png')
                token = r.result['token']
                user.token = token
                user.save()
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
                user = User.enabled.get(phone_number=username)
            else:
                user = User.enabled.get(username=username.lower())
        except User.DoesNotExist:
            abort(401)
        else:
            if not user.is_enabled:
                abort(403)
            if not user.check_password(password):
                abort(401)
            # user.update_token()
            if not user.icon:
                portraitUri = HttpResponseRedirect(
                    UPLOADED_URL + user.icon)
            else:
                portraitUri = 'http://www.rongcloud.cn/images/logo.png'
            rcloud = RongCloud()
            r = rcloud.User.getToken(
                userId=user.id, name=user.name,
                portraitUri=portraitUri)
            token = r.result['token']
            user.token = token
            user.save()
            return JsonResponse({'token': user.token})


class Icon(View):
    @fetch_object(User.enabled, 'user')
    @require_token
    def get(self, request, user=None):
        """获取用户头像"""

        user = user or request.user
        if user.icon:
            return HttpResponseRedirect(UPLOADED_URL + user.icon)
        abort(404)


class Profile(View):
    @fetch_object(User.enabled, 'user')
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
             'tags':
                 list(user.tags.get_queryset().values_list('name', flat=True)),
             'follower_count': user.followers.count(),
             'followed_count': user.followed_users.count() + user.followed_teams.count(),
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


# noinspection PyShadowingBuiltins
class ExperienceList(View):
    @fetch_object(User.enabled, 'user')
    @require_token
    def get(self, request, type, user=None):
        """获取用户的某类经历

        :return:
            count: 经历总数
            list: 经历列表
                id: 该记录的ID
                description: 经历描述
                unit: 学校或公司
                profession: 专业或职业
                degree: 学历
                time_in:
                time_out:
        """
        user = user or request.user

        c = user.education_experiences.filter(type=type).count()
        l = [{'id': e.id,
              'description': e.description,
              'unit': e.unit,
              'profession': e.profession,
              'degree': e.degree,
              'time_in': e.begin_time,
              'time_out': e.end_time,
              } for e in user.experiences.filter(type=type)]
        return JsonResponse({'count': c, 'list': l})


class Experience(View):
    @fetch_object(UserExperience.objects, 'exp')
    @require_token
    @validate_args({
        'description': forms.CharField(max_length=100),
        'unit': forms.CharField(max_length=20),
        'profession': forms.CharField(required=False, max_length=20),
        'degree': forms.CharField(required=False, max_length=20),
        'time_in': forms.DateField(required=False),
        'time_out': forms.DateField(required=False),
    })
    def post(self, request, exp, **kwargs):
        """修改用户的某条经历"""

        if exp.user != request.user:
            abort(403)
        for k in kwargs:
            setattr(exp, k, kwargs[k])
        abort(200)

    @fetch_object(UserExperience.objects, 'exp')
    @require_token
    def delete(self, request, exp):
        """删除用户的某条经历"""

        if exp.user != request.user:
            abort(403)
        exp.delete()
        abort(200)


class FriendList(View):
    ORDERS = (
        'time_created', '-time_created',
        'friend__name', '-friend__name',
    )

    @fetch_object(User.enabled, 'user')
    @require_token
    @validate_args({
        'offset': forms.IntegerField(required=False, min_value=0),
        'order': forms.IntegerField(required=False, min_value=0, max_value=3),
    })
    def get(self, request, user=None, offset=0, limit=10, order=1):
        """
        获取用户的好友列表

        :param offset: 偏移量
        :param limit: 数量上限
        :param order: 排序方式
            0: 成为好友时间升序
            1: 成为好友时间降序（默认值）
            2: 昵称升序
            3: 昵称降序
        :return:
            count: 好友总数
            list: 好友列表
                id: 用户ID
                username: 用户名
                name: 用户昵称
                time_created: 成为好友时间
        """
        user = user or request.user

        c = user.friends.count()
        qs = user.friends.order_by(self.ORDERS[order])[offset:offset + limit]
        l = [{'id': r.friend.id,
              'username': r.friend.username,
              'name': r.friend.name,
              'time_created': r.time_created} for r in qs]
        return JsonResponse({'count': c, 'list': l})


class Friend(View):
    @fetch_object(User.enabled, 'user')
    @fetch_object(User.enabled, 'other_user')
    @require_token
    def get(self, request, other_user, user=None):
        """检查两个用户是否为好友关系"""

        user = user or request.user

        if user.friends.filter(other_user=other_user).exists():
            abort(200)
        abort(404)


class FriendRequestList(View):
    @fetch_object(User.enabled, 'user')
    @require_token
    @validate_args({
        'description': forms.CharField(required=False, max_length=100)
    })
    def post(self, request, user, description=''):
        """向目标用户发出好友申请

        :param description: 附带消息
        """
        if user == request.user:
            abort(403)

        if user.friends.filter(other_user=request.user).exists():
            abort(403)

        if user.friend_requests.filter(other_user=request.user).exists():
            abort(200)

        user.friend_requests.create(other_user=request.user,
                                    description=description)
        abort(200)


class Search(View):
    ORDERS = ('time_created', '-time_created', 'name', '-name')

    @require_token
    @validate_args({
        'offset': forms.IntegerField(required=False, min_value=0),
        'order': forms.IntegerField(required=False, min_value=0, max_value=3),
        'username': forms.CharField(max_length=20),
    })
    def get(self, request, offset=0, limit=10, order=1, **kwargs):
        """
        搜索用户

        :param offset: 偏移量
        :param limit: 数量上限
        :param order: 排序方式
            0: 注册时间升序
            1: 注册时间降序（默认值）
            2: 昵称升序
            3: 昵称降序
        :param kwargs: 搜索条件
            username: 用户名包含字段

        :return:
            count: 用户总数
            list: 用户列表
                id: 用户ID
                username: 用户名
                name: 用户昵称
                gender: 性别
                like_count: 点赞数
                fan_count: 粉丝数
                visitor_count: 访问数
                tags: 标签
                time_created: 注册时间
        """
        i, j, k = offset, offset + limit, self.ORDERS[order]
        users = User.enabled.filter(username__icontain=kwargs['username'])
        c = users.count()
        l = [{'id': u.id,
              'username': u.username,
              'name': u.name,
              'gender': u.profile.gender,
              'like_count': u.like_count,
              'fan_count': u.fan_count,
              'visitor_count': u.visitor_count,
              'icon_url': u.icon_url,
              'tags':
                  list(u.tags.get_queryset().values_list('name', flat=True)),
              'time_created': u.time_created} for u in users.order_by(k)[i:j]]
        return JsonResponse({'count': c, 'list': l})


class ValidationCode(View):
    @validate_args({
        'phone_number': forms.CharField(min_length=11, max_length=11),
    })
    def get(self, request, phone_number):
        """获取验证码"""

        if not phone_number.isdigit():
            abort(400)

        return JsonResponse({
            'validation_code': UserValidationCode.generate(phone_number),
        })
