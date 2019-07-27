from django import forms
from django.db import IntegrityError
from django.db import transaction
from django.http import JsonResponse
from django.views.generic import View

from main.models.need import TeamNeed
from util.base.view import BaseView
from util.decorator.auth import app_auth
from util.decorator.param import validate_args, fetch_object
from ..models import *
from ..utils import abort, save_uploaded_image, get_score_stage
from ..utils import action
from ..utils.decorators import *
from ..utils.dfa import check_bad_words
from ..utils.recommender import record_like_user, record_like_team
from ..views.user import Icon as Icon_, ExperienceList as \
    ExperienceList_


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
        if request.user.check_password(old_password):
            request.user.set_password(new_password)
            request.user.save()
            abort(200)
        abort(403, '旧密码错误')


# noinspection PyClassHasNoInit
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


# noinspection PyClassHasNoInit
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
        if len(name) > 0:
            # 昵称唯一性验证
            if User.enabled.filter(name=name).exclude(
                    id=request.user.id).count() != 0:
                abort(403, '昵称已存在')
            # 昵称非法词验证
            if check_bad_words(name):
                abort(403, '昵称含非法词汇')
            # 首次修改昵称增加积分
            if (request.user.name == "创易汇用户 #" + str(request.user.id)) and \
                    (request.user.name != name):
                request.user.score += get_score_stage(3)
                request.user.score_records.create(
                    score=get_score_stage(3), type="初始数据",
                    description="首次更换昵称")
            request.user.name = name
        normal_keys = ('description', 'qq', 'wechat', 'email', 'gender',
                       'birthday', 'province', 'city', 'county', 'adept_field',
                       'adept_skill', 'expect_role', 'follow_field',
                       'follow_skill')
        for k in normal_keys:
            if k in kwargs:
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
                if k in kwargs:
                    setattr(request.user, k, kwargs[k])

        request.user.save()
        abort(200)


# noinspection PyClassHasNoInit,PyShadowingBuiltins
class ExperienceList(ExperienceList_):
    @app_auth
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

        if check_bad_words(kwargs['description']):
            abort(403, '含有非法词汇')
        request.user.experiences.create(
            type=type, description=kwargs['description'], unit=kwargs['unit'],
            profession=kwargs['profession'], degree=kwargs['degree'],
            time_in=kwargs['time_in'], time_out=kwargs['time_out']
        )
        request.user.score += get_score_stage(3)
        request.user.score_records.create(
            score=get_score_stage(3), type="活跃度", description="增加一条经历")
        request.user.save()
        abort(200)

    @app_auth
    def delete(self, request, type):
        """删除当前用户某类的所有经历"""

        request.user.experiences.filter(type=type).delete()
        abort(200)


class FollowedUserList(View):
    ORDERS = [
        'time_created', '-time_created',
        'followed__name', '-followed__name',
    ]

    @app_auth
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
    @app_auth
    @fetch_object(User.enabled, 'user')
    def get(self, request, user):
        """判断当前用户是否关注了user"""

        if request.user.followed_users.filter(followed=user).exists():
            abort(200)
        abort(404, '未关注该用户')

    @app_auth
    @fetch_object(User.enabled, 'user')
    def post(self, request, user):
        """令当前用户关注user"""

        if request.user.followed_users.filter(followed=user).exists():
            abort(403, '已经关注过')
        request.user.followed_users.create(followed=user)
        # 积分
        request.user.score += get_score_stage(1)
        request.user.score_records.create(
            score=get_score_stage(1), type="活跃度", description="增加关注")
        user.score += get_score_stage(1)
        user.score_records.create(
            score=get_score_stage(1), type="受欢迎度", description="被关注")
        request.user.save()
        user.save()
        abort(200)

    @app_auth
    @fetch_object(User.enabled, 'user')
    def delete(self, request, user):
        """令当前用户取消关注user"""

        qs = request.user.followed_users.filter(followed=user)
        if qs.exists():
            # 积分
            request.user.score -= get_score_stage(1)
            request.user.score_records.create(
                score=-get_score_stage(1), type="活跃度", description="取消关注")
            user.score -= get_score_stage(1)
            user.score_records.create(
                score=-get_score_stage(1), type="受欢迎度",
                description="被关注取消")
            request.user.save()
            user.save()
            qs.delete()
            abort(200)
        abort(403, '未关注过该用户')


class FollowedTeamList(View):
    ORDERS = [
        'time_created', '-time_created',
        'followed__name', '-followed__name',
    ]

    @app_auth
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
    @app_auth
    @fetch_object(Team.enabled, 'team')
    def get(self, request, team):
        """判断当前用户是否关注了team"""

        if request.user.followed_teams.filter(followed=team).exists():
            abort(200)
        abort(404, '未关注该团队')

    @app_auth
    @fetch_object(Team.enabled, 'team')
    def post(self, request, team):
        """令当前用户关注team"""

        if request.user.followed_teams.filter(followed=team).exists():
            abort(403, '已经关注过该团队')
        request.user.followed_teams.create(followed=team)
        request.user.score += get_score_stage(1)
        request.user.score_records.create(
            score=get_score_stage(1), type="活跃度", description="增加一个关注")
        team.score += get_score_stage(1)
        team.score_records.create(
            score=get_score_stage(1), type="受欢迎度", description="增加一个关注")
        request.user.save()
        team.save()
        abort(200)

    @app_auth
    @fetch_object(Team.enabled, 'team')
    def delete(self, request, team):
        """令当前用户取消关注team"""

        qs = request.user.followed_teams.filter(followed=team)
        if qs.exists():
            # 积分
            request.user.score -= get_score_stage(1)
            request.user.score_records.create(
                score=-get_score_stage(1), type="活跃度",
                description="取消关注")
            team.score -= get_score_stage(1)
            team.score_records.create(
                score=-get_score_stage(1), type="受欢迎度",
                description="取消关注")
            request.user.save()
            team.save()
            qs.delete()
            abort(200)
        abort(403, '未关注过该团队')


class FollowedLabList(View):
    ORDERS = [
        'time_created', '-time_created',
        'followed__name', '-followed__name',
    ]

    @app_auth
    @validate_args({
        'offset': forms.IntegerField(required=False, min_value=0),
        'limit': forms.IntegerField(required=False, min_value=0),
        'order': forms.IntegerField(required=False, min_value=0, max_value=3),
    })
    def get(self, request, offset=0, limit=10, order=1):
        c = request.user.followed_labs.count()
        qs = request.user.followed_labs.order_by(
            self.ORDERS[order])[offset:offset + limit]
        l = [{'id': r.followed.id,
              'name': r.followed.name,
              'icon_url': r.followed.icon,
              'time_created': r.time_created} for r in qs]
        return JsonResponse({'count': c, 'list': l})


class FollowedLab(View):
    @app_auth
    @fetch_object(Lab.enabled, 'Lab')
    def get(self, request, lab):
        """判断当前用户是否关注了team"""

        if request.user.followed_labs.filter(followed=lab).exists():
            abort(200)
        abort(404, '未关注该实验室')

    @app_auth
    @fetch_object(Lab.enabled, 'lab')
    def post(self, request, lab):
        if request.user.followed_labs.filter(followed=lab).exists():
            abort(403, '已经关注过该实验室')
        request.user.followed_labs.create(followed=lab)
        request.user.score += get_score_stage(1)
        request.user.score_records.create(
            score=get_score_stage(1), type="活跃度", description="增加一个关注")
        lab.score += get_score_stage(1)
        lab.score_records.create(
            score=get_score_stage(1), type="受欢迎度", description="增加一个关注")
        request.user.save()
        lab.save()
        abort(200)

    @app_auth
    @fetch_object(Lab.enabled, 'lab')
    def delete(self, request, lab):
        qs = request.user.followed_labs.filter(followed=lab)
        if qs.exists():
            # 积分
            request.user.score -= get_score_stage(1)
            request.user.score_records.create(
                score=-get_score_stage(1), type="活跃度",
                description="取消关注")
            lab.score -= get_score_stage(1)
            lab.score_records.create(
                score=-get_score_stage(1), type="受欢迎度",
                description="取消关注")
            request.user.save()
            lab.save()
            qs.delete()
            abort(200)
        abort(403, '未关注过该团队')


class FollowedTeamNeedList(View):
    @app_auth
    @validate_args({
        'offset': forms.IntegerField(required=False, min_value=0),
        'limit': forms.IntegerField(required=False, min_value=0),
        'status': forms.IntegerField(required=False, min_value=0, max_value=2),
        'type': forms.IntegerField(required=False, min_value=0, max_value=2)
    })
    def get(self, request, type=None, status=None, offset=0, limit=10, ):
        """获取用户的关注需求列表

        :param offset: 起始量
        :param limit: 偏移量
        :param type: 需求类型
        :param status: 需求状态
        :return:
            count: 需求总数
            list: 需求列表
                need_id: 需求ID
                team_id: 团队ID
                team_name: 团队名称
                icon_url: 团队头像
                status: 需求状态
                title: 需求标题
                number: 所需人数/团队人数
                degree: 需求学历
                members: 需求的加入者
                time_created: 发布时间
        """
        c = request.user.followed_needs.count()
        qs = request.user.followed_needs.all()

        if type is not None:
            qs = qs.filter(type=type)
        if status is not None:
            qs = qs.filter(status=status)
        needs = qs[offset:offset + limit]
        l = list()
        for n in needs:
            need_dic = dict()
            members = dict()
            if n.members:
                ids = n.members.split("|")
                for id in ids:
                    id = int(id)
                    if n.type == 0:
                        members[id] = User.enabled.get(id=id).name
                    else:
                        members[id] = Team.enabled.get(id=id).name
            need_dic['id'] = n.id
            need_dic['team_id'] = n.team.id
            need_dic['team_name'] = n.team.name
            need_dic['number'] = n.number
            need_dic['icon_url'] = n.team.icon
            need_dic['status'] = n.status
            need_dic['title'] = n.title
            need_dic['degree'] = n.degree
            need_dic['members'] = members
            need_dic['time_created'] = n.time_created
            l.append(need_dic)
        return JsonResponse({'count': c, 'list': l})


class FollowedTeamNeed(View):
    @fetch_object(TeamNeed.objects, 'need')
    @app_auth
    def get(self, request, need):
        """判断当前用户是否关注了need"""

        if request.user.followed_needs.filter(followed=need).exists():
            abort(200)
        abort(404, '未关注该需求')

    @fetch_object(TeamNeed.objects, 'need')
    @app_auth
    def post(self, request, need):
        """令当前用户关注need"""

        if request.user.followed_needs.filter(followed=need).exists():
            abort(403, '已经关注过该需求')
        request.user.followed_needs.create(followed=need)
        request.user.score += get_score_stage(1)
        request.user.score_records.create(
            score=get_score_stage(1), type="活跃度", description="增加一个关注")
        request.user.save()
        abort(200)

    @fetch_object(TeamNeed.objects, 'need')
    @app_auth
    def delete(self, request, need):
        """令当前用户取消关注need"""

        qs = request.user.followed_needs.filter(followed=need)
        if qs.exists():
            # 积分
            request.user.score -= get_score_stage(1)
            request.user.score_records.create(
                score=-get_score_stage(1), type="活跃度",
                description="取消关注")
            qs.delete()
            abort(200)
        abort(403, '未关注过该需求')


class FollowedActivityList(View):
    ORDERS = ['time_created', '-time_created', 'name', '-name']

    @app_auth
    @validate_args({
        'offset': forms.IntegerField(required=False, min_value=0),
        'limit': forms.IntegerField(required=False, min_value=0),
        'order': forms.IntegerField(required=False, min_value=0,
                                    max_value=3),
    })
    def get(self, request, offset=0, limit=10, order=1):
        """获取用户的关注活动列表

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
        c = request.user.followed_activities.count()
        qs = request.user.followed_activities.order_by(
            self.ORDERS[order])[offset:offset + limit]
        l = [{'id': a.id,
              'name': a.name,
              'liker_count': a.likers.count(),
              'status': a.status,
              'time_started': a.time_started,
              'time_ended': a.time_ended,
              'deadline': a.deadline,
              'user_participator_count': a.user_participators.count(),
              'time_created': a.time_created} for a in qs]
        return JsonResponse({'count': c, 'list': l})


class FollowedActivity(View):
    @fetch_object(Activity.enabled, 'activity')
    @app_auth
    def get(self, request, activity):
        """判断当前用户是否关注了activity"""

        if request.user.followed_activities.filter(
                followed=activity).exists():
            abort(200)
        abort(404, '未关注该活动')

    @fetch_object(Activity.enabled, 'activity')
    @app_auth
    def post(self, request, activity):
        """令当前用户关注activity"""

        if request.user.followed_activities.filter(
                followed=activity).exists():
            abort(403, '已经关注过该活动')
        request.user.followed_activities.create(followed=activity)
        request.user.score += get_score_stage(1)
        request.user.score_records.create(
            score=get_score_stage(1), type="活跃度", description="增加一个关注")
        request.user.save()
        abort(200)

    @fetch_object(Activity.enabled, 'activity')
    @app_auth
    def delete(self, request, activity):
        """令当前用户取消关注activity"""

        qs = request.user.followed_activities.filter(followed=activity)
        if qs.exists():
            # 积分
            request.user.score -= get_score_stage(1)
            request.user.score_records.create(
                score=-get_score_stage(1), type="活跃度",
                description="取消关注")
            qs.delete()
            abort(200)
        abort(403, '未关注过该活动')


class FollowedCompetitionList(View):
    ORDERS = ['time_created', '-time_created', 'name', '-name']

    @app_auth
    @validate_args({
        'offset': forms.IntegerField(required=False, min_value=0),
        'limit': forms.IntegerField(required=False, min_value=0),
        'order': forms.IntegerField(required=False, min_value=0,
                                    max_value=3),
    })
    def get(self, request, offset=0, limit=10, order=1):
        """获取用户的关注竞赛列表

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
        c = request.user.followed_competitions.count()
        qs = request.user.followed_competitions.order_by(
            self.ORDERS[order])[offset:offset + limit]
        l = [{'id': a.id,
              'name': a.name,
              'liker_count': a.likers.count(),
              'status': a.status,
              'time_started': a.time_started,
              'time_ended': a.time_ended,
              'deadline': a.deadline,
              'team_participator_count': a.team_participators.count(),
              'time_created': a.time_created} for a in qs]
        return JsonResponse({'count': c, 'list': l})


class FollowedCompetition(View):
    @fetch_object(Competition.enabled, 'competition')
    @app_auth
    def get(self, request, competition):
        """判断当前用户是否关注了competition"""

        if request.user.followed_competitions.filter(
                followed=competition).exists():
            abort(200)
        abort(404, '未关注该竞赛')

    @fetch_object(Competition.enabled, 'competition')
    @app_auth
    def post(self, request, competition):
        """令当前用户关注competition"""

        if request.user.followed_competitions.filter(
                followed=competition).exists():
            abort(403, '已经关注过该竞赛')
        request.user.followed_competitions.create(followed=competition)
        request.user.score += get_score_stage(1)
        request.user.score_records.create(
            score=get_score_stage(1), type="活跃度", description="增加一个关注")
        request.user.save()
        abort(200)

    @fetch_object(Competition.enabled, 'competition')
    @app_auth
    def delete(self, request, competition):
        """令当前用户取消关注competition"""

        qs = request.user.followed_competitions.filter(followed=competition)
        if qs.exists():
            # 积分
            request.user.score -= get_score_stage(1)
            request.user.score_records.create(
                score=-get_score_stage(1), type="活跃度",
                description="取消关注")
            qs.delete()
            abort(200)
        abort(403, '未关注过该竞赛')


class LikedEntity(View):
    """与当前用户点赞行为相关的View"""

    @app_auth
    def get(self, request, entity):
        """判断当前用户是否对某个对象点过赞"""

        if entity.likers.filter(liker=request.user).exists():
            abort(200)
        abort(404, '未点过赞')

    @app_auth
    def post(self, request, entity):
        """对某个对象点赞"""

        if not entity.likers.filter(liker=request.user).exists():
            entity.likers.create(liker=request.user)
            # 积分
            request.user.score += get_score_stage(1)
            request.user.score_records.create(
                score=get_score_stage(1), type="活跃度", description="给他人点赞")
            # 特征模型
            if isinstance(entity, User):
                record_like_user(request.user, entity)
            elif isinstance(entity, UserAction):
                record_like_user(request.user, entity.entity)
            elif isinstance(entity, Team):
                record_like_team(request.user, entity)
            elif isinstance(entity, TeamAction):
                record_like_user(request.user, entity.entity)
            else:
                pass

            request.user.save()
        abort(200)

    @app_auth
    def delete(self, request, entity):
        """对某个对象取消点赞"""

        # 积分
        request.user.score -= get_score_stage(1)
        request.user.score_records.create(
            score=-get_score_stage(1), type="活跃度", description="取消给他人点赞")
        request.user.save()
        entity.likers.filter(liker=request.user).delete()
        abort(200)


# noinspection PyMethodOverriding
class LikedUser(LikedEntity):
    @fetch_object(User.enabled, 'user')
    def get(self, request, user):
        return super().get(request, user)

    @fetch_object(User.enabled, 'user')
    def post(self, request, user):
        # 积分
        user.score += get_score_stage(1)
        user.score_records.create(
            score=get_score_stage(1), type="受欢迎度", description="他人点赞")
        user.save()
        return super().post(request, user)

    @fetch_object(User.enabled, 'user')
    def delete(self, request, user):
        # 积分
        user.score -= get_score_stage(1)
        user.score_records.create(
            score=-get_score_stage(1), type="受欢迎度", description="他人取消点赞")
        user.save()
        return super().delete(request, user)


# noinspection PyMethodOverriding
class LikedTeam(LikedEntity):
    @fetch_object(Team.enabled, 'team')
    def get(self, request, team):
        return super().get(request, team)

    @fetch_object(Team.enabled, 'team')
    def post(self, request, team):
        # 积分
        team.score += get_score_stage(1)
        team.score_records.create(
            score=get_score_stage(1), type="受欢迎度", description="他人点赞")
        team.save()
        return super().post(request, team)

    @fetch_object(Team.enabled, 'team')
    def delete(self, request, team):
        # 积分
        team.score -= get_score_stage(1)
        team.score_records.create(
            score=-get_score_stage(1), type="受欢迎度", description="他人取消点赞")
        team.save()
        return super().delete(request, team)


# noinspection PyMethodOverriding
class LikedLab(LikedEntity):
    @fetch_object(Lab.enabled, 'lab')
    def get(self, request, lab):
        return super().get(request, lab)

    @fetch_object(Lab.enabled, 'lab')
    def post(self, request, lab):
        # 积分
        lab.score += get_score_stage(1)
        lab.score_records.create(
            score=get_score_stage(1), type="受欢迎度", description="他人点赞")
        lab.save()
        return super().post(request, lab)

    @fetch_object(Lab.enabled, 'lab')
    def delete(self, request, lab):
        # 积分
        lab.score -= get_score_stage(1)
        lab.score_records.create(
            score=-get_score_stage(1), type="受欢迎度", description="他人取消点赞")
        lab.save()
        return super().delete(request, lab)


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


# noinspection PyMethodOverriding
class LikedUserAction(LikedEntity):
    @fetch_object(UserAction.objects, 'action')
    def get(self, request, action):
        return super().get(request, action)

    @fetch_object(UserAction.objects, 'action')
    def post(self, request, action):
        return super().post(request, action)

    @fetch_object(UserAction.objects, 'action')
    def delete(self, request, action):
        return super().delete(request, action)


# noinspection PyMethodOverriding
class LikedTeamAction(LikedEntity):
    @fetch_object(TeamAction.objects, 'action')
    def get(self, request, action):
        return super().get(request, action)

    @fetch_object(TeamAction.objects, 'action')
    def post(self, request, action):
        return super().post(request, action)

    @fetch_object(TeamAction.objects, 'action')
    def delete(self, request, action):
        return super().delete(request, action)


# noinspection PyMethodOverriding
class LikedLabAction(LikedEntity):
    @fetch_object(LabAction.objects, 'action')
    def get(self, request, action):
        return super().get(request, action)

    @fetch_object(LabAction.objects, 'action')
    def post(self, request, action):
        return super().post(request, action)

    @fetch_object(LabAction.objects, 'action')
    def delete(self, request, action):
        return super().delete(request, action)


# noinspection PyMethodOverriding
class LikedSystemAction(LikedEntity):
    @fetch_object(SystemAction.objects, 'action')
    def get(self, request, action):
        return super().get(request, action)

    @fetch_object(SystemAction.objects, 'action')
    def post(self, request, action):
        return super().post(request, action)

    @fetch_object(SystemAction.objects, 'action')
    def delete(self, request, action):
        return super().delete(request, action)


# noinspection PyMethodOverriding
class LikedUserTag(LikedEntity):
    @fetch_object(UserTag.objects, 'tag')
    def get(self, request, tag):
        return super().get(request, tag)

    @fetch_object(UserTag.objects, 'tag')
    def post(self, request, tag):
        return super().post(request, tag)

    @fetch_object(UserTag.objects, 'tag')
    def delete(self, request, tag):
        return super().delete(request, tag)


# noinspection PyMethodOverriding
class LikedTeamTag(LikedEntity):
    @fetch_object(TeamTag.objects, 'tag')
    def get(self, request, tag):
        return super().get(request, tag)

    @fetch_object(TeamTag.objects, 'tag')
    def post(self, request, tag):
        return super().post(request, tag)

    @fetch_object(TeamTag.objects, 'tag')
    def delete(self, request, tag):
        return super().delete(request, tag)


class RelatedTeamList(View):
    ORDERS = ('team__time_created', '-team__time_created',
              'team__name', '-team__name')

    # noinspection PyUnusedLocal
    @app_auth
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
    @app_auth
    @validate_args({
        'offset': forms.IntegerField(required=False, min_value=0),
        'limit': forms.IntegerField(required=False, min_value=0),
        'order': forms.IntegerField(required=False, min_value=0, max_value=3),
    })
    def get(self, request, offset=0, limit=10, order=1):
        """获取当前用户创建的团队列表

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


class RelatedLabList(View):
    ORDERS = ('lab__time_created', '-lab__time_created',
              'lab__name', '-lab__name')

    # noinspection PyUnusedLocal
    @app_auth
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
        c = request.user.labs.count()
        labs = request.user.labs.order_by(k)[i:j]
        l = [{'id': t.lab.id,
              'name': t.lab.name,
              'icon_url': t.lab.icon,
              'owner_id': t.lab.owner.id,
              'liker_count': t.lab.likers.count(),
              'visitor_count': t.lab.visitors.count(),
              'member_count': t.lab.members.count(),
              'fields': [t.lab.field1, t.lab.field2],
              'tags': [tag.name for tag in t.lab.tags.all()],
              'time_created': t.lab.time_created} for t in labs]
        return JsonResponse({'count': c, 'list': l})


class OwnedLabList(View):
    ORDERS = ('time_created', '-time_created', 'name', '-name')

    # noinspection PyUnusedLocal
    @app_auth
    @validate_args({
        'offset': forms.IntegerField(required=False, min_value=0),
        'limit': forms.IntegerField(required=False, min_value=0),
        'order': forms.IntegerField(required=False, min_value=0, max_value=3),
    })
    def get(self, request, offset=0, limit=10, order=1):
        """获取当前用户创建的团队列表

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
        c = request.user.owned_labs.count()
        labs = request.user.owned_labs.order_by(k)[i:j]
        l = [{'id': t.id,
              'name': t.name,
              'icon_url': t.icon,
              'owner_id': t.owner.id,
              'liker_count': t.likers.count(),
              'visitor_count': t.visitors.count(),
              'member_count': t.members.count(),
              'fields': [t.field1, t.field2],
              'tags': [tag.name for tag in t.tags.all()],
              'time_created': t.time_created} for t in labs]
        return JsonResponse({'count': c, 'list': l})


class ActivityList(View):
    ORDERS = ('time_created', '-time_created', 'name', '-name')

    @app_auth
    @validate_args({
        'offset': forms.IntegerField(required=False, min_value=0),
        'limit': forms.IntegerField(required=False, min_value=0),
        'order': forms.IntegerField(required=False, min_value=0,
                                    max_value=3),
    })
    def get(self, request, offset=0, limit=10, order=1):
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
                time_started: 开始时间
                time_ended: 结束时间
                deadline: 截止时间
                user_participator_count: 已报名人数
                time_created: 创建时间
        """

        k = self.ORDERS[order]
        c = request.user.activities.count()
        qs = request.user.activities.order_by(k)[offset: offset + limit]
        l = [{'id': a.activity.id,
              'name': a.activity.name,
              'liker_count': a.activity.likers.count(),
              'time_started': a.activity.time_started,
              'time_ended': a.activity.time_ended,
              'deadline': a.activity.deadline,
              'user_participator_count': a.activity.user_participators.count(),
              'time_created': a.activity.time_created} for a in qs]
        return JsonResponse({'count': c, 'list': l})


class CompetitionList(View):
    ORDERS = ('time_created', '-time_created', 'name', '-name')

    @app_auth
    @validate_args({
        'offset': forms.IntegerField(required=False, min_value=0),
        'limit': forms.IntegerField(required=False, min_value=0),
        'order': forms.IntegerField(required=False, min_value=0,
                                    max_value=3),
    })
    def get(self, request, offset=0, limit=10, order=1):
        """获取竞赛列表

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
                time_started: 开始时间
                time_ended: 结束时间
                deadline: 截止时间
                team_participator_count: 已报名人数
                time_created: 创建时间
        """
        k = self.ORDERS[order]
        if request.user.role == '专家':
            ctp = request.user.scored_competitions.all()
            qs = ctp.order_by(k)[offset: offset + limit]
            c = ctp.count()
            l = [{'id': a.id,
                  'name': a.name,
                  'liker_count': a.likers.count(),
                  'status': a.status,
                  'time_started': a.time_started,
                  'time_ended': a.time_ended,
                  'deadline': a.deadline,
                  'team_participator_count': a.team_participators.count(),
                  'time_created': a.time_created,
                  'province': a.province} for a in qs]
            return JsonResponse({'count': c, 'list': l})

        ctp = CompetitionTeamParticipator.objects.filter(
            team__members__user=request.user).distinct()
        qs = ctp.order_by(k)[offset: offset + limit]
        c = ctp.count()
        l = [{'id': a.competition.id,
              'name': a.competition.name,
              'liker_count': a.competition.likers.count(),
              'time_started': a.competition.time_started,
              'time_ended': a.competition.time_ended,
              'deadline': a.competition.deadline,
              'team_participator_count':
                  a.competition.team_participators.count(),
              'time_created': a.competition.time_created,
              'team_id': a.team.id,
              'team_name': a.team.name,
              } for a in qs]

        ctp2 = CompetitionTeamParticipator.objects.filter(
            team__owner=request.user).distinct()
        qs2 = ctp2.order_by(k)[offset: offset + limit]
        c2 = ctp2.count()
        l2 = [{'id': a.competition.id,
               'name': a.competition.name,
               'liker_count': a.competition.likers.count(),
               'time_started': a.competition.time_started,
               'time_ended': a.competition.time_ended,
               'deadline': a.competition.deadline,
               'team_participator_count':
                   a.competition.team_participators.count(),
               'time_created': a.competition.time_created,
               'team_id': a.team.id,
               'team_name': a.team.name,
               } for a in qs2]
        return JsonResponse({'count': c + c2, 'list': l + l2})


# noinspection PyClassHasNoInit
class InvitationList(View):
    @app_auth
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
    @require_verification_token
    def post(self, request, invitation):
        """同意团队的加入邀请并成为团队成员（需收到过加入团队邀请）"""

        if invitation.user != request.user:
            abort(403, '未收到过邀请')

        # 若已是团队成员则不做处理
        if invitation.team.members.filter(user=request.user).exists():
            invitation.delete()
            abort(200)

        # 在事务中建立关系，并删除对应的加团队邀请
        with transaction.atomic():
            invitation.team.members.create(user=request.user)
            # 发布用户加入团队动态
            action.join_team(request.user, invitation.team)
            invitation.delete()
            request.user.score += get_score_stage(1)
            request.user.score_records.create(
                score=get_score_stage(1), type="能力",
                description="成功加入一个团队")
            invitation.team.score += get_score_stage(1)
            invitation.team.score_records.create(
                score=get_score_stage(1), type="能力",
                description="成功招募队员")
            request.user.save()
            invitation.team.save()
        abort(200)

    @fetch_object(TeamInvitation.objects, 'invitation')
    @require_verification_token
    def delete(self, request, invitation):
        """忽略某邀请"""

        if invitation.user != request.user:
            abort(403, '未收到过邀请')

        invitation.delete()
        abort(200)


class Feedback(View):
    @app_auth
    @validate_args({
        'content': forms.CharField(max_length=200),
    })
    def post(self, request, content):
        """用户意见反馈

        :param content: 反馈内容
        :return: 200
        """
        if request.user.feedback.count() == 0:
            request.user.score += get_score_stage(2)
            request.user.score_records.create(
                score=get_score_stage(2), type="活跃度",
                description="增加一条反馈")
            request.user.save()
        request.user.feedback.create(content=content)
        abort(200)


class InvitationCode(View):
    @app_auth
    def get(self, request):
        """获取用户自己的邀请码

        :return: invitation_code: 邀请码
        """
        invitation_code = request.user.invitation_code
        return JsonResponse({'invitation_code': invitation_code})


class Inviter(View):
    @app_auth
    def get(self, request):
        """获取用户自己的邀请者信息

        """
        used_invitation_code = request.user.used_invitation_code
        if not used_invitation_code:
            abort(403, '你没有邀请人')
        try:
            user = User.enabled.get(invitation_code=used_invitation_code)
        except IntegrityError:
            abort(404, '该用户已不存在')
        else:
            r = {'id': user.id,
                 'time_created': user.time_created,
                 'name': user.name,
                 'icon_url': user.icon,
                 'description': user.description,
                 'gender': user.gender,
                 'birthday': user.birthday,
                 'province': user.province,
                 'city': user.city,
                 'county': user.county,
                 'tags': [tag.name for tag in user.tags.all()],
                 'follower_count': user.followers.count(),
                 'followed_count': user.followed_users.count() +
                                   user.followed_teams.count(),
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
                 'unit1': user.unit1,
                 'unit2': user.unit2,
                 'profession': user.profession,
                 'score': user.score}
            return JsonResponse(r)


class BindPhoneNumber(View):
    @app_auth
    @validate_args({
        'phone_number': forms.CharField(min_length=11, max_length=11),
        'password': forms.CharField(min_length=6, max_length=32),
        'validation_code': forms.CharField(min_length=6, max_length=6),
    })
    def post(self, request, phone_number, password, validation_code):
        """绑定手机号，若成功返回200
        param phone_number: 手机号
        :param password: 密码
        :param validation_code: 手机号收到的验证码

        :return 200
        """

        if not UserValidationCode.verify(phone_number, validation_code):
            abort(400, '验证码与手机不匹配')

        if not request.user.check_password(password):
            abort(401, '密码错误')

        if User.enabled.filter(phone_number=phone_number).count() > 0:
            abort(404, '手机号已存在')

        request.user.phone_number = phone_number
        request.user.save()
        abort(200)


class UserScoreRecord(View):
    ORDERS = ('time_created', '-time_created')

    @app_auth
    @validate_args({
        'offset': forms.IntegerField(required=False, min_value=0),
        'limit': forms.IntegerField(required=False, min_value=0),
        'order': forms.IntegerField(required=False, min_value=0, max_value=1),
    })
    def get(self, request, offset=0, limit=10, order=1):
        """获取用户的积分明细

        :param offset: 拉取的起始
        :param limit: 拉取的数量上限
        :return:
            count: 明细的总条数
            list:
                score: 积分
                type: 积分类别
                description: 描述
                time_created: 时间

        """
        k = self.ORDERS[order]
        r = request.user.score_records.all()
        c = r.count()
        qs = r.order_by(k)[offset: offset + limit]
        l = [{'description': s.description,
              'score': s.score,
              'type': s.type,
              'time_created': s.time_created} for s in qs]
        return JsonResponse({'count': c, 'list': l})


class FavoredEntity(View):
    """与当前用户收藏行为相关的View"""

    @app_auth
    def get(self, request, entity):
        """判断当前用户是否收藏过某个对象"""

        if entity.favorers.filter(favorer=request.user).exists():
            abort(200)
        abort(404, '未收藏过')

    @app_auth
    def post(self, request, entity):
        """收藏某个对象"""

        if not entity.favorers.filter(favorer=request.user).exists():
            entity.favorers.create(favorer=request.user)

            request.user.save()
        abort(200)

    @app_auth
    def delete(self, request, entity):
        """对某个对象取消点赞"""

        entity.favorers.filter(favorer=request.user).delete()
        abort(200)


# noinspection PyMethodOverriding
class FavoredActivity(FavoredEntity):
    @fetch_object(Activity.objects, 'activity')
    def get(self, request, activity):
        return super().get(request, activity)

    @fetch_object(Activity.objects, 'activity')
    def post(self, request, activity):
        return super().post(request, activity)

    @fetch_object(Activity.objects, 'activity')
    def delete(self, request, activity):
        return super().delete(request, activity)


# noinspection PyMethodOverriding
class FavoredCompetition(FavoredEntity):
    @fetch_object(Competition.objects, 'competition')
    def get(self, request, competition):
        return super().get(request, competition)

    @fetch_object(Competition.objects, 'competition')
    def post(self, request, competition):
        return super().post(request, competition)

    @fetch_object(Competition.objects, 'competition')
    def delete(self, request, competition):
        return super().delete(request, competition)


# noinspection PyMethodOverriding
class FavoredUserAction(FavoredEntity):
    @fetch_object(UserAction.objects, 'action')
    def get(self, request, action):
        return super().get(request, action)

    @fetch_object(UserAction.objects, 'action')
    def post(self, request, action):
        return super().post(request, action)

    @fetch_object(UserAction.objects, 'action')
    def delete(self, request, action):
        return super().delete(request, action)


# noinspection PyMethodOverriding
class FavoredTeamAction(FavoredEntity):
    @fetch_object(TeamAction.objects, 'action')
    def get(self, request, action):
        return super().get(request, action)

    @fetch_object(TeamAction.objects, 'action')
    def post(self, request, action):
        return super().post(request, action)

    @fetch_object(TeamAction.objects, 'action')
    def delete(self, request, action):
        return super().delete(request, action)


# noinspection PyMethodOverriding
class FavoredLabAction(FavoredEntity):
    @fetch_object(LabAction.objects, 'action')
    def get(self, request, action):
        return super().get(request, action)

    @fetch_object(LabAction.objects, 'action')
    def post(self, request, action):
        return super().post(request, action)

    @fetch_object(LabAction.objects, 'action')
    def delete(self, request, action):
        return super().delete(request, action)


# noinspection PyMethodOverriding
class FavoredSystemAction(FavoredEntity):
    @fetch_object(SystemAction.objects, 'action')
    def get(self, request, action):
        return super().get(request, action)

    @fetch_object(SystemAction.objects, 'action')
    def post(self, request, action):
        return super().post(request, action)

    @fetch_object(SystemAction.objects, 'action')
    def delete(self, request, action):
        return super().delete(request, action)


# noinspection PyUnusedLocal
class AchievementList(View):
    ORDERS = ('time_created', '-time_created')

    @app_auth
    @validate_args({
        'offset': forms.IntegerField(required=False, min_value=0),
        'limit': forms.IntegerField(required=False, min_value=0),
        'order': forms.IntegerField(required=False, min_value=0, max_value=3),
    })
    def get(self, request, offset=0, limit=10, order=1):
        user = request.user
        i, j, k = offset, offset + limit, self.ORDERS[order]
        c = user.achievements.count()
        achievements = user.achievements.order_by(k)[i:j]
        l = [{'id': a.id,
              'description': a.description,
              'picture': a.picture,
              'time_created': a.time_created} for a in achievements]
        return JsonResponse({'count': c, 'list': l})

    @require_verification_token
    @validate_args({
        'description': forms.CharField(min_length=1, max_length=100),
    })
    def post(self, request, description):
        user = request.user
        if check_bad_words(description):
            abort(403, '含有非法词汇')

        achievement = Achievement(user=user, description=description)
        picture = request.FILES.get('image')
        if picture:
            filename = save_uploaded_image(picture)
            if filename:
                achievement.picture = filename
        else:
            abort(400, '图片上传失败')
        achievement.save()

        return JsonResponse({'achievement_id': achievement.id})
