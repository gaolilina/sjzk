import json

from django import forms
from django.core.exceptions import ObjectDoesNotExist
from django.db import transaction
from django.db.models import Q
from django.http import HttpResponseRedirect, JsonResponse
from django.http import JsonResponse
from django.utils import timezone
from django.views.generic import View

from ChuangYi.settings import UPLOADED_URL
from main.models import Lab, User, LabAchievement, LabNeed, LabAction
from main.models.task import InternalTask, ExternalTask
from main.utils import abort, action, save_uploaded_image, get_score_stage
from main.utils.decorators import *
from main.utils.decorators import require_verification_token
from main.utils.dfa import check_bad_words
from main.utils.http import notify_user
from main.utils.recommender import calculate_ranking_score
from main.views.common import CommentList
from main.views.favor import FavoredActionList, IFavorSomething
from main.views.like import ILikeSomething
from util.decorator.auth import app_auth
from util.decorator.param import validate_args, fetch_object

__all__ = ('List', 'Screen', 'Profile', 'Icon', 'MemberList',
           'Member', 'MemberRequestList', 'MemberRequest', 'Invitation',
           'AllAchievementList', 'AllAchievement', 'AchievementList',
           'AllNeedList', 'NeedList', 'Need', 'MemberNeedRequestList',
           'MemberNeedRequest', 'NeedRequestList', 'NeedRequest',
           'NeedInvitationList', 'NeedInvitation', 'InternalTaskList',
           'InternalTasks', 'LabInternalTask', 'ExternalTaskList',
           'ExternalTasks', 'LabExternalTask', 'NeedUserList', 'NeedLabList',
           'CompetitionList', 'LabScoreRecord', 'NeedSearch', 'NeedScreen',
           'LabAwardList')


class List(View):
    ORDERS = ('time_created', '-time_created', 'name', '-name')

    # noinspection PyUnusedLocal
    @validate_args({
        'offset': forms.IntegerField(required=False, min_value=0),
        'limit': forms.IntegerField(required=False, min_value=0),
        'order': forms.IntegerField(required=False, min_value=0, max_value=3),
    })
    def get(self, request, offset=0, limit=10, order=1):
        """获取实验室列表

        :param offset: 偏移量
        :param limit: 数量上限
        :param order: 排序方式
            0: 注册时间升序
            1: 注册时间降序（默认值）
            2: 昵称升序
            3: 昵称降序
        :return:
            count: 实验室总数
            list: 实验室列表
                id: 实验室ID
                name: 实验室名
                icon_url: 头像
                owner_id: 创建者ID
                liker_count: 点赞数
                visitor_count: 最近7天访问数
                member_count: 实验室成员人数
                fields: 所属领域，格式：['field1', 'field2']
                tags: 标签，格式：['tag1', 'tag2', ...]
                time_created: 注册时间
        """
        i, j, k = offset, offset + limit, self.ORDERS[order]
        c = Lab.enabled.count()
        labs = Lab.enabled.order_by(k)[i:j]
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

    @require_verification_token
    @validate_args({
        'name': forms.CharField(max_length=20),
        'description': forms.CharField(required=False, max_length=100),
        'url': forms.CharField(required=False, max_length=100),
        'province': forms.CharField(required=False, max_length=20),
        'city': forms.CharField(required=False, max_length=20),
        'county': forms.CharField(required=False, max_length=20),
        'fields': forms.CharField(required=False, max_length=100),
        'tags': forms.CharField(required=False, max_length=100),
    })
    def post(self, request, **kwargs):
        """新建实验室，同时调用融云接口为该实验室创建一个对应的群聊

        :param kwargs:
            name: 实验室名称
            description: 实验室描述
            url: 实验室链接
            province:
            city:
            county:
            fields: 实验室领域，格式:'field1|field2'
            tags: 标签，格式：'tag1|tag2|tag3|...'
        :return: lab_id: 实验室id
        """
        name = kwargs.pop('name')
        fields = kwargs.pop('fields', None)
        tags = kwargs.pop('tags', None)

        # 昵称唯一性验证
        if Lab.enabled.filter(name=name).count() != 0:
            abort(403, '实验室名已被注册')
        # 昵称非法词验证
        if check_bad_words(name):
            abort(403, '实验室名含非法词汇')

        lab = Lab(owner=request.user, name=name)
        lab.save()

        for k in kwargs:
            setattr(lab, k, kwargs[k])
        fields = fields.split('|')[:2] if fields is not None else ('', '')
        lab.field1, lab.field2 = fields[0].strip(), fields[1].strip()

        if tags:
            tags = tags.split('|')[:5]
            with transaction.atomic():
                lab.tags.all().delete()
                order = 0
                for tag in tags:
                    tag = tag.strip()
                    if tag:
                        lab.tags.create(name=tag, order=order)
                        order += 1
        lab.save()

        # action.create_lab(request.user, lab)
        request.user.score += get_score_stage(2)
        request.user.score_records.create(
            score=get_score_stage(2), type="能力", description="成功创建一个实验室")
        request.user.save()
        return JsonResponse({'lab_id': lab.id})


class Screen(View):
    ORDERS = ('time_created', '-time_created', 'name', '-name')

    @validate_args({
        'offset': forms.IntegerField(required=False, min_value=0),
        'limit': forms.IntegerField(required=False, min_value=0),
        'order': forms.IntegerField(required=False, min_value=0, max_value=3),
        'name': forms.CharField(required=False, max_length=20),
        'province': forms.CharField(required=False, max_length=20),
        'city': forms.CharField(required=False, max_length=20),
        'county': forms.CharField(required=False, max_length=20),
        'field': forms.CharField(required=False, max_length=10),
    })
    def get(self, request, offset=0, limit=10, order=None, **kwargs):
        """
        筛选实验室

        :param offset: 偏移量
        :param limit: 数量上限
        :param order: 排序方式（若无则进行个性化排序）
            0: 注册时间升序
            1: 注册时间降序
            2: 昵称升序
            3: 昵称降序
        :param kwargs: 搜索条件
            name: 实验室名包含字段
            province: 省
            city: 市
            county: 区/县
            field: 领域

        :return:
            count: 实验室总数
            list: 实验室列表
                id: 实验室ID
                name: 实验室名
                icon_url: 头像
                owner_id: 创建者ID
                liker_count: 点赞数
                visitor_count: 最近7天访问数
                member_count: 实验室成员人数
                fields: 所属领域，格式：['field1', 'field2']
                tags: 标签，格式：['tag1', 'tag2', ...]
                time_created: 注册时间
        """
        labs = Lab.enabled

        i, j = offset, offset + limit
        name = kwargs.pop('name', '')
        if name:
            # 按用户昵称段检索
            labs = labs.filter(name__icontains=name)

        province = kwargs.pop('province', '')
        if province:
            # 按省会筛选
            labs = labs.filter(province=province)
        city = kwargs.pop('city', '')
        if city:
            # 按城市筛选
            labs = labs.filter(city=city)
        county = kwargs.pop('county', '')
        if county:
            # 按区/县筛选
            labs = labs.filter(county=county)
        field = kwargs.pop('field', '')
        if field:
            # 按领域筛选
            labs = labs.filter(Q(field1=field) | Q(field2=field))

        labs = labs.all()
        c = labs.count()
        if order is not None:
            labs = labs.order_by(self.ORDERS[order])[i:j]
        else:
            # 将结果进行个性化排序
            lab_list = list()
            for t in labs:
                if fetch_user_by_token(request):
                    lab_list.append((t, calculate_ranking_score(request.user, t)))
                else:
                    lab_list.append((t, 0))
            lab_list = sorted(lab_list, key=lambda x: x[1], reverse=True)
            labs = (t[0] for t in lab_list[i:j])
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


class Profile(View):
    @fetch_object(Lab.enabled, 'lab')
    @app_auth
    def get(self, request, lab):
        """获取实验室的基本资料

        :param: lab_id : 实验室ID
        :return:
            id: 实验室ID
            name: 实验室名
            icon_url: 头像
            owner_id: 创始人id
            time_created: 注册时间
            is_recruiting：是否招募新成员
            description: 实验室简介
            url: 实验室链接
            liker_count: 点赞数
            fan_count: 粉丝数
            visitor_count: 最近访客数
            advantage: 实验室优势
            business_stage: 工商阶段
            financing_stage: 融资阶段
            valuation: 实验室估值
            valuation_unit: 实验室估值单位
            province:
            city:
            county:
            fields: 所属领域，格式：['field1', 'field2']
            tag_ids: 标签id，格式：[id1, id2, ...]
            tag_likers: 标签点赞数，格式：[count1, count2, ...]
            tags: 标签，格式：['tag1', 'tag2', ...]
            score: 积分
        """
        if lab.owner != request.user:
            lab.visitors.update_or_create(visitor=request.user)
            # record_view_lab(request.user, lab)

        r = dict()
        r['id'] = lab.id
        r['name'] = lab.name
        r['icon_url'] = lab.icon
        r['owner_id'] = lab.owner.id
        r['time_created'] = lab.time_created
        r['is_recruiting'] = lab.is_recruiting
        r['description'] = lab.description
        r['url'] = lab.url
        r['liker_count'] = lab.likers.count()
        r['fan_count'] = lab.followers.count()
        r['visitor_count'] = lab.visitors.count()
        r['fields'] = [lab.field1, lab.field2]
        r['advantage'] = lab.advantage
        r['business_stage'] = lab.business_stage
        r['financing_stage'] = lab.financing_stage
        r['valuation'] = lab.valuation
        r['valuation_unit'] = lab.valuation_unit
        r['province'] = lab.province
        r['city'] = lab.city
        r['county'] = lab.county
        r['score'] = lab.score
        r['tag_ids'] = []
        r['tag_likers'] = []
        r['tags'] = []
        for t in lab.tags.all():
            r['tag_ids'].append(t.id)
            r['tags'].append(t.name)
            r['tag_likers'].append(t.likers.count())

        return JsonResponse(r)

    @fetch_object(Lab.enabled, 'lab')
    @require_verification_token
    @validate_args({
        'name': forms.CharField(required=False, max_length=20),
        'description': forms.CharField(required=False, max_length=100),
        'is_recruiting': forms.BooleanField(required=False),
        'url': forms.CharField(required=False, max_length=100),
        'province': forms.CharField(required=False, max_length=20),
        'city': forms.CharField(required=False, max_length=20),
        'county': forms.CharField(required=False, max_length=20),
        'fields': forms.CharField(required=False, max_length=100),
        'tags': forms.CharField(required=False, max_length=100),
        'advantage': forms.CharField(required=False, max_length=100),
        'business_stage': forms.IntegerField(required=False),
        'financing_stage': forms.CharField(required=False, max_length=10),
        'valuation': forms.IntegerField(required=False),
        'valuation_unit': forms.CharField(required=False, max_length=5),
    })
    def post(self, request, lab, **kwargs):
        """修改实验室资料

        :param lab: 实验室ID
        :param kwargs:
            name: 实验室名
            description: 实验室简介
            is_recruiting：是否招募新成员
            url: 实验室链接
            advantage: 实验室优势
            business_stage: 工商阶段
            financing_stage: 融资阶段
            valuation: 实验室估值
            valuation_unit: 实验室估值单位
            province:
            city:
            county:
            fields: 实验室领域，格式:'field1|field2'
            tags: 标签，格式：'tag1|tag2|tag3|...'
        """
        if request.user != lab.owner:
            abort(403, '只允许负责人操作')

        fields = kwargs.pop('fields', None)
        tags = kwargs.pop('tags', None)

        for k in kwargs:
            if k == "name":
                name = kwargs['name']
                # 昵称唯一性验证
                if Lab.enabled.filter(name=name).exclude(
                        id=lab.id).count() != 0:
                    abort(403, '实验室名已被注册')
                # 昵称非法词验证
                if check_bad_words(name):
                    abort(403, '实验室名含非法词汇')
            if k == "description":
                if check_bad_words(kwargs['description']):
                    abort(403, '含有非法词汇')
            setattr(lab, k, kwargs[k])

        if fields:
            fields = fields.split('|')[:2]
            if len(fields) < 2:
                fields.append('')
            lab.field1, lab.field2 = fields[0].strip(), fields[1].strip()

        if tags:
            tags = tags.split('|')[:5]
            with transaction.atomic():
                lab.tags.all().delete()
                order = 0
                for tag in tags:
                    tag = tag.strip()
                    if tag:
                        lab.tags.create(name=tag, order=order)
                        order += 1
        lab.save()
        abort(200)


# noinspection PyUnusedLocal
class Icon(View):
    @fetch_object(Lab.enabled, 'lab')
    def get(self, request, lab):
        """获取实验室头像"""

        if lab.icon:
            return HttpResponseRedirect(UPLOADED_URL + lab.icon)
        abort(404, '未设置头像')

    @fetch_object(Lab.enabled, 'lab')
    @require_verification_token
    def post(self, request, lab):
        """设置实验室的头像"""

        if request.user != lab.owner:
            abort(403, '只有负责人可以操作')

        icon = request.FILES.get('image')
        if not icon:
            abort(400, '头像上传失败')

        filename = save_uploaded_image(icon)
        if filename:
            lab.icon = filename
            lab.save()
            return JsonResponse({'icon_url': lab.icon})
        abort(400, '头像保存失败')


# noinspection PyUnusedLocal
class MemberList(View):
    ORDERS = (
        'time_created',
        '-time_created',
        'user__name',
        '-user__name',
    )

    @fetch_object(Lab.enabled, 'lab')
    @app_auth
    @validate_args({
        'offset': forms.IntegerField(required=False, min_value=0),
        'limit': forms.IntegerField(required=False, min_value=0),
        'order': forms.IntegerField(required=False, min_value=0, max_value=3),
    })
    def get(self, request, lab, offset=0, limit=10, order=1):
        """获取实验室的成员列表

        :param offset: 偏移量
        :param order: 排序方式
            0: 成为成员时间升序
            1: 成为成员时间降序（默认值）
            2: 昵称升序
            3: 昵称降序
        :return:
            count: 成员总数
            list: 成员列表
                id: 用户ID
                username: 用户名
                icon_url: 头像
                name: 用户昵称
                time_created: 成为实验室成员时间
        """

        i, j, k = offset, offset + limit, self.ORDERS[order]
        c = lab.members.count()
        rs = lab.members.order_by(k)[i:j]
        l = [{'id': r.user.id,
              'username': r.user.username,
              'icon_url': r.user.icon,
              'name': r.user.name,
              'time_created': r.time_created} for r in rs]
        return JsonResponse({'count': c, 'list': l})


# noinspection PyUnusedLocal
class Member(View):
    @fetch_object(Lab.enabled, 'lab')
    @fetch_object(User.enabled, 'user')
    @app_auth
    def get(self, request, lab, user):
        """检查用户是否为实验室成员"""

        if lab.members.filter(user=user).exists():
            abort(200)
        abort(404, '非实验室成员')

    @fetch_object(Lab.enabled, 'lab')
    @fetch_object(User.enabled, 'user')
    @require_verification_token
    def post(self, request, lab, user):
        """将目标用户添加为自己的实验室成员（对方需发送过加入实验室申请）"""

        if request.user != lab.owner:
            abort(403, '只有负责人能操作')

        if not lab.member_requests.filter(user=user):
            abort(403, '该用户未发送过请求')

        # 若对方已是实验室成员则不做处理
        if lab.members.filter(user=user).exists():
            abort(200)

        # 在事务中建立关系，并删除对应的加实验室申请
        with transaction.atomic():
            lab.member_requests.filter(user=user).delete()
            lab.members.create(user=user)
            # action.join_lab(user, lab)
        abort(200)

    @fetch_object(Lab.enabled, 'lab')
    @fetch_object(User.enabled, 'user')
    @require_verification_token
    def delete(self, request, lab, user):
        """退出实验室(默认)/删除成员"""
        if user == lab.owner:
            abort(403, "负责人不能退出")

        qs = lab.members.filter(user=user)
        if qs.exists():
            qs.delete()
            abort(200)
        abort(404, '成员不存在')


class MemberRequestList(View):
    @fetch_object(Lab.enabled, 'lab')
    @validate_args({
        'offset': forms.IntegerField(required=False),
        'limit': forms.IntegerField(required=False, min_value=0),
    })
    @app_auth
    def get(self, request, lab, offset=0, limit=10):
        """获取实验室的加入申请列表

        * 若当前用户为实验室创始人时，按请求时间逆序获取收到的加实验室申请信息，
          拉取后的申请 标记为已读
        * 若不为实验室创始人时，检查当前用户是否已经发送过加实验室请求，
          并且该请求未被处理（接收或忽略）

        :param limit: 拉取的数量上限
        :return: request.user 为实验室创始人时，200 | 404
        :return: request.user 不为实验室创始人时
            count: 申请总条数
            list: 加入实验室请求信息列表
                id: 用户ID
                username: 用户名
                name: 用户昵称
                icon_url: 用户头像
                description: 附带消息
                time_created: 请求发出的时间
        """
        if request.user == lab.owner:
            # 拉取实验室的加入申请信息
            c = lab.member_requests.count()
            qs = lab.member_requests.all()[offset:offset + limit]

            l = [{'id': r.user.id,
                  'username': r.user.username,
                  'name': r.user.name,
                  'icon_url': r.user.icon,
                  'description': r.description,
                  'time_created': r.time_created} for r in qs]
            return JsonResponse({'count': c, 'list': l})

    @fetch_object(Lab.enabled, 'lab')
    @require_verification_token
    @validate_args({
        'description': forms.CharField(required=False, max_length=100),
    })
    def post(self, request, lab, description=''):
        """向实验室发出加入申请

        :param description: 附带消息
        """
        if request.user == lab.owner:
            abort(403, '负责人不能申请')

        if lab.members.filter(user=request.user).exists():
            abort(403, '已经发送过申请')

        if lab.member_requests.filter(user=request.user).exists():
            abort(200)

        if lab.invitations.filter(user=request.user).exists():
            abort(403, '实验室已经发送过邀请')

        for need in lab.needs.all():
            if need.member_requests.filter(sender=request.user).exists():
                abort(403, '已经发送过申请')

        lab.member_requests.create(user=request.user, description=description)
        abort(200)


class MemberRequest(View):
    @fetch_object(Lab.enabled, 'lab')
    @fetch_object(User.enabled, 'user')
    @app_auth
    def delete(self, request, lab, user):
        """忽略某用户的加实验室请求"""

        if request.user != lab.owner:
            abort(403, '只有负责人可以操作')

        qs = lab.member_requests.filter(user=user)
        if not qs.exists():
            abort(404, '申请不存在')
        qs.delete()
        abort(200)


class Invitation(View):
    @fetch_object(Lab.enabled, 'lab')
    @fetch_object(User.enabled, 'user')
    @require_verification_token
    @validate_args({
        'description': forms.CharField(required=False, max_length=100),
    })
    def post(self, request, lab, user, description=''):
        """向用户发出加入实验室邀请

        :param description: 附带消息
        """
        if request.user != lab.owner:
            abort(403, '只有负责人可以操作')

        if user == lab.owner:
            abort(403, '对方是本实验室负责人')

        if lab.members.filter(user=user).exists():
            abort(403, '对方已经是实验室成员')

        if lab.invitations.filter(user=user).exists():
            abort(200)

        if lab.member_requests.filter(user=user).exists():
            abort(403, '对方已经发送过申请')

        for need in lab.needs.all():
            if need.member_requests.filter(sender=request.user).exists():
                abort(403, '对方已经发送过申请')

        lab.invitations.create(user=user, description=description)
        notify_user(user, json.dumps({
            'type': 'invitation'
        }))
        abort(200)


# noinspection PyUnusedLocal
class AllAchievementList(View):
    ORDERS = ('time_created', '-time_created')

    @app_auth
    @validate_args({
        'offset': forms.IntegerField(required=False, min_value=0),
        'limit': forms.IntegerField(required=False, min_value=0),
        'order': forms.IntegerField(required=False, min_value=0, max_value=3),
    })
    def get(self, request, offset=0, limit=10, order=1):
        """获取所有实验室发布的成果

        :param offset: 偏移量
        :param limit: 数量上限
        :param order: 排序方式
            0: 发布时间升序
            1: 发布时间降序（默认值）
        :return:
            count: 成果总数
            list: 成果列表
                id: 成果ID
                lab_id: 实验室ID
                lab_name: 实验室名称
                icon_url: 实验室头像
                description: 成果描述
                picture: 图片
                time_created: 发布时间
        """
        i, j, k = offset, offset + limit, self.ORDERS[order]
        c = LabAchievement.objects.count()
        achievements = LabAchievement.objects.order_by(k)[i:j]
        l = [{'id': a.id,
              'lab_id': a.lab.id,
              'lab_name': a.lab.name,
              'icon_url': a.lab.icon,
              'description': a.description,
              'picture': a.picture,
              'time_created': a.time_created,
              'yes_count': a.likers.count(),
              'is_yes': request.user in a.likers.all()} for a in achievements]
        return JsonResponse({'count': c, 'list': l})


# noinspection PyUnusedLocal
class AllAchievement(View):
    @fetch_object(LabAchievement.objects, 'achievement')
    @require_verification_token
    def delete(self, request, lab, achievement):
        """删除成果"""

        if request.user != achievement.lab.owner:
            abort(403, '只有负责人可以操作')
        achievement.delete()
        abort(200)


# noinspection PyUnusedLocal
class AchievementList(View):
    ORDERS = ('time_created', '-time_created')

    @fetch_object(Lab.enabled, 'lab')
    @app_auth
    @validate_args({
        'offset': forms.IntegerField(required=False, min_value=0),
        'limit': forms.IntegerField(required=False, min_value=0),
        'order': forms.IntegerField(required=False, min_value=0, max_value=3),
    })
    def get(self, request, lab, offset=0, limit=10, order=1):
        """获取实验室发布的成果

        :param offset: 偏移量
        :param limit: 数量上限
        :param order: 排序方式
            0: 发布时间升序
            1: 发布时间降序（默认值）
        :return:
            count: 成果总数
            list: 成果列表
                id: 成果ID
                description: 成果描述
                picture: 图片
                time_created: 发布时间
        """
        i, j, k = offset, offset + limit, self.ORDERS[order]
        c = lab.achievements.count()
        achievements = lab.achievements.order_by(k)[i:j]
        l = [{'id': a.id,
              'description': a.description,
              'picture': a.picture,
              'time_created': a.time_created,
              'yes_count': a.likers.count(),
              'is_yes': request.user in a.likers.all()} for a in achievements]
        return JsonResponse({'count': c, 'list': l})

    @fetch_object(Lab.enabled, 'lab')
    @require_verification_token
    @validate_args({
        'description': forms.CharField(min_length=1, max_length=100),
    })
    def post(self, request, lab, description):
        """发布成果

        :param description: 成果描述
        :return: achievement_id: 成果id
        """
        if request.user != lab.owner:
            abort(403, '只有负责人可以操作')

        if check_bad_words(description):
            abort(403, '含有非法词汇')

        achievement_num = lab.achievements.count()
        if achievement_num == 0:
            lab.score += get_score_stage(2)
            lab.score_records.create(
                score=get_score_stage(2), type="初始数据",
                description="首次发布实验室成果")

        achievement = LabAchievement(lab=lab, description=description)
        picture = request.FILES.get('image')
        if picture:
            filename = save_uploaded_image(picture)
            if filename:
                achievement.picture = filename
        else:
            abort(400, '图片上传失败')
        achievement.save()

        request.user.score += get_score_stage(1)
        request.user.score_records.create(
            score=get_score_stage(1), type="能力", description="发布一个实验室成果")
        request.user.save()
        lab.score += get_score_stage(1)
        lab.score_records.create(
            score=get_score_stage(1), type="活跃度", description="发布一个实验室成果")
        lab.save()
        return JsonResponse({'achievement_id': achievement.id})


# noinspection PyUnusedLocal
class AllNeedList(View):
    # noinspection PyShadowingBuiltins
    @validate_args({
        'offset': forms.IntegerField(required=False, min_value=0),
        'limit': forms.IntegerField(required=False, min_value=0),
        'status': forms.IntegerField(required=False, min_value=0, max_value=2),
        'type': forms.IntegerField(required=False, min_value=0, max_value=2)
    })
    def get(self, request, type=None, status=None, offset=0, limit=10):
        """
        获取发布中的需求列表

        :param offset: 起始量
        :param limit: 偏移量
        :param type: 需求类型 - 0: member, 1: outsource, 2: undertake
        :param status: 需求状态 - 0: pending, 1: completed, 2: removed
        :return:
            count: 需求总数
            list: 需求列表
                need_id: 需求ID
                lab_id: 实验室ID
                lab_name: 实验室名称
                icon_url: 实验室头像
                status: 需求状态
                title: 需求标题
                number: 所需人数/实验室人数
                degree: 需求学历
                members: 需求的加入者
                time_created: 发布时间
        """
        qs = LabNeed.objects
        if type is not None:
            qs = qs.filter(type=type)
        if status is not None:
            qs = qs.filter(status=status)
        else:
            qs = qs.filter(status=0)
        c = qs.count()
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
                        members[id] = Lab.enabled.get(id=id).name
            need_dic['id'] = n.id
            need_dic['lab_id'] = n.lab.id
            need_dic['lab_name'] = n.lab.name
            need_dic['number'] = n.number
            need_dic['icon_url'] = n.lab.icon
            need_dic['status'] = n.status
            need_dic['title'] = n.title
            need_dic['degree'] = n.degree
            need_dic['members'] = members
            need_dic['time_created'] = n.time_created
            l.append(need_dic)
        return JsonResponse({'count': c, 'list': l})


class NeedList(View):
    # noinspection PyShadowingBuiltins
    @fetch_object(Lab.enabled, 'lab')
    @validate_args({
        'offset': forms.IntegerField(required=False, min_value=0),
        'limit': forms.IntegerField(required=False, min_value=0),
        'status': forms.IntegerField(required=False, min_value=0, max_value=2),
        'type': forms.IntegerField(required=False, min_value=0, max_value=2)
    })
    def get(self, request, lab, type=None, status=None, offset=0, limit=10):
        """
        :param offset: 起始量
        :param limit: 偏移量
        :param type: 需求类型 - 0: member, 1: outsource, 2: undertake
        :param status: 需求状态 - 0: pending, 1: completed, 2: removed
        :return:
            count: 需求总数
            list: 需求列表
                id: 需求ID
                lab_id: 实验室ID
                lab_name: 实验室名称
                icon_url: 实验室头像
                status: 需求状态
                title: 需求标题
                number: 所需人数/实验室人数
                degree: 需求学历
                time_created: 发布时间
        """
        qs = lab.needs
        if type is not None:
            qs = qs.filter(type=type)
        if status is not None:
            qs = qs.filter(status=status)
        else:
            qs = qs.filter(status=0)
        c = qs.count()
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
                        members[id] = Lab.enabled.get(id=id).name
            need_dic['id'] = n.id
            need_dic['lab_id'] = n.lab.id
            need_dic['lab_name'] = n.lab.name
            need_dic['icon_url'] = n.lab.icon
            need_dic['status'] = n.status
            need_dic['title'] = n.title
            need_dic['members'] = members
            need_dic['degree'] = n.degree
            need_dic['number'] = n.number
            need_dic['time_created'] = n.time_created
            l.append(need_dic)
        return JsonResponse({'count': c, 'list': l})

    # noinspection PyShadowingBuiltins
    @fetch_object(Lab.enabled, 'lab')
    @require_verification_token
    def post(self, request, lab, type):
        """发布需求

        人员需求：
            deadline: 截止时间
            description: 需求描述
            number: 所需人数
            age_min: 最小年龄
            age_max: 最大年龄
            gender: 性别要求
            field: 领域
            skill: 技能
            province: 省
            city: 市
            county: 县\区
            degree: 学历
            major: 专业
            time_graduated: 毕业时间
        外包需求：
            deadline: 截止时间
            description: 需求描述
            number: 所需人数
            age_min: 最小年龄
            age_max: 最大年龄
            gender: 性别要求
            field: 领域
            skill: 技能
            province: 省
            city: 市
            county: 县\区
            degree: 学历
            major: 专业
            cost: 费用
            cost_unit: 费用单位
            time_started: 外包任务开始时间
            time_ended: 外包任务结束时间
        承接需求：
            deadline: 截止时间
            description: 需求描述
            field: 领域
            skill: 技能
            major: 专业
            province: 省
            city: 市
            county: 县\区
            cost: 费用
            cost_unit: 费用单位
            time_started: 承接开始时间
            time_ended: 承接结束时间
        """
        if request.user != lab.owner:
            abort(403, '只有负责人可以操作')

        if type == 0:
            self.create_member_need(request, lab)
        elif type == 1:
            self.create_outsource_need(request, lab)
        elif type == 2:
            self.create_undertake_need(request, lab)
        else:
            abort(500)

    @validate_args({
        'deadline': forms.DateField(),
        'title': forms.CharField(max_length=20),
        'description': forms.CharField(required=False, max_length=200),
        'number': forms.IntegerField(min_value=1),
        'gender': forms.IntegerField(required=False, min_value=0, max_value=2),
        'field': forms.CharField(required=False, max_length=20),
        'skill': forms.CharField(required=False, max_length=20),
        'degree': forms.CharField(required=False, max_length=20),
        'major': forms.CharField(required=False, max_length=20),
        'age_min': forms.IntegerField(
            required=False, min_value=0, max_value=99),
        'age_max': forms.IntegerField(
            required=False, min_value=1, max_value=100),
        'province': forms.CharField(required=False, max_length=20),
        'city': forms.CharField(required=False, max_length=20),
        'county': forms.CharField(required=False, max_length=20),
        'time_graduated': forms.DateField(required=False),
    })
    def create_member_need(self, request, lab, **kwargs):
        if check_bad_words(kwargs["title"]) or check_bad_words(kwargs["description"]):
            abort(403, '含有非法词汇')

        lab_needs = LabNeed.objects.filter(lab=lab, type=0)
        if lab_needs.count() == 0:
            lab.score += get_score_stage(2)
            lab.score_records.create(
                score=get_score_stage(2), type="初始数据",
                description="首次发布实验室需求")
            lab.save()

        n = lab.needs.create(type=0)
        for k in kwargs:
            setattr(n, k, kwargs[k])
        n.save()
        # 发布动态
        action.send_member_need(lab, n)
        # 增加积分
        request.user.score += get_score_stage(1)
        request.user.score_records.create(
            score=get_score_stage(1), type="能力",
            description="发布一个实验室需求")
        lab.score += get_score_stage(1)
        lab.score_records.create(
            score=get_score_stage(1), type="活跃度",
            description="发布一个实验室需求")
        request.user.save()
        lab.save()
        abort(200)

    @validate_args({
        'deadline': forms.DateField(),
        'title': forms.CharField(max_length=20),
        'description': forms.CharField(required=False, max_length=200),
        'number': forms.IntegerField(min_value=1),
        'gender': forms.IntegerField(required=False, min_value=0, max_value=2),
        'field': forms.CharField(required=False, max_length=20),
        'skill': forms.CharField(required=False, max_length=20),
        'major': forms.CharField(required=False, max_length=20),
        'degree': forms.CharField(required=False, max_length=20),
        'age_min': forms.IntegerField(
            required=False, min_value=0, max_value=99),
        'age_max': forms.IntegerField(
            required=False, min_value=1, max_value=100),
        'cost': forms.IntegerField(required=False),
        'cost_unit': forms.CharField(required=False, max_length=1),
        'province': forms.CharField(required=False, max_length=20),
        'city': forms.CharField(required=False, max_length=20),
        'county': forms.CharField(required=False, max_length=20),
        'time_started': forms.DateField(),
        'time_ended': forms.DateField(),
    })
    def create_outsource_need(self, request, lab, **kwargs):
        if check_bad_words(kwargs["title"]) or check_bad_words(kwargs["description"]):
            abort(403, '含有非法词汇')

        lab_needs = LabNeed.objects.filter(lab=lab, type=1)
        if lab_needs.count() == 0:
            lab.score += get_score_stage(2)
            lab.score_records.create(
                score=get_score_stage(2), type="初始数据",
                description="首次发布实验室需求")
            lab.save()

        n = lab.needs.create(type=1)
        for k in kwargs:
            setattr(n, k, kwargs[k])
        n.save()
        # 发布动态
        action.send_member_need(lab, n)
        # 增加积分
        request.user.score += get_score_stage(1)
        request.user.score_records.create(
            score=get_score_stage(1), type="能力",
            description="发布一个实验室需求")
        lab.score += get_score_stage(1)
        lab.score_records.create(
            score=get_score_stage(1), type="活跃度",
            description="发布一个实验室需求")
        request.user.save()
        lab.save()
        abort(200)

    @validate_args({
        'deadline': forms.DateField(),
        'title': forms.CharField(max_length=20),
        'description': forms.CharField(required=False, max_length=200),
        'field': forms.CharField(required=False, max_length=20),
        'skill': forms.CharField(required=False, max_length=20),
        'province': forms.CharField(required=False, max_length=20),
        'city': forms.CharField(required=False, max_length=20),
        'county': forms.CharField(required=False, max_length=20),
        'major': forms.CharField(required=False, max_length=20),
        'cost': forms.IntegerField(required=False),
        'cost_unit': forms.CharField(required=False, max_length=1),
        'time_started': forms.DateField(),
        'time_ended': forms.DateField(),
    })
    def create_undertake_need(self, request, lab, **kwargs):
        if check_bad_words(kwargs["title"]) or check_bad_words(kwargs["description"]):
            abort(403, '含有非法词汇')

        lab_needs = LabNeed.objects.filter(lab=lab, type=2)
        if lab_needs.count() == 0:
            lab.score += get_score_stage(2)
            lab.score_records.create(
                score=get_score_stage(2), type="初始数据",
                description="首次发布实验室需求")
            lab.save()

        n = lab.needs.create(type=2)
        for k in kwargs:
            setattr(n, k, kwargs[k])
        n.save()
        # 发布动态
        action.send_member_need(lab, n)
        # 增加积分
        request.user.score += get_score_stage(1)
        request.user.score_records.create(
            score=get_score_stage(1), type="能力",
            description="发布一个实验室需求")
        lab.score += get_score_stage(1)
        lab.score_records.create(
            score=get_score_stage(1), type="活跃度",
            description="发布一个实验室需求")
        request.user.save()
        lab.save()
        abort(200)


class Need(View):
    member_keys = ('id', 'title', 'description', 'number', 'age_min',
                   'age_max', 'gender', 'field', 'skill', 'degree', 'major',
                   'time_graduated', 'deadline', 'province', 'city', 'county')
    outsource_keys = ('id', 'title', 'description', 'number', 'age_min',
                      'age_max', 'gender', 'degree', 'field', 'skill', 'major',
                      'cost', 'cost_unit', 'time_started', 'time_ended',
                      'deadline', 'province', 'city', 'county')
    undertake_keys = ('id', 'title', 'description', 'field', 'skill', 'major',
                      'cost', 'cost_unit', 'time_started', 'time_ended',
                      'deadline', 'province', 'city', 'county')

    @fetch_object(LabNeed.objects, 'need')
    @app_auth
    def get(self, request, need):
        """获取需求详情

        :return:
            if type==0(人员需求)：
                id: 需求id
                title: 需求标题
                description: 需求描述
                lab_id: 实验室ID
                lab_name: 实验室名称
                icon_url: 实验室头像
                number: 所需人数
                age_min: 最小年龄
                age_max: 最大年龄
                gender: 性别要求
                field: 领域
                skill: 技能
                degree: 学历
                major: 专业
                province: 省
                city: 市
                county: 县\区
                members: 已加入成员
                time_graduated: 毕业时间
                deadline: 截止时间
            if type==1(外包需求):
                id: 需求id
                title: 需求标题
                description: 需求描述
                lab_id: 实验室ID
                lab_name: 实验室名称
                icon_url: 实验室头像
                number: 所需人数
                age_min: 最小年龄
                age_max: 最大年龄
                gender: 性别要求
                field: 领域
                skill: 技能
                degree: 学历
                major: 专业
                cost: 费用
                province: 省
                city: 市
                county: 县\区
                cost_unit: 费用单位
                members: 已加入实验室
                time_started: 任务开始时间
                time_ended: 任务结束时间
                deadline: 截止时间
            if type==2(承接需求):
                id: 需求id
                deadline: 截止时间
                title: 需求标题
                description: 需求描述
                lab_id: 实验室ID
                lab_name: 实验室名称
                icon_url: 实验室头像
                field: 领域
                skill: 技能
                major: 专业
                cost: 费用
                province: 省
                city: 市
                county: 县\区
                cost_unit: 费用单位
                members: 已加入实验室
                time_started: 任务开始时间
                time_ended: 任务结束时间
        """

        d = {'lab_id': need.lab.id, 'lab_name': need.lab.name}
        if need.type == 0:
            keys = self.member_keys
        elif need.type == 1:
            keys = self.outsource_keys
        elif need.type == 2:
            keys = self.undertake_keys
        else:
            abort(500)

        # noinspection PyUnboundLocalVariable
        for k in keys:
            d[k] = getattr(need, k)

        members = dict()
        if need.members:
            ids = need.members.split("|")
            for uid in ids:
                uid = int(uid)
                if need.type == 0:
                    members[uid] = User.enabled.get(id=uid).name
                else:
                    members[uid] = Lab.enabled.get(id=uid).name
        d['members'] = members
        d['icon_url'] = need.lab.icon
        return JsonResponse(d)

    @fetch_object(LabNeed.objects, 'need')
    @require_verification_token
    def post(self, request, need):
        """将需求标记成已满足"""

        if request.user != need.lab.owner:
            abort(403, '只有负责人可以操作')
        need.status = 1
        need.save()
        request.user.score += get_score_stage(1)
        request.user.score_records.create(
            score=get_score_stage(1), type="能力",
            description="将实验室需求标记为已满足")
        need.lab.score += get_score_stage(1)
        need.lab.score_records.create(
            score=get_score_stage(1), type="能力",
            description="将实验室需求标记为已满足")
        request.user.save()
        need.lab.save()
        abort(200)

    @fetch_object(LabNeed, 'need')
    @require_verification_token
    def delete(self, request, need):
        """将需求标记成已删除"""

        if request.user != need.lab.owner:
            abort(403, '只有负责人可以操作')
        need.status = 2
        need.save()
        abort(200)


class NeedSearch(View):
    @validate_args({
        'offset': forms.IntegerField(required=False, min_value=0),
        'limit': forms.IntegerField(required=False, min_value=0),
        'status': forms.IntegerField(required=False, min_value=0, max_value=2),
        'type': forms.IntegerField(required=False, min_value=0, max_value=2),
        'name': forms.CharField(max_length=20),
    })
    def get(self, request, name, type=None, status=None, offset=0, limit=10):
        """
        搜索发布中的需求列表

        :param offset: 偏移量
        :param name: 标题包含字段
        :param type: 需求的类型，默认为获取全部
        :param status: 需求状态，默认为获取全部
        :return:
            count: 需求总数
            list: 需求列表
                need_id: 需求ID
                lab_id: 实验室ID
                lab_name: 实验室名称
                icon_url: 实验室头像
                status: 需求状态
                type: 需求类型
                title: 需求标题
                number: 所需人数/实验室人数
                degree: 需求学历
                members: 需求的加入者
                time_created: 发布时间
        """
        qs = LabNeed.objects.filter(title__icontains=name)
        if status is not None:
            # 按需求状态搜索
            qs = qs.filter(status=status)
        if type is not None:
            # 按需求类别搜索
            qs = qs.filter(type=type)
        c = qs.count()
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
                        members[id] = Lab.enabled.get(id=id).name
            need_dic['id'] = n.id
            need_dic['lab_id'] = n.lab.id
            need_dic['lab_name'] = n.lab.name
            need_dic['number'] = n.number
            need_dic['icon_url'] = n.lab.icon
            need_dic['status'] = n.status
            need_dic['type'] = n.type
            need_dic['title'] = n.title
            need_dic['degree'] = n.degree
            need_dic['members'] = members
            need_dic['time_created'] = n.time_created
            l.append(need_dic)
        return JsonResponse({'count': c, 'list': l})


class NeedScreen(View):
    @validate_args({
        'offset': forms.IntegerField(required=False, min_value=0),
        'limit': forms.IntegerField(required=False, min_value=0),
        'status': forms.IntegerField(required=False, min_value=0, max_value=2),
        'type': forms.IntegerField(required=False, min_value=0, max_value=2),
        'name': forms.CharField(required=False, max_length=20),
        'province': forms.CharField(required=False, max_length=20),
        'city': forms.CharField(required=False, max_length=20),
        'county': forms.CharField(required=False, max_length=20),
        'number': forms.IntegerField(required=False, min_value=0),
        'degree': forms.CharField(required=False, max_length=20),
    })
    def get(self, request, type=None, status=None, offset=0, limit=10,
            **kwargs):
        """
        筛选发布中的需求列表

        :param offset: 起始量
        :param limit: 偏移量
        :param type: 需求的类型，默认为获取全部
        :param status: 需求状态，默认为获取全部
        :param kwargs:
                    name: 标题包含字段
                    province: 省
                    city: 市
                    county: 区\县
                    number: 需要人数
                    degree: 学历
        :return:
            count: 需求总数
            list: 需求列表
                need_id: 需求ID
                lab_id: 实验室ID
                lab_name: 实验室名称
                icon_url: 实验室头像
                status: 需求状态
                type: 需求类别
                title: 需求标题
                number: 所需人数/实验室人数
                degree: 需求学历
                members: 需求的加入者
                time_created: 发布时间
        """
        qs = LabNeed.objects.all()
        if status is not None:
            # 按需求状态筛选
            qs = qs.filter(status=status)
        if type is not None:
            # 按需求类别筛选
            qs = qs.filter(type=type)
        name = kwargs.pop('name', '')
        if name:
            # 按标题检索
            qs = qs.filter(title__icontains=name)

        province = kwargs.pop('province', '')
        if province:
            # 按省会筛选
            qs = qs.filter(province=province)
        city = kwargs.pop('city', '')
        if city:
            # 按城市筛选
            qs = qs.filter(city=city)
        county = kwargs.pop('county', '')
        if county:
            # 按区/县筛选
            qs = qs.filter(county=county)
        number = kwargs.pop('number', '')
        if number:
            # 按需求所需最多人数筛选
            qs = qs.filter(number__lte=number)
        degree = kwargs.pop('degree', '')
        if degree:
            # 按学历筛选
            qs = qs.filter(degree=degree)

        c = qs.count()
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
                        members[id] = Lab.enabled.get(id=id).name
            need_dic['id'] = n.id
            need_dic['lab_id'] = n.lab.id
            need_dic['lab_name'] = n.lab.name
            need_dic['number'] = n.number
            need_dic['icon_url'] = n.lab.icon
            need_dic['status'] = n.status
            need_dic['type'] = n.type
            need_dic['title'] = n.title
            need_dic['degree'] = n.degree
            need_dic['members'] = members
            need_dic['time_created'] = n.time_created
            l.append(need_dic)
        return JsonResponse({'count': c, 'list': l})


class NeedUserList(View):
    ORDERS = (
        'time_created',
        '-time_created',
        'name',
        '-name',
    )

    @fetch_object(LabNeed.objects, 'need')
    @app_auth
    @validate_args({
        'offset': forms.IntegerField(required=False, min_value=0),
        'limit': forms.IntegerField(required=False, min_value=0),
        'order': forms.IntegerField(required=False, min_value=0, max_value=3),
    })
    def get(self, request, need, offset=0, limit=10, order=1):
        """获取需求的成员列表

        :param offset: 偏移量
        :param order: 排序方式
            0: 成为成员时间升序
            1: 成为成员时间降序（默认值）
            2: 昵称升序
            3: 昵称降序
        :return:
            count: 成员总数
            list: 成员列表
                id: 用户ID
                username:用户名
                name: 用户昵称
                icon_url: 用户头像
                tags: 标签
                gender: 性别
                liker_count: 点赞数
                follower_count: 粉丝数
                visitor_count: 访问数
                time_created: 注册时间
        """
        i, j, k = offset, offset + limit, self.ORDERS[order]
        uids = []
        if need.members:
            ids = need.members.split("|")
            for uid in ids:
                uids.append(int(uid))
            members = User.enabled.filter(id__in=uids)
            c = members.count()
            rs = members.order_by(k)[i:j]
            l = [{'id': r.id,
                  'username': r.username,
                  'name': r.name,
                  'icon_url': r.icon,
                  'tags': [tag.name for tag in r.tags.all()],
                  'gender': r.gender,
                  'liker_count': r.likers.count(),
                  'follower_count': r.followers.count(),
                  'visitor_count': r.visitors.count(),
                  'time_created': r.time_created} for r in rs]
        else:
            c = 0
            l = []
        return JsonResponse({'count': c, 'list': l})


class NeedLabList(View):
    ORDERS = (
        'time_created',
        '-time_created',
        'name',
        '-name',
    )

    @fetch_object(LabNeed.objects, 'need')
    @app_auth
    @validate_args({
        'offset': forms.IntegerField(required=False, min_value=0),
        'limit': forms.IntegerField(required=False, min_value=0),
        'order': forms.IntegerField(required=False, min_value=0, max_value=3),
    })
    def get(self, request, need, offset=0, limit=10, order=1):
        """获取需求的成员列表

        :param offset: 偏移量
        :param order: 排序方式
            0: 成为成员时间升序
            1: 成为成员时间降序（默认值）
            2: 昵称升序
            3: 昵称降序
        :return:
            count: 成员总数
            list: 成员列表
                id: 实验室ID
                name: 实验室昵称
                icon_url: 实验室头像
                owner_id: 创建者ID
                liker_count: 点赞数
                visitor_count: 最近7天访问数
                member_count: 实验室成员人数
                fields: 所属领域，格式：['field1', 'field2']
                tags: 标签，格式：['tag1', 'tag2', ...]
                time_created: 注册时间
        """
        i, j, k = offset, offset + limit, self.ORDERS[order]
        tids = []
        if need.members:
            ids = need.members.split("|")
            for tid in ids:
                tids.append(int(tid))
            members = Lab.enabled.filter(id__in=tids)
            c = members.count()
            rs = members.order_by(k)[i:j]
            l = [{'id': r.id,
                  'name': r.name,
                  'icon_url': r.icon,
                  'owner_id': r.owner.id,
                  'liker_count': r.likers.count(),
                  'visitor_count': r.visitors.count(),
                  'member_count': r.members.count(),
                  'fields': [r.field1, r.field2],
                  'tags': [tag.name for tag in r.tags.all()],
                  'time_created': r.time_created} for r in rs]
        else:
            c = 0
            l = []
        return JsonResponse({'count': c, 'list': l})


class MemberNeedRequestList(View):
    @fetch_object(LabNeed.objects, 'need')
    @app_auth
    @validate_args({
        'offset': forms.IntegerField(required=False, min_value=0),
        'limit': forms.IntegerField(required=False, min_value=0),
    })
    def get(self, request, need, offset=0, limit=10):
        """获取人员需求的加入申请列表

        :param offset: 偏移量
        :return: request.user 不为实验室创始人时，404
        :return: request.user 为实验室创始人时
            count: 申请总数
            list: 申请列表
                id: 申请者ID
                username: 申请者用户名
                name: 申请者昵称
                icon_url: 申请者头像
                description: 备注
                time_created: 申请时间
        """
        if request.user == need.lab.owner:
            # 拉取人员需求下实验室的加入申请信息
            c = need.member_requests.count()
            qs = need.member_requests.all()[offset:offset + limit]

            l = [{'id': r.sender.id,
                  'username': r.sender.username,
                  'name': r.sender.name,
                  'icon_url': r.sender.icon,
                  'description': r.description,
                  'time_created': r.time_created} for r in qs]
            return JsonResponse({'count': c, 'list': l})
        abort(404, '只有负责人可以操作')

    @fetch_object(LabNeed.objects, 'need')
    @require_verification_token
    @validate_args({
        'description': forms.CharField(required=False, max_length=100),
    })
    def post(self, request, need, description=''):
        """向人员需求发出加入申请

        :param description: 附带消息
        """
        if request.user == need.lab.owner:
            abort(403, '负责人不能操作')

        if need.lab.members.filter(user=request.user).exists():
            abort(403, '已经是对方实验室成员')

        if need.lab.member_requests.filter(user=request.user).exists():
            abort(200)

        if need.lab.invitations.filter(user=request.user).exists():
            abort(403, '对方实验室已经发送邀请')

        need.member_requests.create(sender=request.user,
                                    description=description)
        abort(200)


class MemberNeedRequest(View):
    @fetch_object(LabNeed.objects, 'need')
    @fetch_object(User.enabled, 'user')
    @require_verification_token
    def post(self, request, need, user):
        """将目标用户添加为自己的实验室成员（对方需发送过人员需求下的加入实验室申请）"""

        if request.user != need.lab.owner:
            abort(403, '只有负责人可以操作')

        if not need.member_requests.filter(sender=user):
            abort(403, '对方未发送申请')

        # 若对方已是实验室成员则不做处理
        if need.lab.members.filter(user=user).exists():
            abort(200)

        # 在事务中建立关系，并删除对应的加实验室申请
        with transaction.atomic():
            need.member_requests.filter(sender=user).delete()
            # 保存需求的加入成员Id
            if len(need.members) > 0:
                need.members = need.members + "|" + str(user.id)
            else:
                need.members = str(user.id)
            need.save()
            need.lab.members.create(user=user)
            # action.join_lab(user, need.lab)
            # 积分
            request.user.score += get_score_stage(1)
            request.user.score_records.create(
                score=get_score_stage(1), type="能力", description="加入实验室成功")
            need.lab.score += get_score_stage(1)
            need.lab.score_records.create(
                score=get_score_stage(1), type="能力",
                description="成功招募一个成员")
            request.user.save()
            need.lab.save()
        abort(200)

    @fetch_object(LabNeed.objects, 'need')
    @fetch_object(User.enabled, 'user')
    @require_verification_token
    def delete(self, request, need, user):
        """忽略某用户人员需求下的加实验室请求"""

        if request.user != need.lab.owner:
            abort(403, '只有负责人可以操作')

        qs = need.member_requests.filter(sender=user)
        if not qs.exists():
            abort(404, '申请不存在')
        qs.delete()
        abort(200)


class NeedRequestList(View):
    @fetch_object(LabNeed.objects, 'need')
    @fetch_object(Lab.enabled, 'lab')
    @app_auth
    @validate_args({
        'offset': forms.IntegerField(required=False, min_value=0),
        'limit': forms.IntegerField(required=False, min_value=0),
    })
    def get(self, request, need, lab, offset=0, limit=10):
        """获取需求的合作申请列表

        :param offset: 偏移量
        :return: request.user 不为实验室创始人时，404
        :return: request.user 为实验室创始人时
            count: 申请总数
            list: 申请列表
                id: 申请者ID
                lab_id: 申请实验室ID
                name: 申请实验室名称
                icon_url: 申请实验室头像
                time_created: 申请时间
        """
        if request.user == need.lab.owner and need.lab == lab:
            # 拉取需求的申请合作信息
            c = need.cooperation_requests.count()
            qs = need.cooperation_requests.all()[offset:offset + limit]

            l = [{'id': r.sender.owner.id,
                  'lab_id': r.sender.id,
                  'name': r.sender.name,
                  'icon_url': r.sender.icon,
                  'time_created': r.time_created} for r in qs]
            return JsonResponse({'count': c, 'list': l})
        abort(404, '只有负责人可以操作')

    @fetch_object(LabNeed.objects, 'need')
    @fetch_object(Lab.enabled, 'lab')
    @require_verification_token
    def post(self, request, need, lab):
        """向需求发出合作申请

        """
        if need.cooperation_requests.filter(sender=lab).exists():
            abort(404, '合作申请已经发送过')
        if need.cooperation_invitations.filter(invitee=lab).exists():
            abort(404, '合作申请已经发送过')
        if request.user == lab.owner:
            need.cooperation_requests.create(sender=lab)
            abort(200)
        abort(404, '只有负责人能操作')


class NeedRequest(View):
    @fetch_object(Lab.enabled, 'lab')
    @app_auth
    @validate_args({
        'offset': forms.IntegerField(required=False, min_value=0),
        'limit': forms.IntegerField(required=False, min_value=0),
    })
    def get(self, request, lab, offset=0, limit=10):
        """获取实验室发出的的合作申请列表

        :param offset: 偏移量
        :return: request.user 不为实验室创始人时，404
        :return: request.user 为实验室创始人时
            count: 申请总数
            list: 申请列表
                lab_id: 申请的实验室ID
                need_id: 申请的需求ID
                title: 申请的需求标题
                name: 申请实验室名称
                icon_url: 申请实验室头像
                time_created: 申请时间
        """
        if request.user == lab.owner:
            # 拉取申请合作信息
            c = lab.cooperation_requests.count()
            qs = lab.cooperation_requests.all()[offset:offset + limit]

            l = [{'lab_id': r.need.lab.id,
                  'id': r.need.id,
                  'name': r.need.lab.name,
                  'title': r.need.title,
                  'icon_url': r.need.lab.icon,
                  'time_created': r.time_created} for r in qs]
            return JsonResponse({'count': c, 'list': l})
        abort(404, '只有负责人能操作')

    @fetch_object(LabNeed.objects, 'need')
    @fetch_object(Lab.enabled, 'lab')
    @require_verification_token
    def post(self, request, need, lab):
        """同意加入申请并将创始人加入自己实验室（对方需发送过合作申请）"""

        if request.user != need.lab.owner:
            abort(404, '只有负责人能操作')

        if need.cooperation_requests.filter(sender=lab).exists():
            # 在事务中建立关系，并删除对应的申请合作
            with transaction.atomic():
                need.cooperation_requests.filter(sender=lab).delete()
                if need.lab.members.filter(user=lab.owner).exists():
                    abort(200)
                # 保存需求的加入实验室Id
                if len(need.members) > 0:
                    need.members = need.members + "|" + str(lab.id)
                else:
                    need.members = str(lab.id)
                need.save()

                need.lab.members.create(user=lab.owner)
                # action.join_lab(lab.owner, need.lab)
                request.user.score += get_score_stage(1)
                request.user.score_records.create(
                    score=get_score_stage(1), type="能力",
                    description="与其他实验室合作")
                lab.score += get_score_stage(1)
                lab.score_records.create(
                    score=get_score_stage(1), type="能力",
                    description="与其他实验室合作")
                request.user.save()
                lab.save()
            abort(200)
        abort(404, '对方未发送过申请合作')

    @fetch_object(LabNeed.objects, 'need')
    @fetch_object(Lab.enabled, 'lab')
    @require_verification_token
    def delete(self, request, need, lab):
        """忽略某实验室的合作申请"""

        if request.user != need.lab.owner:
            abort(403, '只有负责人可以操作')

        qs = need.cooperation_requests.filter(sender=lab)
        if not qs.exists():
            abort(404, '合作申请不存在')
        qs.delete()
        abort(200)


class NeedInvitationList(View):
    @fetch_object(LabNeed.objects, 'need')
    @fetch_object(Lab.enabled, 'lab')
    @app_auth
    @validate_args({
        'offset': forms.IntegerField(required=False, min_value=0),
        'limit': forms.IntegerField(required=False, min_value=0),
    })
    def get(self, request, need, lab, offset=0, limit=10):
        """获取需求的合作邀请列表

        :param offset: 偏移量
        :return: request.user 不为实验室创始人时，404
        :return: request.user 为实验室创始人时
            count: 邀请总数
            list: 邀请列表
                lab_id: 被邀请实验室ID
                name: 被邀请实验室名称
                icon_url: 被邀请实验室头像
                time_created: 邀请时间
        """
        if request.user == need.lab.owner and need.lab == lab:
            # 拉取邀请合作信息
            c = need.cooperation_invitations.count()
            qs = need.cooperation_invitations.all()[offset:offset + limit]

            l = [{'lab_id': r.invitee.id,
                  'name': r.invitee.name,
                  'icon_url': r.invitee.icon,
                  'time_created': r.time_created} for r in qs]
            return JsonResponse({'count': c, 'list': l})
        abort(404, '只有负责人可以操作')

    @fetch_object(LabNeed.objects, 'need')
    @fetch_object(Lab.enabled, 'lab')
    @require_verification_token
    def post(self, request, need, lab):
        """向实验室发出合作邀请

        """
        if need.cooperation_invitations.filter(invitee=lab).exists():
            abort(404, '已经发送过合作申请')
        if need.cooperation_requests.filter(sender=lab).exists():
            abort(404, '对方已经发送过合作申请')
        if request.user == lab.owner:
            need.cooperation_invitations.create(invitee=lab)
            abort(200)
        abort(404, '只有负责人可以操作')


class NeedInvitation(View):
    @fetch_object(Lab.enabled, 'lab')
    @app_auth
    @validate_args({
        'offset': forms.IntegerField(required=False, min_value=0),
        'limit': forms.IntegerField(required=False, min_value=0),
    })
    def get(self, request, lab, offset=0, limit=10):
        """获取当前实验室的需求合作邀请列表

        :param offset: 偏移量
        :return: request.user 不为实验室创始人时，404
        :return: request.user 为实验室创始人时
            count: 邀请总数
            list: 邀请列表
                lab_id: 邀请方实验室ID
                need_id: 邀请方需求ID
                title: 邀请方需求标题
                name: 邀请方实验室名称
                icon_url: 邀请方实验室头像
                time_created: 邀请时间
        """
        if request.user == lab.owner:
            # 拉取邀请合作信息
            c = lab.cooperation_invitations.count()
            qs = lab.cooperation_invitations.all()[offset:offset + limit]

            l = [{'lab_id': r.inviter.id,
                  'need_id': r.need.id,
                  'title': r.need.title,
                  'name': r.inviter.name,
                  'icon_url': r.invitee.icon,
                  'time_created': r.time_created} for r in qs]
            return JsonResponse({'count': c, 'list': l})
        abort(404, '只有负责人可以操作')

    @fetch_object(LabNeed.objects, 'need')
    @fetch_object(Lab.enabled, 'lab')
    @require_verification_token
    def post(self, request, need, lab):
        """同意邀请并将加入他人的实验室（对方需发送过合作邀请）"""

        if request.user != need.lab.owner:
            abort(404, '只有负责人可以操作')

        if need.cooperation_invitations.filter(invitee=lab).exists():
            # 在事务中建立关系，并删除对应的邀请合作
            with transaction.atomic():
                need.cooperation_invitations.filter(invitee=lab).delete()
                if need.lab.members.filter(user=lab.owner).exists():
                    abort(200)
                # 保存需求的加入实验室Id
                if len(need.members) > 0:
                    need.members = need.members + "|" + str(lab.id)
                else:
                    need.members = str(lab.id)
                need.save()
                need.lab.members.create(user=lab.owner)
                # action.join_lab(lab.owner, need.lab)
                request.user.score += get_score_stage(1)
                request.user.score_records.create(
                    score=get_score_stage(1), type="能力",
                    description="与其他实验室合作")
                lab.score += get_score_stage(1)
                lab.score_records.create(
                    score=get_score_stage(1), type="能力",
                    description="与其他实验室合作")
                request.user.save()
                lab.save()
            abort(200)
        abort(404, '邀请合作不存在')

    @fetch_object(LabNeed.objects, 'need')
    @fetch_object(Lab.enabled, 'lab')
    @require_verification_token
    def delete(self, request, need, lab):
        """忽略某来自需求的合作邀请"""

        if request.user != lab.owner:
            abort(403, '只有负责人可以操作')

        qs = need.cooperation_invitations.filter(invitee=lab)
        if not qs.exists():
            abort(404, '合作邀请不存在')
        qs.delete()
        abort(200)


class InternalTaskList(View):
    @fetch_object(Lab.enabled, 'lab')
    @app_auth
    @validate_args({
        'offset': forms.IntegerField(required=False, min_value=0),
        'limit': forms.IntegerField(required=False, min_value=0),
        'sign': forms.IntegerField(required=False, min_value=0, max_value=2),
    })
    def get(self, request, lab, sign=None, offset=0, limit=10):
        """获取实验室的内部任务列表
        :param offset: 偏移量
        :param sign: 任务状态 - 0: pending, 1: completed, 2: terminated
        :return:
            count: 任务总数
            list: 任务列表
                id: 任务ID
                status: 任务状态 - ('等待接受', 0), ('再派任务', 1),
                                  ('等待完成', 2), ('等待验收', 3),
                                  ('再次提交', 4), ('按时结束', 5),
                                  ('超时结束', 6), ('终止', 7)
                title: 任务标题
                executor_id: 执行者ID
                executor_name: 执行者昵称
                icon_url: 执行者头像
                time_created: 发布时间
        """
        qs = lab.internal_tasks
        if sign is not None:
            if sign == 0:
                qs = qs.filter(status__range=[0, 4])
            elif sign == 1:
                qs = qs.filter(status__in=[5, 6])
            else:
                qs = qs.filter(status=7)
            tasks = qs[offset:offset + limit]
        else:
            tasks = qs.all()[offset:offset + limit]
        c = qs.count()
        l = [{'id': t.id,
              'status': t.status,
              'title': t.title,
              'executor_id': t.executor.id,
              'executor_name': t.executor.name,
              'icon_url': t.executor.icon,
              'time_created': t.time_created} for t in tasks]
        return JsonResponse({'count': c, 'list': l})

    @fetch_object(Lab.enabled, 'lab')
    @require_verification_token
    @validate_args({
        'executor_id': forms.IntegerField(),
        'title': forms.CharField(max_length=20),
        'content': forms.CharField(max_length=200),
        'deadline': forms.DateField(),
    })
    def post(self, request, lab, **kwargs):
        """发布内部任务

        :param: executor_id: 执行者ID
        :param: title: 标题
        :param: content: 内容
        :param；deadline: 截止时间
        """
        if check_bad_words(kwargs["title"]) or check_bad_words(kwargs["content"]):
            abort(403, '含有非法词汇')
        if request.user != lab.owner:
            abort(403, '只有负责人可以操作')
        executor_id = kwargs.pop('executor_id')
        executor = None
        try:
            executor = User.enabled.get(id=executor_id)
        except ObjectDoesNotExist:
            abort(401, '执行者不存在')

        if not lab.members.filter(user=executor).exists():
            abort(404, '执行者非实验室成员')
        t = lab.internal_tasks.create(status=0, executor=executor,
                                      deadline=kwargs['deadline'])
        for k in kwargs:
            setattr(t, k, kwargs[k])
        t.save()
        request.user.score += get_score_stage(1)
        request.user.score_records.create(
            score=get_score_stage(1), type="能力",
            description="发布一个内部任务")
        lab.score += get_score_stage(1)
        lab.score_records.create(
            score=get_score_stage(1), type="活跃度",
            description="发布一个内部任务")
        request.user.save()
        lab.save()
        abort(200)


class InternalTasks(View):
    @app_auth
    @validate_args({
        'offset': forms.IntegerField(required=False, min_value=0),
        'limit': forms.IntegerField(required=False, min_value=0),
        'sign': forms.IntegerField(required=False, min_value=0, max_value=2),
    })
    def get(self, request, sign=None, offset=0, limit=10):
        """获取用户的内部任务列表
        :param offset: 偏移量
        :param sign: 任务状态 - 0: pending, 1: completed, 2: terminated
        :return:
            count: 任务总数
            list: 任务列表
                id: 任务ID
                lab_id: 实验室ID
                lab_name: 实验室名称
                icon_url: 实验室头像
                status: 任务状态 - ('等待接受', 0), ('再派任务', 1),
                                  ('等待完成', 2), ('等待验收', 3),
                                  ('再次提交', 4), ('按时结束', 5),
                                  ('超时结束', 6), ('终止', 7)
                title: 任务标题
                time_created: 发布时间
        """
        qs = request.user.internal_tasks
        if sign is not None:
            if sign == 0:
                qs = qs.filter(status__range=[0, 4])
            elif sign == 1:
                qs = qs.filter(status__in=[5, 6])
            else:
                qs = qs.filter(status=7)
            tasks = qs[offset:offset + limit]
        else:
            tasks = qs.all()[offset:offset + limit]

        c = qs.count()
        l = [{'id': t.id,
              'lab_id': t.lab.id,
              'lab_name': t.lab.name,
              'icon_url': t.lab.icon,
              'status': t.status,
              'title': t.title,
              'time_created': t.time_created} for t in tasks]
        return JsonResponse({'count': c, 'list': l})

    @fetch_object(InternalTask.objects, 'task')
    @require_verification_token
    @validate_args({
        'title': forms.CharField(required=False, max_length=20),
        'content': forms.CharField(required=False, max_length=200),
        'deadline': forms.DateField(required=False),
    })
    def post(self, request, task, **kwargs):
        """再派任务状态下的任务修改
        :param task_id: 任务ID
        :param title: 任务标题
        :param content: 任务内容
        :param deadline: 任务期限

        """
        if check_bad_words(kwargs["title"]) or check_bad_words(kwargs["content"]):
            abort(403, '含有非法词汇')
        if request.user != task.lab.owner:
            abort(403, '不能给自己发送任务')
        if task.status != 1:
            abort(404, '任务状态错误')

        for k in kwargs:
            setattr(task, k, kwargs[k])
        task.save()
        abort(200)


class LabInternalTask(View):
    keys = ('id', 'title', 'content', 'status', 'deadline', 'assign_num',
            'submit_num', 'finish_time', 'time_created')

    @fetch_object(InternalTask.objects, 'task')
    @app_auth
    def get(self, request, task):
        """获取内部任务详情

        :return:
            id: 任务id
            executor_id: 执行者ID
            executor_name: 执行者名称
            lab_id: 实验室ID
            lab_name: 实验室名称
            icon_url: 实验室头像
            title: 任务标题
            content: 任务内容
            status: 任务状态 - ('等待接受', 0), ('再派任务', 1),
                              ('等待完成', 2), ('等待验收', 3),
                              ('再次提交', 4), ('按时结束', 5),
                              ('超时结束', 6), ('终止', 7)
            deadline: 任务期限
            assign_num: 任务分派次数
            submit_num: 任务提交次数
            finish_time: 任务完成时间
            time_created: 任务创建时间
        """

        d = {'executor_id': task.executor.id,
             'executor_name': task.executor.name,
             'lab_id': task.lab.id,
             'lab_name': task.lab.name,
             'icon_url': task.lab.icon}

        # noinspection PyUnboundLocalVariable
        for k in self.keys:
            d[k] = getattr(task, k)

        return JsonResponse(d)

    @fetch_object(InternalTask.objects, 'task')
    @require_verification_token
    @validate_args({
        'status': forms.IntegerField(required=False, min_value=0, max_value=7),
    })
    def post(self, request, task, status=None):
        """
        修改内部任务的状态(默认为None, 后台确认任务是按时还是超时完成)
        :param status:
        要修改的任务状态 - ('等待接受', 0), ('再派任务', 1),
                          ('等待完成', 2), ('等待验收', 3),
                          ('再次提交', 4), ('按时结束', 5),
                          ('超时结束', 6), ('终止', 7)
        """
        if request.user != task.lab.owner and request.user != task.executor:
            abort(403, '非法操作')

        # 任务已经终止，不允许操作
        if task.status == 7:
            abort(404, '任务已结束')

        if status is None:
            if request.user != task.lab.owner or task.status != 3:
                abort(403, '非法操作')
            task.finish_time = timezone.now()
            if task.finish_time.date() > task.deadline:
                task.status = 6
            else:
                task.status = 5
            # 积分
            task.executor.score += get_score_stage(1)
            task.executor.score_records.create(
                score=get_score_stage(1), type="能力",
                description="完成一个内部任务")
            task.lab.score += get_score_stage(1)
            task.lab.score_records.create(
                score=get_score_stage(1), type="能力",
                description="队友完成一个内部任务")
            task.executor.save()
            task.lab.save()
            task.save()
            abort(200)
        elif status == 0:
            if request.user != task.lab.owner or task.status != 1:
                abort(403, '非法操作')
            else:
                # 如果任务状态为再派任务-->等待接受，则分派次数+1
                task.assign_num += 1
        elif status == 1:
            if request.user != task.executor or task.status != 0:
                abort(403, '非法操作')
        elif status == 2:
            if request.user != task.executor or task.status != 0:
                abort(403, '非法操作')
        elif status == 3:
            if request.user != task.executor or (task.status not in [2, 4]):
                abort(403, '非法操作')
            elif task.status == 4:
                # 如果任务状态为再次提交-->等待验收，则提交次数+1
                task.submit_num += 1
        elif status == 4:
            if request.user != task.lab.owner or task.status != 3:
                abort(403, '非法操作')
        elif status == 7:
            if request.user != task.lab.owner or task.status != 1:
                abort(403, '非法操作')
        else:
            abort(403, '状态参数错误')

        task.status = status
        task.save()
        abort(200)


class ExternalTaskList(View):
    @fetch_object(Lab.enabled, 'lab')
    @app_auth
    @validate_args({
        'offset': forms.IntegerField(required=False, min_value=0),
        'limit': forms.IntegerField(required=False, min_value=0),
        'sign': forms.IntegerField(required=False, min_value=0, max_value=1),
        'type': forms.IntegerField(required=False, min_value=0, max_value=1),
    })
    def get(self, request, lab, sign=None, type=0, offset=0, limit=10):
        """获取实验室的外包/承接任务列表
        :param offset: 偏移量
        :param type: 任务类型 - 0: outsource, 1: undertake
        :param sign: 任务状态 - 0: pending, 1: completed
        :return:
            count: 任务总数
            list: 任务列表
                if type==0（实验室的外包任务）
                    id: 任务ID
                    status: 任务状态 - ('等待接受', 0), ('再派任务', 1),
                                      ('等待完成', 2), ('等待验收', 3),
                                      ('再次提交', 4), ('等待支付', 6),
                                      ('再次支付', 7), ('等待确认', 8),
                                      ('按时结束', 9),('超时结束', 10)
                    title: 任务标题
                    executor_id: 执行实验室ID
                    executor_name: 执行实验室昵称
                    icon_url: 执行实验室头像
                    time_created: 发布时间
                if type==1（实验室的承接任务）
                    id: 任务ID
                    status: 任务状态 - ('等待接受', 0), ('再派任务', 1),
                                      ('等待完成', 2), ('等待验收', 3),
                                      ('再次提交', 4), ('等待支付', 6),
                                      ('再次支付', 7), ('等待确认', 8),
                                      ('按时结束', 9),('超时结束', 10)
                    title: 任务标题
                    lab_id: 外包实验室ID
                    lab_name: 外包实验室昵称
                    icon_url: 外包实验室头像
                    time_created: 发布时间
        """
        if type == 0:
            qs = lab.outsource_external_tasks
            if sign is not None:
                if sign == 0:
                    qs = qs.filter(status__range=[0, 8])
                else:
                    qs = qs.filter(status__in=[9, 10])
                tasks = qs[offset:offset + limit]
            else:
                tasks = qs.all()[offset:offset + limit]
            c = qs.count()
            l = [{'id': t.id,
                  'status': t.status,
                  'title': t.title,
                  'executor_id': t.executor.id,
                  'executor_name': t.executor.name,
                  'icon_url': t.executor.icon,
                  'time_created': t.time_created} for t in tasks]
            return JsonResponse({'count': c, 'list': l})
        else:
            qs = lab.undertake_external_tasks
            if sign is not None:
                if sign == 0:
                    qs = qs.filter(status__range=[0, 8])
                else:
                    qs = qs.filter(status__in=[9, 10])

            c = qs.count()
            tasks = qs[offset:offset + limit]
            l = [{'id': t.id,
                  'status': t.status,
                  'title': t.title,
                  'lab_id': t.lab.id,
                  'lab_name': t.lab.name,
                  'icon_url': t.lab.icon,
                  'time_created': t.time_created} for t in tasks]
            return JsonResponse({'count': c, 'list': l})

    @fetch_object(Lab.enabled, 'lab')
    @require_verification_token
    @validate_args({
        'executor_id': forms.IntegerField(),
        'title': forms.CharField(max_length=20),
        'content': forms.CharField(max_length=200),
        'expend': forms.IntegerField(required=False, min_value=1),
        'deadline': forms.DateField(),
    })
    def post(self, request, lab, **kwargs):
        """发布外包任务

        :param: executor_id: 执行者ID
        :param: title: 标题
        :param: content: 内容
        :param: expend: 预计费用
        :param；deadline: 截止时间
        """
        if check_bad_words(kwargs["title"]) or check_bad_words(kwargs["content"]):
            abort(403, '含有非法词汇')
        if request.user != lab.owner:
            abort(403, '只有负责人可以操作')
        executor_id = kwargs.pop('executor_id')
        executor = None
        try:
            executor = Lab.enabled.get(id=executor_id)
        except ObjectDoesNotExist:
            abort(403, '执行者不存在')

        if not lab.members.filter(user=executor.owner).exists():
            abort(404, '执行者非实验室成员')
        t = lab.outsource_external_tasks.create(
            status=0, executor=executor, deadline=kwargs['deadline'])
        for k in kwargs:
            setattr(t, k, kwargs[k])
        t.save()
        request.user.score += get_score_stage(1)
        request.user.score_records.create(
            score=get_score_stage(1), type="能力",
            description="发布一个外部任务")
        lab.score += get_score_stage(1)
        lab.score_records.create(
            score=get_score_stage(1), type="能力",
            description="发布一个外部任务")
        request.user.save()
        lab.save()
        abort(200)


class ExternalTasks(View):
    @fetch_object(ExternalTask.objects, 'task')
    @require_verification_token
    @validate_args({
        'title': forms.CharField(required=False, max_length=20),
        'content': forms.CharField(required=False, max_length=200),
        'deadline': forms.DateField(required=False),
        'expend': forms.IntegerField(required=False, min_value=1),
    })
    def post(self, request, task, **kwargs):
        """再派任务状态下的任务修改
        :param task_id: 任务ID
        :param title: 任务标题
        :param content: 任务内容
        :param deadline: 任务期限

        """
        if check_bad_words(kwargs["title"]) or check_bad_words(kwargs["content"]):
            abort(403, '含有非法词汇')
        if request.user != task.lab.owner:
            abort(403, '只有负责人可以操作')
        if task.status != 1:
            abort(404, '任务状态错误')

        for k in kwargs:
            setattr(task, k, kwargs[k])
        task.save()
        abort(200)


class LabExternalTask(View):
    keys = ('id', 'title', 'content', 'status', 'expend', 'expend_actual',
            'deadline', 'assign_num', 'submit_num', 'pay_num', 'finish_time',
            'time_created')

    @fetch_object(ExternalTask.objects, 'task')
    @app_auth
    def get(self, request, task):
        """获取外部任务详情

        :return:
            id: 任务id
            executor_id: 执行实验室ID
            executor_name: 执行实验室名称
            lab_id: 实验室ID
            lab_name: 实验室名称
            icon_url: 实验室头像
            title: 任务标题
            content: 任务内容
            status: 任务状态 - ('等待接受', 0), ('再派任务', 1),
                              ('等待完成', 2), ('等待验收', 3),
                              ('再次提交', 4), ('等待支付', 6),
                              ('再次支付', 7), ('等待确认', 8),
                              ('按时结束', 9),('超时结束', 10)
            expend: 预计费用
            expend_actual: 实际费用
            assign_num: 分派次数
            submit_num: 提交次数
            pay_num: 支付次数
            deadline: 任务期限
            finish_time: 任务完成时间
            time_created: 任务创建时间
        """

        d = {'executor_id': task.executor.id,
             'executor_name': task.executor.name,
             'lab_id': task.lab.id,
             'lab_name': task.lab.name,
             'icon_url': task.lab.icon}

        # noinspection PyUnboundLocalVariable
        for k in self.keys:
            d[k] = getattr(task, k)

        return JsonResponse(d)

    @fetch_object(ExternalTask.objects, 'task')
    @require_verification_token
    @validate_args({
        'expend_actual': forms.IntegerField(required=False, min_value=0),
        'pay_time': forms.DateField(required=False),
        'status': forms.IntegerField(required=False, min_value=0, max_value=8),
    })
    def post(self, request, task, expend_actual=None, pay_time=None,
             status=None):
        """
        修改外部任务的状态(默认为None, 后台确认任务是按时还是超时完成)
        :param expend_actual: 实际支付金额(确认支付时传)
        :param pay_time: 支付时间(确认支付时传)
        :param status:
            任务状态 - ('等待接受', 0), ('再派任务', 1),
                      ('等待完成', 2), ('等待验收', 3),
                      ('再次提交', 4), ('等待支付', 6),
                      ('再次支付', 7), ('等待确认', 8),
                      ('按时结束', 9),('超时结束', 10)
        """
        if request.user != task.lab.owner \
                and request.user != task.executor.owner:
            abort(403, '非法操作')

        if status is None:
            if request.user != task.executor.owner or task.status != 8:
                abort(403, '非法操作')
            task.finish_time = timezone.now()
            if task.finish_time.date() > task.deadline:
                task.status = 10
            else:
                task.status = 9
            # 积分
            task.executor.score += get_score_stage(1)
            task.executor.score_records.create(
                score=get_score_stage(1), type="能力",
                description="完成一个外部任务")
            task.lab.score += get_score_stage(1)
            task.lab.score_records.create(
                score=get_score_stage(1), type="能力",
                description="队友完成一个外部任务")
            task.executor.save()
            task.lab.save()
            task.save()
            # 发动态
            action.finish_external_task(task.executor, task)
            abort(200)
        elif status == 0:
            if request.user != task.lab.owner or task.status != 1:
                abort(403, '非法操作')
            else:
                # 如果任务状态为再派任务-->等待接受，则分派次数+1
                task.assign_num += 1
        elif status == 1:
            if request.user != task.executor.owner or task.status != 0:
                abort(403, '非法操作')
        elif status == 2:
            if request.user != task.executor.owner or task.status != 0:
                abort(403, '非法操作')
        elif status == 3:
            if request.user != task.executor.owner \
                    or (task.status not in [2, 4]):
                abort(403, '非法操作')
            elif task.status == 4:
                # 如果任务状态为再次提交-->等待验收，则提交次数+1
                task.submit_num += 1
        elif status == 4:
            if request.user != task.lab.owner or task.status != 3:
                abort(403, '非法操作')
        elif status == 6:
            if request.user != task.lab.owner or task.status != 3:
                abort(403, '非法操作')
        elif status == 7:
            if request.user != task.executor.owner or task.status != 8:
                abort(403, '非法操作')
        elif status == 8:
            if request.user != task.lab.owner or (task.status not in [6, 7]):
                abort(403, '非法操作')
            elif task.status == 7:
                # 如果任务状态为再次支付-->等待确认，则支付次数+1
                task.pay_num += 1
            # 获取任务的支付信息
            if expend_actual is None or pay_time is None:
                abort(404, '参数不全')
            else:
                task.expend_actual = expend_actual
                task.pay_time = pay_time
        else:
            abort(403, '状态参数错误')

        task.status = status
        task.save()
        abort(200)


class CompetitionList(View):
    @fetch_object(Lab.enabled, 'lab')
    @app_auth
    @validate_args({
        'offset': forms.IntegerField(required=False, min_value=0),
        'limit': forms.IntegerField(required=False, min_value=0),
    })
    def get(self, request, lab, offset=0, limit=10):
        """获取实验室的竞赛列表"""
        '''
        r = CompetitionLabParticipator.objects.filter(lab=lab)
        c = r.count()
        qs = r[offset: offset + limit]
        l = [{'id': a.competition.id,
              'name': a.competition.name,
              'time_started': a.competition.time_started,
              'time_ended': a.competition.time_ended,
              'deadline': a.competition.deadline,
              'lab_participator_count':
                  a.competition.lab_participators.count(),
              'time_created': a.competition.time_created} for a in qs]
        return JsonResponse({'count': c, 'list': l})
        '''
        pass


class LabScoreRecord(View):
    ORDERS = ('time_created', '-time_created')

    @fetch_object(Lab.enabled, 'lab')
    @app_auth
    @validate_args({
        'offset': forms.IntegerField(required=False, min_value=0),
        'limit': forms.IntegerField(required=False, min_value=0),
        'order': forms.IntegerField(required=False, min_value=0, max_value=1),
    })
    def get(self, request, lab, offset=0, limit=10, order=1):
        """获取实验室的积分明细

        :param offset: 拉取的起始
        :param limit: 拉取的数量上限
        :return:
            count: 明细的总条数
            list:
                score: 积分
                type: 积分类型
                description: 描述
                time_created: 时间
        """
        k = self.ORDERS[order]
        r = lab.score_records.all()
        c = r.count()
        qs = r.order_by(k)[offset: offset + limit]
        l = [{'description': s.description,
              'score': s.score,
              'type': s.type,
              'time_created': s.time_created} for s in qs]
        return JsonResponse({'count': c, 'list': l})


class LabAwardList(View):
    @fetch_object(Lab.enabled, 'lab')
    @app_auth
    @validate_args({
        'offset': forms.IntegerField(required=False, min_value=0),
        'limit': forms.IntegerField(required=False, min_value=0),
    })
    def get(self, request, lab, offset=0, limit=10):
        """获取实验室参加的竞赛评比列表
        :param offset: 偏移量
        :param limit: 数量上限

        :return:
            count: 评比总数
            list: 评比列表
                id: 评比ID
                competition_id: 竞赛ID
                competition_name: 竞赛名称
                award: 获奖情况
                time_created: 创建时间
        """

        c = lab.awards.count()
        qs = lab.awards.all()[offset: offset + limit]
        l = [{'id': p.id,
              'competition_id': p.competition.id,
              'competition_name': p.competition.name,
              'award': p.award,
              'time_started': p.time_started} for p in qs]
        return JsonResponse({'count': c, 'list': l})


class LabActionCommentList(CommentList):
    @fetch_object(LabAction.objects, 'action')
    @app_auth
    def get(self, request, action):
        """获取团队动态的评论信息列表

        :return:
            count: 评论总数
            list: 评论列表
                id: 评论ID
                author_id: 评论者ID
                author_name: 评论者昵称
                icon_url: 头像
                content: 内容
                time_created: 发布时间
        """
        return super().get(request, action)

    @fetch_object(LabAction.objects, 'action')
    @require_verification_token
    def post(self, request, action):
        """当前用户对团队动态进行评论"""

        return super().post(request, action)


class ScreenLabActionList(View):
    @validate_args({
        'offset': forms.IntegerField(required=False, min_value=0),
        'limit': forms.IntegerField(required=False, min_value=0),
        'name': forms.CharField(required=False, max_length=20),
        'province': forms.CharField(required=False, max_length=20),
        'city': forms.CharField(required=False, max_length=20),
        'county': forms.CharField(required=False, max_length=20),
        'field': forms.CharField(required=False, max_length=10),
        'action': forms.CharField(required=False, max_length=20),
    })
    def get(self, request, offset=0, limit=10, **kwargs):
        """筛选与团队名或者动态名相关的动态列表

        :param offset: 偏移量
        :param limit: 数量上限
        :param kwargs: 筛选条件
            name: 团队名或动态名包含字段
            province: 主体的省
            city: 主体的市
            county: 主体的区/县
            field: 领域
            action: 动态动作

        :return:
            count: 动态总数（包括标记为disabled的内容）
            last_time_created: 最近更新时间
            list: 动态列表
                action_id: 动态id
                id: 主语的id
                name: 主语的名称
                icon: 主语的头像
                action: 相关动作
                object_type: 相关对象的类型
                object_id: 相关对象的ID
                object_name: 相关对象名称
                icon_url: 头像
                related_object_type: 额外相关对象的类型
                related_object_id: 额外相关对象的ID
                related_object_name: 额外相关对象的名称
                liker_count: 点赞数
                comment_count: 评论数
                time_created: 创建时间
        """

        r = Labction.objects
        name = kwargs.pop('name', '')
        if name:
            # 按用户昵称或动态名检索
            r = r.filter(Q(entity__name__icontains=name) |
                         Q(action__icontains=name))
        province = kwargs.pop('province', '')
        if province:
            # 按省会筛选
            r = r.filter(entity__province=province)
        city = kwargs.pop('city', '')
        if city:
            # 按城市筛选
            r = r.filter(entity__city=city)
        county = kwargs.pop('county', '')
        if county:
            # 按区/县筛选
            r = r.filter(entity__county=county)
        field = kwargs.pop('field', '')
        if field:
            # 按机构筛选
            r = r.filter(entity__field=field)
        act = kwargs.pop('action', '')
        if act:
            # 按动作筛选
            r = r.filter(action__icontains=act)

        r = r.all()
        c = r.count()
        records = (i for i in r[offset:offset + limit])
        l = [{'id': i.entity.id,
              'action_id': i.id,
              'name': i.entity.name,
              'icon': i.entity.icon,
              'action': i.action,
              'object_type': i.object_type,
              'object_id': i.object_id,
              'object_name': action.get_object_name(i),
              'icon_url': action.get_object_icon(i),
              'related_object_type': i.related_object_type,
              'related_object_id': i.related_object_id,
              'related_object_name': action.get_related_object_name(i),
              'liker_count': i.likers.count(),
              'comment_count': i.comments.count(),
              'time_created': i.time_created,
              } for i in records]
        return JsonResponse({'count': c, 'list': l})


class FollowedLabActionList(View):
    @app_auth
    @validate_args({
        'offset': forms.IntegerField(required=False, min_value=0),
        'limit': forms.IntegerField(required=False, min_value=0),
    })
    def get(self, request, offset=0, limit=10):
        """获取当前用户所关注的团队的动态列表

        :param offset: 偏移量
        :param limit: 数量上限
        :return:
            count: 动态总数（包括标记为disabled的内容）
            last_time_created: 最近更新时间
            list: 动态列表
                action_id: 动态id
                id: 主语的id
                name: 主语的名称
                icon: 主语的头像
                action: 相关动作
                object_type: 相关对象的类型
                object_id: 相关对象的ID
                object_name: 相关对象名称
                icon_url: 头像
                related_object_type: 额外相关对象的类型
                related_object_id: 额外相关对象的ID
                related_object_name: 额外相关对象的名称
                liker_count: 点赞数
                comment_count: 评论数
                time_created: 创建时间
        """

        r = LabAction.objects.filter(
            Q(entity__followers__follower=request.user))
        c = r.count()
        records = (i for i in r[offset:offset + limit])
        l = [{'id': i.entity.id,
              'action_id': i.id,
              'name': i.entity.name,
              'icon': i.entity.icon,
              'action': i.action,
              'object_type': i.object_type,
              'object_id': i.object_id,
              'object_name': action.get_object_name(i),
              'icon_url': action.get_object_icon(i),
              'related_object_type': i.related_object_type,
              'related_object_id': i.related_object_id,
              'related_object_name': action.get_related_object_name(i),
              'liker_count': i.likers.count(),
              'comment_count': i.comments.count(),
              'time_created': i.time_created,
              } for i in records]
        return JsonResponse({'count': c, 'list': l})


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


class LikedLab(ILikeSomething):
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


class LikedLabAction(ILikeSomething):
    @fetch_object(LabAction.objects, 'action')
    def get(self, request, action):
        return super().get(request, action)

    @fetch_object(LabAction.objects, 'action')
    def post(self, request, action):
        return super().post(request, action)

    @fetch_object(LabAction.objects, 'action')
    def delete(self, request, action):
        return super().delete(request, action)


class FavoredLabAction(IFavorSomething):
    @fetch_object(LabAction.objects, 'action')
    def get(self, request, action):
        return super().get(request, action)

    @fetch_object(LabAction.objects, 'action')
    def post(self, request, action):
        return super().post(request, action)

    @fetch_object(LabAction.objects, 'action')
    def delete(self, request, action):
        return super().delete(request, action)


class FavoredLabActionList(FavoredActionList):
    @app_auth
    def get(self, request):
        return super().get(request, request.user.favored_lab_actions)


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