from django import forms
from django.db import IntegrityError
from django.db import transaction
from django.http import JsonResponse, HttpResponseRedirect
from django.views.generic import View

from ChuangYi.settings import UPLOADED_URL
from util.decorator.auth import app_auth
from util.decorator.param import fetch_object, validate_args
from ..models import *
from ..utils import abort
from util.message import send_message
from ..utils.decorators import *
from ..utils.recommender import calculate_ranking_score

__all__ = ['Icon', 'Profile', 'Screen', 'TeamOwnedList', 'TeamJoinedList', 'ValidationCode',
           'PasswordForgotten', 'ActivityList', 'CompetitionList', 'CompetitionJoinedList']


class Icon(View):
    @fetch_object(User.enabled, 'user')
    def get(self, request, user=None):
        """获取用户头像"""

        user = user or request.user
        if user.icon:
            return HttpResponseRedirect(UPLOADED_URL + user.icon)
        abort(404, '用户未设置头像')


class Profile(View):
    @app_auth
    @fetch_object(User.enabled, 'user', force=False)
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
            province: 所在省
            city: 所在市
            county: 所在区/县
            tag_ids: 标签id，格式：[id1, id2, ...]
            tag_likers: 标签点赞数，格式：[count1, count2, ...]
            tags: 标签，格式：['tag1', 'tag2', ...]
            x_counts 各种计数
                x: follower | followed | friend | liker | visitor
            is_verified: 是否实名，0：未提交，1：待审核，2：身份认证通过，
                3：审核未通过，请重新提交，4：通过Eid认证
            is_role_verified: 是否实名，
                0：未提交，1：待审核，2：审核通过，3：审核未通过，请重新提交
            role: 角色
            adept_field: 擅长领域
            adept_skill: 擅长技能
            expect_role: 期望角色
            follow_field: 关注领域
            follow_skill: 关注技能
            unit1: 机构名（学校或公司等）
            unit2: 二级机构名（学院或部门等）
            profession: 专业
            score: 积分
        """
        user = user

        # 更新访客记录
        # if user != request.user:
        #     UserVisitor.objects.update_or_create(visited=user, visitor=request.user)
        #     record_view_user(request.user, user)

        arr1 = []
        arr2 = []
        arr3 = []
        arr4 = []
        for t in user.tags.all():
            arr1.append(t.id)
            arr2.append(t.name)
            arr3.append(t.likers.count())
            arr4.append(t.likers.filter(liker_id=request.user.id).exists())
        r = {'id': user.id,
             'time_created': user.time_created,
             'name': user.name,
             'real_name': user.real_name,
             'phone': user.phone_number,
             'icon_url': user.icon,
             'description': user.description,
             'email': user.email,
             'gender': user.gender,
             'birthday': user.birthday,
             'province': user.province,
             'city': user.city,
             'county': user.county,
             'tag_ids': arr1,
             'tag_likers': arr3,
             'tag_islike': arr4,
             'tags': arr2,
             'follower_count': user.followers.count(),
             'followed_count': user.followed_users.count() + user.followed_teams.count(),
             'friend_count': user.friends.count(),
             'liker_count': user.likers.count(),
             'visitor_count': user.visitors.count(),
             'is_verified': user.is_verified,
             'is_role_verified': user.is_role_verified,
             'role': user.role,
             'adept_field': user.adept_field,
             'adept_skill': user.adept_skill,
             'expect_role': user.expect_role,
             'follow_field': user.follow_field,
             'follow_skill': user.follow_skill,
             'follow': user.follow,
             'goodat': user.goodat,
             'unit1': user.unit1,
             'unit2': user.unit2,
             'profession': user.profession,
             'score': user.score}
        return JsonResponse(r)


class Screen(View):
    ORDERS = ('time_created', '-time_created', 'name', '-name')

    @validate_args({
        'offset': forms.IntegerField(required=False, min_value=0),
        'limit': forms.IntegerField(required=False, min_value=0),
        'order': forms.IntegerField(required=False, min_value=0, max_value=3),
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
        筛选用户

        :param offset: 偏移量
        :param limit: 数量上限
        :param order: 排序方式（若无则进行个性化排序）
            0: 注册时间升序
            1: 注册时间降序
            2: 昵称升序
            3: 昵称降序
        :param kwargs: 搜索条件
            name: 用户名包含字段
            gender: 性别
            province: 省
            city: 市
            county: 区/县
            role: 角色
            unit1: 机构

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
                is_verified: 是否通过实名认证
                is_role_verified: 是否通过身份认证
                time_created: 注册时间
        """
        users = User.enabled

        i, j = offset, offset + limit
        name = kwargs.pop('name', '')
        if name:
            # 按用户昵称段检索
            users = users.filter(name__icontains=name)

        gender = kwargs.pop('gender', None)
        if gender is not None:
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
        if role:
            # 按角色筛选
            users = users.filter(role=role)
        unit1 = kwargs.pop('unit1', '')
        if unit1:
            # 按机构筛选
            users = users.filter(unit1=unit1)

        users = users.all()
        c = users.count()
        if order is not None:
            users = users.order_by(self.ORDERS[order])[i:j]
        else:
            # 将结果进行个性化排序
            user_list = list()
            for u in users:
                if fetch_user_by_token(request):
                    user_list.append((u, calculate_ranking_score(request.user, u)))
                else:
                    user_list.append((u, 0))
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
              'is_verified': u.is_verified,
              'is_role_verified': u.is_role_verified,
              'time_created': u.time_created} for u in users]
        return JsonResponse({'count': c, 'list': l})


class TeamOwnedList(View):
    ORDERS = ('time_created', '-time_created',
              'name', '-name')

    @fetch_object(User.enabled, 'user')
    @app_auth
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
        c = Team.enabled.filter(owner=user).count()
        teams = Team.enabled.filter(owner=user).order_by(k)[i:j]
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


class TeamJoinedList(View):
    ORDERS = ('team__time_created', '-team__time_created',
              'team__name', '-team__name')

    @fetch_object(User.enabled, 'user')
    @app_auth
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
        qs = user.teams.order_by(k)[i:j]
        l = [{'id': t.team.id,
              'name': t.team.name,
              'icon_url': t.team.icon,
              'owner_id': t.team.owner.id,
              'liker_count': t.team.likers.count(),
              'visitor_count': t.team.visitors.count(),
              'member_count': t.team.members.count(),
              'fields': [t.team.field1, t.team.field2],
              'tags': [tag.name for tag in t.team.tags.all()],
              'time_created': t.team.time_created} for t in qs]
        return JsonResponse({'count': c, 'list': l})


class ActivityList(View):
    ORDERS = ('time_created', '-time_created', 'name', '-name')

    @fetch_object(User.enabled, 'user')
    @app_auth
    @validate_args({
        'offset': forms.IntegerField(required=False, min_value=0),
        'limit': forms.IntegerField(required=False, min_value=0),
        'order': forms.IntegerField(required=False, min_value=0,
                                    max_value=3),
    })
    def get(self, request, user, offset=0, limit=10, order=1):
        """获取当前用户参加的活动列表

        :param offset: 偏移量
        :param limit: 数量上限
        :param order: 排序方式
            0: 注册时间升序
            1: 注册时间降序（默认值）
            2: 昵称升序
            3: 昵称降序

        :return:
            count: 活动总数
            list: 活动列表
                id: 活动ID
                name: 活动名
                liker_count: 点赞数
                status: 竞赛当前阶段
                time_started: 开始时间
                time_ended: 结束时间
                deadline: 截止时间
                user_participator_count: 已报名人数
                time_created: 创建时间
        """

        k = self.ORDERS[order]
        c = user.activities.count()
        qs = user.activities.order_by(k)[offset: offset + limit]
        l = [{'id': a.activity.id,
              'name': a.activity.name,
              'liker_count': a.activity.likers.count(),
              'status': a.activity.get_current_state(),
              'time_started': a.activity.time_started,
              'time_ended': a.activity.time_ended,
              'deadline': a.activity.deadline,
              'user_participator_count': a.activity.user_participators.count(),
              'time_created': a.activity.time_created} for a in qs]
        return JsonResponse({'count': c, 'list': l})


class CompetitionList(View):
    ORDERS = ('time_created', '-time_created', 'name', '-name')

    @fetch_object(User.enabled, 'user')
    @app_auth
    @validate_args({
        'offset': forms.IntegerField(required=False, min_value=0),
        'limit': forms.IntegerField(required=False, min_value=0),
        'order': forms.IntegerField(required=False, min_value=0,
                                    max_value=3),
    })
    def get(self, request, user, offset=0, limit=10, order=1):
        """获取用户参加的竞赛列表

        :param offset: 偏移量
        :param limit: 数量上限
        :param order: 排序方式
            0: 注册时间升序
            1: 注册时间降序（默认值）
            2: 昵称升序
            3: 昵称降序

        :return:
            count: 竞赛总数
            list: 竞赛列表
                id: 竞赛ID
                name: 竞赛名
                liker_count: 点赞数
                status: 竞赛当前阶段
                time_started: 开始时间
                time_ended: 结束时间
                deadline: 截止时间
                team_participator_count: 已报名人数
                time_created: 创建时间
        """

        k = self.ORDERS[order]
        ctp = CompetitionTeamParticipator.objects.filter(
            team__members__user=user).distinct()
        qs = ctp.order_by(k)[offset: offset + limit]
        c = ctp.count()
        l = [{'id': a.competition.id,
              'name': a.competition.name,
              'team_name': a.team.name,
              'liker_count': a.competition.likers.count(),
              'status': a.competition.status,
              'time_started': a.competition.time_started,
              'time_ended': a.competition.time_ended,
              'deadline': a.competition.deadline,
              'team_participator_count':
                  a.competition.team_participators.count(),
              'time_created': a.competition.time_created
              } for a in qs]
        return JsonResponse({'count': c, 'list': l})


class CompetitionJoinedList(View):
    ORDERS = ('time_created', '-time_created', 'name', '-name')

    @fetch_object(User.enabled, 'user')
    @app_auth
    @validate_args({
        'offset': forms.IntegerField(required=False, min_value=0),
        'limit': forms.IntegerField(required=False, min_value=0),
        'order': forms.IntegerField(required=False, min_value=0,
                                    max_value=3),
    })
    def get(self, request, user, offset=0, limit=10, order=1):
        """获取用户参加的竞赛列表

        :param offset: 偏移量
        :param limit: 数量上限
        :param order: 排序方式
            0: 注册时间升序
            1: 注册时间降序（默认值）
            2: 昵称升序
            3: 昵称降序

        :return:
            count: 竞赛总数
            list: 竞赛列表
                id: 竞赛ID
                name: 竞赛名
                liker_count: 点赞数
                status: 竞赛当前阶段
                time_started: 开始时间
                time_ended: 结束时间
                deadline: 截止时间
                team_participator_count: 已报名人数
                time_created: 创建时间
        """

        k = self.ORDERS[order]
        ctp = Competition.objects.filter(experts=user)
        qs = ctp.order_by(k)[offset: offset + limit]
        c = ctp.count()
        l = [{'id': a.id,
              'name': a.name,
              'liker_count': a.likers.count(),
              'status': a.status,
              'time_started': a.time_started,
              'time_ended': a.time_ended,
              'deadline': a.deadline,
              'team_participator_count':
                  a.team_participators.count(),
              'time_created': a.time_created
              } for a in qs]
        return JsonResponse({'count': c, 'list': l})

    @fetch_object(User.enabled, 'user')
    @app_auth
    @validate_args({
        'competition_id': forms.IntegerField(),
    })
    def post(self, request, user, competition_id):
        ctp = Competition.objects.filter(pk=competition_id).get()
        ctp.experts.add(user)
        abort(200)


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
            abort(400, '手机号码格式不正确')
        code = UserValidationCode.generate(phone_number)
        tpl_value = "#code#=" + code

        send_message(phone_number, tpl_value)
        abort(200)


class PasswordForgotten(View):
    @validate_args({
        'phone_number': forms.CharField(min_length=11, max_length=11),
        'password': forms.CharField(min_length=6, max_length=32),
        'validation_code': forms.CharField(min_length=6, max_length=6),
    })
    def post(self, request, phone_number, password, validation_code):
        """忘记密码，若成功返回用户令牌
        :param phone_number: 手机号
        :param password: 新的密码
        :param validation_code: 手机号收到的验证码

        :return token
        """

        if not UserValidationCode.verify(phone_number, validation_code):
            abort(400, '验证码错误')

        with transaction.atomic():
            try:
                user = User.enabled.get(phone_number=phone_number)
                user.set_password(password)
                user.save()
                return JsonResponse({'token': user.token})
            except IntegrityError:
                abort(403, '修改密码失败')
