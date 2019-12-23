from django import forms
from django.db import IntegrityError, transaction
from django.http import JsonResponse
from django.views.generic import View

from im.huanxin import update_nickname, update_password
from main.models import User
from main.utils import abort, save_uploaded_image, get_score_stage
from main.utils.dfa import check_bad_words
from main.views.user import Icon as Icon_
from util.base.view import BaseView
from util.decorator.auth import app_auth
from util.decorator.param import validate_args


class Username(View):
    @app_auth
    def get(self, request):
        """获取当前用户的用户名"""

        request.user.save()
        return JsonResponse({'username': request.user.username})

    @app_auth
    @validate_args({
        'username': forms.RegexField(r'^[a-zA-Z0-9_]{4,15}$', strip=True)
    })
    def post(self, request, username):
        """
        设置当前用户的用户名，存储时字母转换成小写，只能设置一次

        :param username: 用户名
        """

        if request.user.username:
            abort(403, '用户名已经设置过')

        if username.isdigit():
            abort(400, '用户名格式错误')

        try:
            request.user.username = username.lower()
            request.user.save()
            return JsonResponse({'username': request.user.username})
        except IntegrityError:
            abort(403, '用户名已存在')


class Password(View):
    @app_auth
    @validate_args({
        'new_password': forms.CharField(min_length=6, max_length=20),
        'old_password': forms.CharField(min_length=6, max_length=20),
    })
    def post(self, request, old_password, new_password):
        """修改密码

        :param old_password: 旧密码
        :param new_password: 新密码（6-20位）

        """
        user = request.user
        if not user.check_password(old_password):
            abort(403, '旧密码错误')
        user.set_password(new_password)
        result = update_password(user.phone_number, user.password)
        if result == 404:
            abort(404, 'user not found')
        user.save()
        abort(200)


class Icon(Icon_):
    @app_auth
    def post(self, request):
        """上传用户头像"""

        icon = request.FILES.get('image')
        if not icon:
            abort(400, '头像上传失败')

        filename = save_uploaded_image(icon)
        if filename:
            if not request.user.icon:
                request.user.score += get_score_stage(3)
                request.user.score_records.create(
                    score=get_score_stage(3), type="初始数据",
                    description="首次上传头像")
            request.user.icon = filename
            request.user.save()
            return JsonResponse({'icon_url': request.user.icon})
        abort(400, '头像保存失败')


class Getui(View):
    @app_auth
    @validate_args({
        'client_id': forms.CharField(max_length=50),
    })
    def post(self, request, client_id):
        """上传个推ID"""
        request.user.getui_id = client_id
        request.user.save()
        abort(200)


class Profile(BaseView):

    @app_auth
    def get(self, request, **kwargs):
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
        user = request.user

        # 更新访客记录
        # if user != request.user:
        #     UserVisitor.objects.update_or_create(visited=user, visitor=request.user)
        #     record_view_user(request.user, user)

        arr1 = []
        arr2 = []
        arr3 = []
        for t in user.tags.all():
            arr1.append(t.id)
            arr2.append(t.name)
            arr3.append(t.likers.count())
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
             'goodat': user.goodat,
             'follow': user.follow,
             'unit1': user.unit1,
             'unit2': user.unit2,
             'profession': user.profession,
             'score': user.score}
        return JsonResponse(r)

    @app_auth
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
        'adept_field': forms.CharField(required=False, max_length=20),
        'adept_skill': forms.CharField(required=False, max_length=20),
        'expect_role': forms.CharField(required=False, max_length=20),
        'follow_field': forms.CharField(required=False, max_length=20),
        'follow_skill': forms.CharField(required=False, max_length=20),
        'other_number': forms.CharField(required=False, max_length=20),
        'unit1': forms.CharField(required=False, max_length=20),
        'unit2': forms.CharField(required=False, max_length=20),
        'profession': forms.CharField(required=False, max_length=20),
        'goodat': forms.CharField(required=False, max_length=256),
        'follow': forms.CharField(required=False, max_length=256),
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
            adept_field: 擅长领域
            adept_skill: 擅长技能
            expect_role: 期望角色
            follow_field: 关注领域
            follow_skill: 关注技能
            other_number:
            unit1:
            unit2:
            profession:
        """

        name = kwargs.pop('name', '')
        user = request.user
        if len(name) > 0:
            # 昵称唯一性验证
            if User.enabled.filter(name=name).exclude(
                    id=user.id).count() != 0:
                abort(403, '昵称已存在')
            # 昵称非法词验证
            if check_bad_words(name):
                abort(403, '昵称含非法词汇')
            # 首次修改昵称增加积分
            if (user.name == "创易汇用户 #" + str(user.id)) and \
                    (user.name != name):
                user.score += get_score_stage(3)
                user.score_records.create(
                    score=get_score_stage(3), type="初始数据",
                    description="首次更换昵称")
            user.name = name
            update_nickname(user.phone_number, name)
        normal_keys = ('description', 'qq', 'wechat', 'email', 'gender',
                       'birthday', 'province', 'city', 'county', 'adept_field',
                       'adept_skill', 'expect_role', 'follow_field',
                       'follow_skill', 'goodat', 'follow')
        for k in normal_keys:
            if k in kwargs:
                setattr(user, k, kwargs[k])

        tags = kwargs.pop('tags', None)
        if tags:
            tags = tags.split('|')[:5]
            with transaction.atomic():
                user.tags.all().delete()
                order = 0
                for tag in tags:
                    tag = tag.strip()
                    if tag:
                        user.tags.create(name=tag, order=order)
                        order += 1

        role_keys = ('role', 'other_number', 'unit1', 'unit2', 'profession')
        if not user.is_role_verified:
            for k in role_keys:
                if k in kwargs:
                    setattr(user, k, kwargs[k])

        user.save()
        abort(200)
