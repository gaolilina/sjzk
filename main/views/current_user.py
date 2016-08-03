from django import forms
from django.db import IntegrityError
from django.db import transaction
from django.http import JsonResponse
from django.views.generic import View

from ..models import User, Team
from ..utils import abort, save_uploaded_image
from ..utils.decorators import *
from ..views.user import Icon as Icon_, Profile as Profile_, ExperienceList as \
    ExperienceList_, FriendList, Friend as Friend_


__all__ = ['Username', 'Password', 'Icon', 'IDCard', 'OtherCard', 'Profile',
           'ExperienceList', 'FollowedUserList', 'FollowedUser',
           'FollowedTeamList', 'FollowedTeam', 'FriendList', 'Friend',
           'FriendRequestList', 'FriendRequest']


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


# noinspection PyClassHasNoInit,PyShadowingBuiltins
class ExperienceList(ExperienceList_):
    @require_token
    @validate_args({
        'description': forms.CharField(max_length=100),
        'unit': forms.CharField(max_length=20),
        'profession': forms.CharField(required=False, max_length=20),
        'degree': forms.CharField(required=False, max_length=20),
        'time_in': forms.DateField(required=False),
        'time_out': forms.DateField(required=False),
    })
    def post(self, request, type, **kwargs):
        """增加一条经历"""

        request.user.experiences.create(
            type=type, description=kwargs['description'], unit=kwargs['unit'],
            profession=kwargs['profession'], degree=['degree'],
            time_in=kwargs['time_in'], time_out=kwargs['time_out']
        )
        abort(200)

    @require_token
    def delete(self, request, type):
        """删除当前用户某类的所有经历"""

        request.user.experiences.filter(type=type).delete()
        abort(200)


class FollowedUserList(View):
    ORDERS = [
        'create_time', '-create_time',
        'followed__name', '-followed__name',
    ]

    @require_token
    @validate_args({
        'offset': forms.IntegerField(required=False, min_value=0),
        'order': forms.IntegerField(required=False, min_value=0, max_value=3),
    })
    def get(self, request, offset=0, limit=10, order=1):
        """获取用户的关注用户列表

        :param offset: 偏移量
        :param order: 排序方式
            0: 关注时间升序
            1: 关注时间降序（默认值）
            2: 昵称升序
            3: 昵称降序
        :return:
            count: 关注的用户总数
            list: 关注的用户列表
                id: 用户ID
                username: 用户名
                name: 用户昵称
                time_created: 关注时间
        """
        c = request.user.followed_users.count()
        qs = request.user.followed_users.order_by(
            self.ORDERS[order])[offset:offset + limit]
        l = [{'id': r.followed.id,
              'username': r.followed.username,
              'name': r.followed.name,
              'time_created': r.create_time} for r in qs]
        return JsonResponse({'count': c, 'list': l})


class FollowedUser(View):
    @fetch_object(User, 'user')
    @require_token
    def get(self, request, user):
        """判断当前用户是否关注了user"""

        if request.user.followed_users.filter(follower=user).exists():
            abort(200)
        abort(404)

    @fetch_object(User, 'user')
    @require_token
    def post(self, request, user):
        """令当前用户关注user"""

        if request.user.followed_users.filter(follower=user).exists():
            abort(403)
        request.user.followed_users.create(followed=user)
        abort(200)

    @fetch_object(User, 'user')
    @require_token
    def delete(self, request, user):
        """令当前用户取消关注user"""

        qs = request.user.followed_users.filter(followed=user)
        if qs.exists():
            qs.delete()
            abort(200)
        abort(403)


class FollowedTeamList(View):
    ORDERS = [
        'create_time', '-create_time',
        'followed__name', '-followed__name',
    ]

    @require_token
    @validate_args({
        'offset': forms.IntegerField(required=False, min_value=0),
        'order': forms.IntegerField(required=False, min_value=0, max_value=3),
    })
    def get(self, request, offset=0, limit=10, order=1):
        """获取用户的关注团队列表

        :param offset: 偏移量
        :param order: 排序方式
            0: 关注时间升序
            1: 关注时间降序（默认值）
            2: 团队名称升序
            3: 团队名称降序
        :return:
            count: 关注的团队总数
            list: 关注的用户列表
                id: 团队ID
                name: 团队昵称
                time_created: 关注时间
        """
        c = request.user.followed_teams.count()
        qs = request.user.followed_teams.order_by(
            self.ORDERS[order])[offset:offset + limit]
        l = [{'id': r.followed.id,
              'name': r.followed.name,
              'time_created': r.time_created} for r in qs]
        return JsonResponse({'count': c, 'list': l})


class FollowedTeam(View):
    @fetch_object(Team.enabled, 'team')
    @require_token
    def get(self, request, team):
        """判断当前用户是否关注了team"""

        if request.user.followed_teams.filter(followed=team).exists():
            abort(200)
        abort(404)

    @fetch_object(Team.enabled, 'team')
    @require_token
    def post(self, request, team):
        """令当前用户关注team"""

        if request.user.followed_teams.filter(follower=team).exists():
            abort(403)
        request.user.followed_teams.create(followed=team)
        abort(200)

    @fetch_object(Team.enabled, 'team')
    @require_token
    def delete(self, request, team):
        """令当前用户取消关注team"""

        qs = request.user.followed_users.filter(followed=team)
        if qs.exists():
            qs.delete()
            abort(200)
        abort(403)


# noinspection PyClassHasNoInit
class Friend(Friend_):
    @fetch_object(User, 'other_user')
    @require_token
    def post(self, request, other_user):
        """将目标用户添加为自己的好友（对方需发送过好友请求）"""

        if not request.user.friend_requests.filter(other_user=other_user) \
                                           .exists():
            abort(403)

        if request.user.firends.filter(other_user=other_user).exists():
            abort(403)

        request.user.friends.create(other_user=other_user)
        other_user.friends.create(other_user=request.user)
        abort(200)

    @fetch_object(User, 'other_user')
    @require_token
    def delete(self, request, other_user):
        """删除好友"""

        if not request.user.friends.filter(other_user=other_user).exists():
            abort(404)

        from ..models import UserFriend
        UserFriend.objects.filter(user=request.user, other_user=other_user) \
                          .delete()
        UserFriend.objects.filter(user=other_user, other_user=request.user) \
                          .delete()
        abort(200)


# noinspection PyClassHasNoInit
class FriendRequestList(View):
    @require_token
    def get(self, request, limit=10):
        """按请求时间逆序获取当前用户收到的的好友请求信息，
        拉取后的请求标记为已读

        :return:
            count: 请求的总条数
            list: 好友请求信息列表
                id: 用户ID
                username: 用户名
                name: 用户昵称
                description: 附带消息
                time_created: 请求发出的时间
        """
        # 拉取好友请求信息
        c = request.user.friend_requests.count()
        qs = request.user.friend_requests.all()[:limit]

        l = [{'id': r.sender.id,
              'username': r.other_user.username,
              'name': r.other_user.name,
              'description': r.description,
              'time_created': r.time_created} for r in qs]
        return JsonResponse({'count': c, 'list': l})

    post_dict = {'description': forms.CharField(required=False, max_length=100)}


class FriendRequest(View):
    @require_token
    def delete(self, request, req_id):
        """忽略某条好友请求"""

        request.user.friend_requests.filter(pk=req_id).delete()
        abort(200)
