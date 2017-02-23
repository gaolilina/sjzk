from django import forms
from django.db import IntegrityError
from django.http import JsonResponse, HttpResponseRedirect
from django.db import transaction
from django.views.generic import View
from rongcloud import RongCloud

from ChuangYi.settings import UPLOADED_URL, SERVER_URL, DEFAULT_ICON_URL
from ..utils import abort, get_score_stage
from ..utils.decorators import *
from ..utils.recommender import calculate_ranking_score, record_view_user
from ..models import User, UserVisitor, UserExperience, UserValidationCode, Team


__all__ = ['List', 'Token', 'Icon', 'Profile', 'ExperienceList', 'Experience',
           'FriendList', 'Friend', 'FriendRequestList', 'Search', 'Screen',
           'TeamOwnedList', 'TeamJoinedList', 'ValidationCode',
           'PasswordForgotten']


class List(View):
    ORDERS = ('time_created', '-time_created', 'name', '-name')

    @require_token
    @validate_args({
        'offset': forms.IntegerField(required=False, min_value=0),
        'limit': forms.IntegerField(required=False, min_value=0),
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
                icon_url: 用户头像
                tags: 标签
                gender: 性别
                liker_count: 点赞数
                follower_count: 粉丝数
                visitor_count: 访问数
                is_verified: 是否通过实名认证
        """
        c = User.enabled.count()
        users = User.enabled.order_by(self.ORDERS[order])[offset:offset + limit]
        l = [{'id': u.id,
              'time_created': u.time_created,
              'username': u.username,
              'name': u.name,
              'icon_url': u.icon,
              'tags': [tag.name for tag in u.tags.all()],
              'gender': u.gender,
              'liker_count': u.likers.count(),
              'follower_count': u.followers.count(),
              'visitor_count': u.visitors.count(),
              'is_verified': u.is_verified} for u in users]
        return JsonResponse({'count': c, 'list': l})

    @validate_args({
        'phone_number': forms.CharField(min_length=11, max_length=11),
        'password': forms.CharField(min_length=6, max_length=32),
        'validation_code': forms.CharField(min_length=6, max_length=6),
        'invitation_code': forms.CharField(
            min_length=8, max_length=8, required=False),
    })
    def post(self, request, phone_number, password, validation_code,
             invitation_code=None):
        """注册，若成功返回用户令牌"""

        if not UserValidationCode.verify(phone_number, validation_code):
            abort(400)

        with transaction.atomic():
            try:
                user = User(phone_number=phone_number)
                user.set_password(password)
                # user.update_token()
                user.save_and_generate_name()
                user.create_invitation_code()
                # 注册成功后给融云服务器发送请求获取Token
                rcloud = RongCloud()
                r = rcloud.User.getToken(
                    userId=user.id, name=user.name,
                    portraitUri=DEFAULT_ICON_URL)
                token = r.result['token']
                user.token = token
                if invitation_code:
                    u = User.enabled.filter(invitation_code=invitation_code)
                    if not u:
                        abort(404, 'error invitation code!')
                    user.used_invitation_code = invitation_code
                    u.score_records.create(
                        score=get_score_stage(4), type="活跃度",
                        description="邀请码被使用")
                # 加积分
                user.score += get_score_stage(3)
                user.score_records.create(
                    score=get_score_stage(3), type="初始数据",
                    description="首次手机号注册")
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
                portraitUri = SERVER_URL + user.icon
            else:
                portraitUri = DEFAULT_ICON_URL
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
            name: 昵称
            icon_url: 头像
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
            score: 积分
            id_number:
            other_number:
        """
        user = user or request.user

        # 更新访客记录
        if user != request.user:
            UserVisitor.objects \
                .update_or_create(visited=user, visitor=request.user)
            record_view_user(request.user, user)

        r = {'id': user.id,
             'time_created': user.time_created,
             'name': user.name,
             'icon_url': user.icon,
             'description': user.description,
             'email': user.email,
             'gender': user.gender,
             'birthday': user.birthday,
             'province': user.province,
             'city': user.city,
             'county': user.county,
             'tags': [tag.name for tag in user.tags.all()],
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
             'profession': user.profession,
             'score': user.score,
             'id_number': user.id_number,
             'other_number': user.other_number}
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

        c = user.experiences.filter(type=type).count()
        l = [{'id': e.id,
              'description': e.description,
              'unit': e.unit,
              'profession': e.profession,
              'degree': e.degree,
              'time_in': e.time_in,
              'time_out': e.time_out,
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
        exp.save()
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
        'limit': forms.IntegerField(required=False, min_value=0),
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
                icon_url: 用户头像
                time_created: 成为好友时间
        """
        user = user or request.user

        c = user.friends.count()
        qs = user.friends.order_by(self.ORDERS[order])[offset:offset + limit]
        l = [{'id': r.other_user.id,
              'username': r.other_user.username,
              'name': r.other_user.name,
              'icon_url': r.other_user.icon,
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
        'limit': forms.IntegerField(required=False, min_value=0),
        'order': forms.IntegerField(required=False, min_value=0, max_value=3),
        'by_tag': forms.IntegerField(required=False),
        'name': forms.CharField(max_length=20),
    })
    def get(self, request, name, offset=0, limit=10, order=None, by_tag=0):
        """
        搜索用户

        :param offset: 偏移量
        :param limit: 数量上限
        :param order: 排序方式（若无则进行个性化排序）
            0: 注册时间升序
            1: 注册时间降序
            2: 昵称升序
            3: 昵称降序
        :param name: 用户名包含字段
        :param by_tag: 是否按标签检索

        :return:
            count: 用户总数
            list: 用户列表
                id: 用户ID
                name: 用户昵称
                icon_url: 用户头像
                gender: 性别
                like_count: 点赞数
                follower_count: 粉丝数
                followed_count: 关注的实体数
                visitor_count: 访问数
                tags: 标签
                time_created: 注册时间
        """
        i, j = offset, offset + limit
        if by_tag == 0:
            # 按用户昵称段检索
            users = User.enabled.filter(name__contains=name)
        else:
            # 按标签检索
            users = User.enabled.filter(tags__name=name)
        c = users.count()
        if order is not None:
            users = users.order_by(self.ORDERS[order])[i:j]
        else:
            # 将结果进行个性化排序
            user_list = list()
            for u in users:
                user_list.append((u, calculate_ranking_score(request.user, u)))
            user_list = sorted(user_list, key=lambda x: x[1], reverse=True)
            users = (u[0] for u in user_list[i:j])
        l = [{'id': u.id,
              'name': u.name,
              'gender': u.gender,
              'like_count': u.likers.count(),
              'follower_count': u.followers.count(),
              'followed_count': u.followed_users.count() + u.followed_teams.count(),
              'visitor_count': u.visitors.count(),
              'icon_url': u.icon,
              'tags': [tag.name for tag in u.tags.all()],
              'time_created': u.time_created} for u in users]
        return JsonResponse({'count': c, 'list': l})


class Screen(View):
    ORDERS = ('time_created', '-time_created', 'name', '-name')

    @require_token
    @validate_args({
        'offset': forms.IntegerField(required=False, min_value=0),
        'limit': forms.IntegerField(required=False, min_value=0),
        'order': forms.IntegerField(required=False, min_value=0, max_value=3),
        'by_tag': forms.IntegerField(required=False),
        'name': forms.CharField(required=False, max_length=20),
        'gender': forms.IntegerField(required=False, min_value=0, max_value=2),
        'province': forms.CharField(required=False, max_length=20),
        'city': forms.CharField(required=False, max_length=20),
        'county': forms.CharField(required=False, max_length=20),
        'role': forms.CharField(required=False, max_length=20),
        'unit1': forms.CharField(required=False, max_length=20),
    })
    def get(self, request, offset=0, limit=10, order=None, **kwargs):
        """
        搜索用户

        :param offset: 偏移量
        :param limit: 数量上限
        :param order: 排序方式（若无则进行个性化排序）
            0: 注册时间升序
            1: 注册时间降序
            2: 昵称升序
            3: 昵称降序
        :param name: 用户名包含字段
        :param gender: 性别
        :param province: 省
        :param city: 市
        :param county: 区/县
        :param role: 角色
        :param unit1: 机构

        :return:
            count: 用户总数
            list: 用户列表
                id: 用户ID
                name: 用户昵称
                icon_url: 用户头像
                gender: 性别
                like_count: 点赞数
                follower_count: 粉丝数
                followed_count: 关注的实体数
                visitor_count: 访问数
                tags: 标签
                time_created: 注册时间
        """
        if kwargs:
            users = User.enabled
        else:
            users = User.enabled.all()

        i, j = offset, offset + limit
        name = kwargs.pop('name', '')
        if name:
            # 按用户昵称段检索
            users = users.filter(name__contains=name)

        gender = kwargs.pop('gender', '')
        if gender:
            # 按性别筛选
            users = users.filter(gender=gender)
        province = kwargs.pop('province', '')
        if province:
            # 按省会筛选
            users = users.filter(province=province)
        city = kwargs.pop('city', '')
        if city:
            # 按城市筛选
            users = users.filter(city=city)
        county = kwargs.pop('county', '')
        if county:
            # 按区/县筛选
            users = users.filter(county=county)
        role = kwargs.pop('role', '')
        if province:
            # 按角色筛选
            users = users.filter(role=role)
        unit1 = kwargs.pop('unit1', '')
        if unit1:
            # 按机构筛选
            users = users.filter(unit1=unit1)

        c = users.count()
        if order is not None:
            users = users.order_by(self.ORDERS[order])[i:j]
        else:
            # 将结果进行个性化排序
            user_list = list()
            for u in users:
                user_list.append((u, calculate_ranking_score(request.user, u)))
            user_list = sorted(user_list, key=lambda x: x[1], reverse=True)
            users = (u[0] for u in user_list[i:j])
        l = [{'id': u.id,
              'name': u.name,
              'gender': u.gender,
              'like_count': u.likers.count(),
              'follower_count': u.followers.count(),
              'followed_count': u.followed_users.count() + u.followed_teams.count(),
              'visitor_count': u.visitors.count(),
              'icon_url': u.icon,
              'tags': [tag.name for tag in u.tags.all()],
              'time_created': u.time_created} for u in users]
        return JsonResponse({'count': c, 'list': l})


class TeamOwnedList(View):
    ORDERS = ('team__time_created', '-team__time_created',
              'team__name', '-team__name')

    @fetch_object(User.enabled, 'user')
    @require_token
    @validate_args({
        'offset': forms.IntegerField(required=False, min_value=0),
        'limit': forms.IntegerField(required=False, min_value=0),
        'order': forms.IntegerField(required=False, min_value=0, max_value=3),
    })
    def get(self, request, user, offset=0, limit=10, order=1):
        """获取某用户创建的团队列表

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
        teams = Team.enabled.filter(owner=user)
        c = teams.count()
        l = [{'id': t.team.id,
              'name': t.team.name,
              'icon_url': t.team.icon,
              'owner_id': t.team.owner.id,
              'liker_count': t.team.likers.count(),
              'visitor_count': t.team.visitors.count(),
              'member_count': t.team.members.count(),
              'fields': [t.team.field1, t.team.field2],
              'tags': [tag.name for tag in t.team.tags.all()],
              'time_created': t.team.time_created} for t in teams.order_by(
                k)[i:j]]
        return JsonResponse({'count': c, 'list': l})


class TeamJoinedList(View):
    ORDERS = ('team__time_created', '-team__time_created',
              'team__name', '-team__name')

    @fetch_object(User.enabled, 'user')
    @require_token
    @validate_args({
        'offset': forms.IntegerField(required=False, min_value=0),
        'limit': forms.IntegerField(required=False, min_value=0),
        'order': forms.IntegerField(required=False, min_value=0, max_value=3),
    })
    def get(self, request, user, offset=0, limit=10, order=1):
        """获取某用户参加的团队列表

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
        c = user.teams.count()
        teams = user.teams.order_by(k)[i:j]
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


class ValidationCode(View):
    @validate_args({
        'phone_number': forms.CharField(min_length=11, max_length=11),
    })
    def get(self, request, phone_number):
        """获取验证码
        :param phone_number: 手机号
        :return validation_code: 验证码
        """

        if not phone_number.isdigit():
            abort(400)
        code = UserValidationCode.generate(phone_number)
        data = {"mobile": phone_number,
                "content": "您本次的验证码为：" +
                           code + "，如非本人操作，请忽略！【创易】"}
        # send_message(data)
        return JsonResponse({
            'validation_code': code,
        })


class PasswordForgotten(View):
    @validate_args({
        'phone_number': forms.CharField(min_length=11, max_length=11),
        'password': forms.CharField(min_length=6, max_length=32),
        'validation_code': forms.CharField(min_length=6, max_length=6),
    })
    def post(self, request, phone_number, password, validation_code):
        """忘记密码，若成功返回用户令牌
        :param phone_number: 新手机号
        :param password: 密码
        :param validation_code: 新手机号收到的验证码

        :return token
        """

        if not UserValidationCode.verify(phone_number, validation_code):
            abort(400)

        with transaction.atomic():
            try:
                user = User.enabled.get(phone_number=phone_number)
                user.set_password(password)
                user.save()
                return JsonResponse({'token': user.token})
            except IntegrityError:
                abort(403)
