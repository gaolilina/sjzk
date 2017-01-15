import re
from django import forms
from django.db import IntegrityError
from django.db import transaction
from django.http import JsonResponse
from django.views.generic import View

from ChuangYi.settings import SERVER_URL, DEFAULT_ICON_URL
from rongcloud import RongCloud
from ..models import User, Team, ActivityUserParticipator, UserValidationCode, \
    Activity, Competition
from ..utils import abort, action, save_uploaded_image, identity_verify
from ..utils.decorators import *
from ..views.user import Icon as Icon_, Profile as Profile_, ExperienceList as \
    ExperienceList_, FriendList, Friend as Friend_


__all__ = ['Username', 'Password', 'Icon', 'IDCard', 'OtherCard', 'Profile',
           'ExperienceList', 'FollowedUserList', 'FollowedUser',
           'FollowedTeamList', 'FollowedTeam', 'FriendList', 'Friend',
           'FriendRequestList', 'FriendRequest', 'LikedUser', 'LikedTeam',
           'LikedActivity', 'LikedCompetition',
           'RelatedTeamList', 'OwnedTeamList', 'InvitationList',
           'Invitation', 'IdentityVerification', 'ActivityList',
           'Feedback', 'InvitationCode', 'BindPhoneNumber']


class Username(View):
    @require_token
    def get(self, request):
        """获取当前用户的用户名"""
        request.user.score += 10
        request.user.save()
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
            # 更改融云上的用户信息
            if not request.user.icon:
                portraitUri = SERVER_URL + request.user.icon
            else:
                portraitUri = DEFAULT_ICON_URL
            rcloud = RongCloud()
            rcloud.User.refresh(
                userId=request.user.id,
                name=request.user.name,
                portraitUri=portraitUri)
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
            if not request.user.icon:
                request.user.score += 50
            request.user.icon = filename
            request.user.save()
            # 用户头像更换后调用融云接口更改融云上的用户头像
            portraitUri = SERVER_URL + request.user.icon
            rcloud = RongCloud()
            rcloud.User.refresh(
                userId=request.user.id,
                name=request.user.name,
                portraitUri=portraitUri)
            return JsonResponse({'icon_url': request.user.icon})
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

        # 等待审核或者已通过审核不能上传照片
        if request.user.is_verified in [1, 2]:
            abort(403)

        id_card = request.FILES.get('image')
        if not id_card:
            abort(400)

        filename = save_uploaded_image(id_card, is_private=True)
        if filename:
            if not request.user.id_card:
                request.user.score += 200
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
            if not request.user.other_card:
                request.user.score += 200
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
        'role': forms.CharField(required=False, max_length=20),
        'other_number': forms.CharField(required=False, max_length=20),
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
            role:
            other_number:
            unit1:
            unit2:
            profession:
        """

        name = kwargs.pop('name', '')
        if len(name) > 0:
            if re.match(r'创易用户 #\w+', name):
                request.user.score += 50
            request.user.name = name
            # 用户昵称更换后调用融云接口更改融云上的用户头像
            if request.user.icon:
                portraitUri = SERVER_URL + request.user.icon
            else:
                portraitUri = DEFAULT_ICON_URL
            rcloud = RongCloud()
            rcloud.User.refresh(
                userId=request.user.id,
                name=request.user.name,
                portraitUri=portraitUri)
        normal_keys = ('description', 'qq', 'wechat', 'email', 'gender',
                       'birthday', 'province', 'city', 'county')
        for k in normal_keys:
            setattr(request.user, k, kwargs[k])

        tags = kwargs.pop('tags', None)
        if tags:
            tags = tags.split('|')[:5]
            with transaction.atomic():
                request.user.tags.all().delete()
                order = 0
                for tag in tags:
                    tag = tag.strip()
                    if tag:
                        request.user.tags.create(name=tag, order=order)
                        order += 1

        role_keys = ('role', 'other_number', 'unit1', 'unit2', 'profession')
        if not request.user.is_role_verified:
            for k in role_keys:
                setattr(request.user, k, kwargs[k])

        request.user.score += 50
        request.user.save()
        abort(200)


# noinspection PyClassHasNoInit
class IdentityVerification(Profile_):
    @require_token
    @validate_args({
        'real_name': forms.CharField(required=False, max_length=20),
        'id_number': forms.CharField(
            required=False, min_length=18, max_length=18),
    })
    def post(self, request, **kwargs):
        """实名认证

        :param kwargs:
            real_name:
            id_number:
        """

        if not request.user.id_card:
            abort(403, 'Please upload the positive and negative of ID card')
        id_keys = ('real_name', 'id_number')
        # 调用第三方接口验证身份证的正确性
        res = identity_verify(kwargs['id_number'])
        error_code = res["error_code"]
        if error_code != 0:
            abort(404, res["reason"])

        if not request.user.is_verified:
            for k in id_keys:
                setattr(request.user, k, kwargs[k])
        request.user.score += 50
        request.user.is_verified = 1
        request.user.save()
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
            profession=kwargs['profession'], degree=kwargs['degree'],
            time_in=kwargs['time_in'], time_out=kwargs['time_out']
        )
        request.user.score += 50
        request.user.save()
        abort(200)

    @require_token
    def delete(self, request, type):
        """删除当前用户某类的所有经历"""

        request.user.experiences.filter(type=type).delete()
        abort(200)


class FollowedUserList(View):
    ORDERS = [
        'time_created', '-time_created',
        'followed__name', '-followed__name',
    ]

    @require_token
    @validate_args({
        'offset': forms.IntegerField(required=False, min_value=0),
        'limit': forms.IntegerField(required=False, min_value=0),
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
                icon_url: 用户头像
                time_created: 关注时间
        """
        c = request.user.followed_users.count()
        qs = request.user.followed_users.order_by(
            self.ORDERS[order])[offset:offset + limit]
        l = [{'id': r.followed.id,
              'username': r.followed.username,
              'name': r.followed.name,
              'icon_url': r.followed.icon,
              'time_created': r.time_created} for r in qs]
        return JsonResponse({'count': c, 'list': l})


class FollowedUser(View):
    @fetch_object(User.enabled, 'user')
    @require_token
    def get(self, request, user):
        """判断当前用户是否关注了user"""

        if request.user.followed_users.filter(followed=user).exists():
            abort(200)
        abort(404)

    @fetch_object(User.enabled, 'user')
    @require_token
    def post(self, request, user):
        """令当前用户关注user"""

        if request.user.followed_users.filter(followed=user).exists():
            abort(403)
        request.user.followed_users.create(followed=user)
        request.user.score += 10
        request.user.save()
        abort(200)

    @fetch_object(User.enabled, 'user')
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
        'time_created', '-time_created',
        'followed__name', '-followed__name',
    ]

    @require_token
    @validate_args({
        'offset': forms.IntegerField(required=False, min_value=0),
        'limit': forms.IntegerField(required=False, min_value=0),
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
                icon_url: 团队头像
                time_created: 关注时间
        """
        c = request.user.followed_teams.count()
        qs = request.user.followed_teams.order_by(
            self.ORDERS[order])[offset:offset + limit]
        l = [{'id': r.followed.id,
              'name': r.followed.name,
              'icon_url': r.followed.icon,
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

        if request.user.followed_teams.filter(followed=team).exists():
            abort(403)
        request.user.followed_teams.create(followed=team)
        request.user.score += 10
        request.user.save()
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
    @fetch_object(User.enabled, 'other_user')
    @require_token
    def post(self, request, other_user):
        """将目标用户添加为自己的好友（对方需发送过好友请求）"""

        if not request.user.friend_requests.filter(other_user=other_user) \
                                           .exists():
            abort(403)

        if request.user.friends.filter(other_user=other_user).exists():
            abort(403)

        request.user.friends.create(other_user=other_user)
        other_user.friends.create(other_user=request.user)
        request.user.friend_requests.filter(other_user=other_user).delete()
        request.user.score += 10
        request.user.save()
        abort(200)

    @fetch_object(User.enabled, 'other_user')
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
    @validate_args({
        'offset': forms.IntegerField(required=False),
        'limit': forms.IntegerField(required=False, min_value=0),
    })
    def get(self, request, offset=0, limit=10):
        """按请求时间逆序获取当前用户收到的的好友请求信息，
        拉取后的请求标记为已读

        :return:
            count: 请求的总条数
            list: 好友请求信息列表
                id: 用户ID
                username: 用户名
                request_id: 申请ID
                name: 用户昵称
                icon_url: 用户头像
                description: 附带消息
                time_created: 请求发出的时间
        """
        # 拉取好友请求信息
        c = request.user.friend_requests.count()
        qs = request.user.friend_requests.all()[offset:offset + limit]

        l = [{'id': r.other_user.id,
              'request_id': r.id,
              'username': r.other_user.username,
              'name': r.other_user.name,
              'icon_url': r.other_user.icon,
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


class LikedEntity(View):
    """与当前用户点赞行为相关的View"""

    @require_token
    def get(self, request, entity):
        """判断当前用户是否对某个对象点过赞"""

        if entity.likers.filter(liker=request.user).exists():
            abort(200)
        abort(404)

    @require_token
    def post(self, request, entity):
        """对某个对象点赞"""

        if not entity.likers.filter(liker=request.user).exists():
            entity.likers.create(liker=request.user)
            request.user.score += 10
            request.user.save()
        abort(200)

    @require_token
    def delete(self, request, entity):
        """对某个对象取消点赞"""

        entity.likers.filter(liker=request.user).delete()
        abort(200)


# noinspection PyMethodOverriding
class LikedUser(LikedEntity):
    @fetch_object(User.enabled, 'user')
    def get(self, request, user):
        return super().get(request, user)

    @fetch_object(User.enabled, 'user')
    def post(self, request, user):
        return super().post(request, user)

    @fetch_object(User.enabled, 'user')
    def delete(self, request, user):
        return super().delete(request, user)


# noinspection PyMethodOverriding
class LikedTeam(LikedEntity):
    @fetch_object(Team.enabled, 'team')
    def get(self, request, team):
        return super().get(request, team)

    @fetch_object(Team.enabled, 'team')
    def post(self, request, team):
        return super().post(request, team)

    @fetch_object(Team.enabled, 'team')
    def delete(self, request, team):
        return super().delete(request, team)


# noinspection PyMethodOverriding
class LikedActivity(LikedEntity):
    @fetch_object(Activity.enabled, 'activity')
    def get(self, request, activity):
        return super().get(request, activity)

    @fetch_object(Activity.enabled, 'activity')
    def post(self, request, activity):
        return super().post(request, activity)

    @fetch_object(Activity.enabled, 'activity')
    def delete(self, request, activity):
        return super().delete(request, activity)


# noinspection PyMethodOverriding
class LikedCompetition(LikedEntity):
    @fetch_object(Competition.enabled, 'competition')
    def get(self, request, competition):
        return super().get(request, competition)

    @fetch_object(Competition.enabled, 'competition')
    def post(self, request, competition):
        return super().post(request, competition)

    @fetch_object(Competition.enabled, 'competition')
    def delete(self, request, competition):
        return super().delete(request, competition)


class RelatedTeamList(View):
    ORDERS = ('team__time_created', '-team__time_created',
              'team__name', '-team__name')

    # noinspection PyUnusedLocal
    @require_token
    @validate_args({
        'offset': forms.IntegerField(required=False, min_value=0),
        'limit': forms.IntegerField(required=False, min_value=0),
        'order': forms.IntegerField(required=False, min_value=0, max_value=3),
    })
    def get(self, request, offset=0, limit=10, order=1):
        """获取当前用户参与的团队列表

        :param offset: 偏移量
        :param limit: 数量上限
        :param order: 排序方式
            0: 注册时间升序
            1: 注册时间降序（默认值）
            2: 昵称升序
            3: 昵称降序
        :return:
            count: 团队总数
            list: 团队列表
                id: 团队ID
                name: 团队名
                icon_url: 团队头像
                owner_id: 创建者ID
                liker_count: 点赞数
                visitor_count: 最近7天访问数
                member_count: 团队成员人数
                fields: 所属领域，格式：['field1', 'field2']
                tags: 标签，格式：['tag1', 'tag2', ...]
                time_created: 注册时间
        """
        i, j, k = offset, offset + limit, self.ORDERS[order]
        c = request.user.teams.count()
        teams = request.user.teams.order_by(k)[i:j]
        l = [{'id': t.team.id,
              'name': t.team.name,
              'icon_url': t.team.icon,
              'owner_id': t.team.owner.id,
              'liker_count': t.team.likers.count(),
              'visitor_count': t.team.visitors.count(),
              'member_count': t.team.members.count(),
              'fields': [t.team.field1, t.team.field2],
              'tags': [tag.name for tag in t.team.tags.all()],
              'time_created': t.team.time_created} for t in teams]
        return JsonResponse({'count': c, 'list': l})


class OwnedTeamList(View):
    ORDERS = ('time_created', '-time_created', 'name', '-name')

    # noinspection PyUnusedLocal
    @require_token
    @validate_args({
        'offset': forms.IntegerField(required=False, min_value=0),
        'limit': forms.IntegerField(required=False, min_value=0),
        'order': forms.IntegerField(required=False, min_value=0, max_value=3),
    })
    def get(self, request, offset=0, limit=10, order=1):
        """获取团队列表

        :param offset: 偏移量
        :param limit: 数量上限
        :param order: 排序方式
            0: 注册时间升序
            1: 注册时间降序（默认值）
            2: 昵称升序
            3: 昵称降序
        :return:
            count: 团队总数
            list: 团队列表
                id: 团队ID
                name: 团队名
                icon_url: 团队头像
                owner_id: 创建者ID
                liker_count: 点赞数
                visitor_count: 最近7天访问数
                member_count: 团队成员人数
                fields: 所属领域，格式：['field1', 'field2']
                tags: 标签，格式：['tag1', 'tag2', ...]
                time_created: 注册时间
        """
        i, j, k = offset, offset + limit, self.ORDERS[order]
        c = request.user.owned_teams.count()
        teams = request.user.owned_teams.order_by(k)[i:j]
        l = [{'id': t.id,
              'name': t.name,
              'icon_url': t.icon,
              'owner_id': t.owner.id,
              'liker_count': t.likers.count(),
              'visitor_count': t.visitors.count(),
              'member_count': t.members.count(),
              'fields': [t.field1, t.field2],
              'tags': [tag.name for tag in t.tags.all()],
              'time_created': t.time_created} for t in teams]
        return JsonResponse({'count': c, 'list': l})


# noinspection PyClassHasNoInit
class InvitationList(View):
    @require_token
    @validate_args({
        'offset': forms.IntegerField(required=False),
        'limit': forms.IntegerField(required=False, min_value=0),
    })
    def get(self, request, offset=0, limit=10):
        """获取当前用户的团队邀请列表

        :param limit: 拉取的数量上限
        :return:
            count: 邀请的总条数
            list:
                id: 团队ID
                name: 团队名称
                icon_url: 团队头像
                description: 附带消息
                time_created: 邀请发出的时间
        """
        from ..models import TeamInvitation
        # 拉取来自团队的邀请信息
        c = TeamInvitation.objects.filter(user=request.user).count()
        qs = TeamInvitation.objects.filter(
            user=request.user)[offset:offset + limit]

        l = [{'id': r.team.id,
              'invitation_id': r.id,
              'name': r.team.name,
              'icon_url': r.team.icon,
              'description': r.description,
              'time_created': r.time_created} for r in qs]
        return JsonResponse({'count': c, 'list': l})


class Invitation(View):
    from ..models import TeamInvitation

    @fetch_object(TeamInvitation.objects, 'invitation')
    @require_token
    def post(self, request, invitation):
        """同意团队的加入邀请并成为团队成员（需收到过加入团队邀请）"""

        if invitation.user != request.user:
            abort(403)

        # 若已是团队成员则不做处理
        if invitation.team.members.filter(user=request.user).exists():
            invitation.delete()
            abort(200)

        # 调用融云接口将用户添加进团队群聊
        rcloud = RongCloud()
        r = rcloud.Group.join(
            userId=request.user.id,
            groupId=invitation.team.id,
            groupName=invitation.team.name)
        if r.result['code'] != 200:
            abort(404, 'add member to group chat failed')

        # 在事务中建立关系，并删除对应的加团队邀请
        with transaction.atomic():
            invitation.team.members.create(user=request.user)
            # 发布用户加入团队动态
            action.join_team(request.user, invitation.team)
            invitation.delete()
            request.user.score += 10
            request.user.save()
        abort(200)

    @fetch_object(TeamInvitation.objects, 'invitation')
    @require_token
    def delete(self, request, invitation):
        """忽略某邀请"""

        if invitation.user != request.user:
            abort(403)

        invitation.delete()
        abort(200)


class ActivityList(View):
    @require_token
    @validate_args({
        'offset': forms.IntegerField(required=False, min_value=0),
        'limit': forms.IntegerField(required=False, min_value=0),
    })
    def get(self, request, offset=0, limit=10):
        """获取用户参加的活动列表"""

        r = ActivityUserParticipator.objects.filter(user=request.user)
        c = r.count()
        qs = r[offset: offset + limit]
        l = [{'id': a.activity.id,
              'name': a.activity.name,
              'time_started': a.activity.time_started,
              'time_ended': a.activity.time_ended,
              'deadline': a.activity.deadline,
              'user_participator_count': a.activity.user_participators.count(),
              'time_created': a.activity.time_created} for a in qs]
        return JsonResponse({'count': c, 'list': l})


class Feedback(View):
    @require_token
    @validate_args({
        'content': forms.CharField(max_length=200),
    })
    def post(self, request, content):
        """用户意见反馈

        :param content: 反馈内容
        :return: 200
        """
        if request.user.feedback.count() == 0:
            request.user.score += 30
            request.user.save()
        request.user.feedback.create(content=content)
        abort(200)


class InvitationCode(View):
    @require_token
    def get(self, request):
        """获取用户自己的邀请码

        :return: invitation_code: 邀请码
        """
        invitation_code = request.user.invitation_code
        return JsonResponse({'invitation_code': invitation_code})


class BindPhoneNumber(View):
    @require_token
    @validate_args({
        'phone_number': forms.CharField(min_length=11, max_length=11),
        'password': forms.CharField(min_length=6, max_length=32),
        'validation_code': forms.CharField(min_length=6, max_length=6),
    })
    def post(self, request, phone_number, password, validation_code):
        """绑定手机号，若成功返回200"""

        if not UserValidationCode.verify(
                request.user.phone_number, validation_code):
            abort(400)

        if not request.user.check_password(password):
            abort(401)

        request.user.phone_number = phone_number
        request.user.save()
        abort(200)
