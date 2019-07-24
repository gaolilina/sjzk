from django import forms
from django.db import transaction
from django.db.models import Q
from django.http import HttpResponseRedirect
from django.http import JsonResponse
from django.views.generic import View

from main.utils.recommender import calculate_ranking_score

from ChuangYi.settings import UPLOADED_URL
from main.models import Team, User, CompetitionTeamParticipator
from main.utils import abort, action, save_uploaded_image, get_score_stage
from main.utils.decorators import *
from main.utils.recommender import record_view_team
from main.utils.dfa import check_bad_words
import json
from main.utils.http import notify_user
from util.decorator.param import validate_args, fetch_object

__all__ = ('TeamCreate', 'Screen', 'Profile', 'Icon', 'MemberList',
           'Member', 'MemberRequestList', 'MemberRequest', 'Invitation',
           'CompetitionList', 'TeamScoreRecord', 'TeamAwardList')


class TeamCreate(View):
    ORDERS = ('time_created', '-time_created', 'name', '-name')

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
        """新建团队，同时调用融云接口为该团队创建一个对应的群聊

        :param kwargs:
            name: 团队名称
            description: 团队描述
            url: 团队链接
            province:
            city:
            county:
            fields: 团队领域，格式:'field1|field2'
            tags: 标签，格式：'tag1|tag2|tag3|...'
        :return: team_id: 团队id
        """
        name = kwargs.pop('name')
        fields = kwargs.pop('fields', None)
        tags = kwargs.pop('tags', None)

        # 昵称唯一性验证
        if Team.enabled.filter(name=name).count() != 0:
            abort(403, '团队名已被注册')
        # 昵称非法词验证
        if check_bad_words(name):
            abort(403, '团队名含非法词汇')

        team = Team(owner=request.user, name=name)
        team.save()

        for k in kwargs:
            setattr(team, k, kwargs[k])
        fields = fields.split('|')[:2] if fields is not None else ('', '')
        team.field1, team.field2 = fields[0].strip(), fields[1].strip()

        if tags:
            tags = tags.split('|')[:5]
            with transaction.atomic():
                team.tags.all().delete()
                order = 0
                for tag in tags:
                    tag = tag.strip()
                    if tag:
                        team.tags.create(name=tag, order=order)
                        order += 1
        team.save()

        action.create_team(request.user, team)
        request.user.score += get_score_stage(2)
        request.user.score_records.create(
            score=get_score_stage(2), type="能力", description="成功创建一个团队")
        request.user.save()
        return JsonResponse({'team_id': team.id})


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
        筛选团队

        :param offset: 偏移量
        :param limit: 数量上限
        :param order: 排序方式（若无则进行个性化排序）
            0: 注册时间升序
            1: 注册时间降序
            2: 昵称升序
            3: 昵称降序
        :param kwargs: 搜索条件
            name: 团队名包含字段
            province: 省
            city: 市
            county: 区/县
            field: 领域

        :return:
            count: 团队总数
            list: 团队列表
                id: 团队ID
                name: 团队名
                icon_url: 头像
                owner_id: 创建者ID
                liker_count: 点赞数
                visitor_count: 最近7天访问数
                member_count: 团队成员人数
                fields: 所属领域，格式：['field1', 'field2']
                tags: 标签，格式：['tag1', 'tag2', ...]
                time_created: 注册时间
        """
        teams = Team.enabled

        i, j = offset, offset + limit
        name = kwargs.pop('name', '')
        if name:
            # 按用户昵称段检索
            teams = teams.filter(name__icontains=name)

        province = kwargs.pop('province', '')
        if province:
            # 按省会筛选
            teams = teams.filter(province=province)
        city = kwargs.pop('city', '')
        if city:
            # 按城市筛选
            teams = teams.filter(city=city)
        county = kwargs.pop('county', '')
        if county:
            # 按区/县筛选
            teams = teams.filter(county=county)
        field = kwargs.pop('field', '')
        if field:
            # 按领域筛选
            teams = teams.filter(Q(field1=field) | Q(field2=field))

        teams = teams.all()
        c = teams.count()
        if order is not None:
            teams = teams.order_by(self.ORDERS[order])[i:j]
        else:
            # 将结果进行个性化排序
            team_list = list()
            for t in teams:
                if fetch_user_by_token(request):
                    team_list.append((t, calculate_ranking_score(request.user, t)))
                else:
                    team_list.append((t, 0))
            team_list = sorted(team_list, key=lambda x: x[1], reverse=True)
            teams = (t[0] for t in team_list[i:j])
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


class Profile(View):
    @require_token
    @fetch_object(Team.enabled, 'team')
    def get(self, request, team):
        """获取团队的基本资料

        :param: team_id : 团队ID
        :return:
            id: 团队ID
            name: 团队名
            icon_url: 头像
            owner_id: 创始人id
            time_created: 注册时间
            is_recruiting：是否招募新成员
            description: 团队简介
            url: 团队链接
            liker_count: 点赞数
            fan_count: 粉丝数
            visitor_count: 最近访客数
            advantage: 团队优势
            business_stage: 工商阶段
            financing_stage: 融资阶段
            valuation: 团队估值
            valuation_unit: 团队估值单位
            province:
            city:
            county:
            fields: 所属领域，格式：['field1', 'field2']
            tag_ids: 标签id，格式：[id1, id2, ...]
            tag_likers: 标签点赞数，格式：[count1, count2, ...]
            tags: 标签，格式：['tag1', 'tag2', ...]
            score: 积分
        """
        if team.owner != request.user:
            team.visitors.update_or_create(visitor=request.user)
            record_view_team(request.user, team)

        r = dict()
        r['id'] = team.id
        r['name'] = team.name
        r['icon_url'] = team.icon
        r['owner_id'] = team.owner.id
        r['time_created'] = team.time_created
        r['is_recruiting'] = team.is_recruiting
        r['description'] = team.description
        r['url'] = team.url
        r['liker_count'] = team.likers.count()
        r['fan_count'] = team.followers.count()
        r['visitor_count'] = team.visitors.count()
        r['fields'] = [team.field1, team.field2]
        r['advantage'] = team.advantage
        r['business_stage'] = team.business_stage
        r['financing_stage'] = team.financing_stage
        r['valuation'] = team.valuation
        r['valuation_unit'] = team.valuation_unit
        r['province'] = team.province
        r['city'] = team.city
        r['county'] = team.county
        r['score'] = team.score
        r['tag_ids'] = []
        r['tag_likers'] = []
        r['tags'] = []
        for t in team.tags.all():
            r['tag_ids'].append(t.id)
            r['tags'].append(t.name)
            r['tag_likers'].append(t.likers.count())

        return JsonResponse(r)

    @fetch_object(Team.enabled, 'team')
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
    def post(self, request, team, **kwargs):
        """修改团队资料

        :param team: 团队ID
        :param kwargs:
            name: 团队名
            description: 团队简介
            is_recruiting：是否招募新成员
            url: 团队链接
            advantage: 团队优势
            business_stage: 工商阶段
            financing_stage: 融资阶段
            valuation: 团队估值
            valuation_unit: 团队估值单位
            province:
            city:
            county:
            fields: 团队领域，格式:'field1|field2'
            tags: 标签，格式：'tag1|tag2|tag3|...'
        """
        if request.user != team.owner:
            abort(403, '只允许队长操作')

        fields = kwargs.pop('fields', None)
        tags = kwargs.pop('tags', None)

        for k in kwargs:
            if k == "name":
                name = kwargs['name']
                # 昵称唯一性验证
                if Team.enabled.filter(name=name).exclude(
                        id=team.id).count() != 0:
                    abort(403, '团队名已被注册')
                # 昵称非法词验证
                if check_bad_words(name):
                    abort(403, '团队名含非法词汇')
            if k == "description":
                if check_bad_words(kwargs['description']):
                    abort(403, '含有非法词汇')
            setattr(team, k, kwargs[k])

        if fields:
            fields = fields.split('|')[:2]
            if len(fields) < 2:
                fields.append('')
            team.field1, team.field2 = fields[0].strip(), fields[1].strip()

        if tags:
            tags = tags.split('|')[:5]
            with transaction.atomic():
                team.tags.all().delete()
                order = 0
                for tag in tags:
                    tag = tag.strip()
                    if tag:
                        team.tags.create(name=tag, order=order)
                        order += 1
        team.save()
        abort(200)


# noinspection PyUnusedLocal
class Icon(View):
    @fetch_object(Team.enabled, 'team')
    def get(self, request, team):
        """获取团队头像"""

        if team.icon:
            return HttpResponseRedirect(UPLOADED_URL + team.icon)
        abort(404, '未设置头像')

    @fetch_object(Team.enabled, 'team')
    @require_verification_token
    def post(self, request, team):
        """设置团队的头像"""

        if request.user != team.owner:
            abort(403, '只有队长可以操作')

        icon = request.FILES.get('image')
        if not icon:
            abort(400, '头像上传失败')

        filename = save_uploaded_image(icon)
        if filename:
            team.icon = filename
            team.save()
            return JsonResponse({'icon_url': team.icon})
        abort(400, '头像保存失败')


# noinspection PyUnusedLocal
class MemberList(View):
    ORDERS = (
        'time_created',
        '-time_created',
        'user__name',
        '-user__name',
    )

    @fetch_object(Team.enabled, 'team')
    @require_token
    @validate_args({
        'offset': forms.IntegerField(required=False, min_value=0),
        'limit': forms.IntegerField(required=False, min_value=0),
        'order': forms.IntegerField(required=False, min_value=0, max_value=3),
    })
    def get(self, request, team, offset=0, limit=10, order=1):
        """获取团队的成员列表

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
                time_created: 成为团队成员时间
        """

        i, j, k = offset, offset + limit, self.ORDERS[order]
        c = team.members.count()
        rs = team.members.order_by(k)[i:j]
        l = [{'id': r.user.id,
              'username': r.user.username,
              'icon_url': r.user.icon,
              'name': r.user.name,
              'time_created': r.time_created} for r in rs]
        return JsonResponse({'count': c, 'list': l})


# noinspection PyUnusedLocal
class Member(View):
    @fetch_object(Team.enabled, 'team')
    @fetch_object(User.enabled, 'user')
    @require_token
    def get(self, request, team, user):
        """检查用户是否为团队成员"""

        if team.members.filter(user=user).exists():
            abort(200)
        abort(404, '非团队成员')

    @fetch_object(Team.enabled, 'team')
    @fetch_object(User.enabled, 'user')
    @require_verification_token
    def post(self, request, team, user):
        """将目标用户添加为自己的团队成员（对方需发送过加入团队申请）"""

        if request.user != team.owner:
            abort(403, '只有队长能操作')

        if not team.member_requests.filter(user=user):
            abort(403, '该用户未发送过请求')

        # 若对方已是团队成员则不做处理
        if team.members.filter(user=user).exists():
            abort(200)

        # 在事务中建立关系，并删除对应的加团队申请
        with transaction.atomic():
            team.member_requests.filter(user=user).delete()
            team.members.create(user=user)
            action.join_team(user, team)
        abort(200)

    @fetch_object(Team.enabled, 'team')
    @fetch_object(User.enabled, 'user')
    @require_verification_token
    def delete(self, request, team, user):
        """退出团队(默认)/删除成员"""
        if user == team.owner:
            abort(403, "队长不能退出")

        qs = team.members.filter(user=user)
        if qs.exists():
            qs.delete()
            abort(200)
        abort(404, '成员不存在')


class MemberRequestList(View):
    @fetch_object(Team.enabled, 'team')
    @validate_args({
        'offset': forms.IntegerField(required=False),
        'limit': forms.IntegerField(required=False, min_value=0),
    })
    @require_token
    def get(self, request, team, offset=0, limit=10):
        """获取团队的加入申请列表

        * 若当前用户为团队创始人时，按请求时间逆序获取收到的加团队申请信息，
          拉取后的申请 标记为已读
        * 若不为团队创始人时，检查当前用户是否已经发送过加团队请求，
          并且该请求未被处理（接收或忽略）

        :param limit: 拉取的数量上限
        :return: request.user 为团队创始人时，200 | 404
        :return: request.user 不为团队创始人时
            count: 申请总条数
            list: 加入团队请求信息列表
                id: 用户ID
                username: 用户名
                name: 用户昵称
                icon_url: 用户头像
                description: 附带消息
                time_created: 请求发出的时间
        """
        if request.user == team.owner:
            # 拉取团队的加入申请信息
            c = team.member_requests.count()
            qs = team.member_requests.all()[offset:offset + limit]

            l = [{'id': r.user.id,
                  'username': r.user.username,
                  'name': r.user.name,
                  'icon_url': r.user.icon,
                  'description': r.description,
                  'time_created': r.time_created} for r in qs]
            return JsonResponse({'count': c, 'list': l})

    @fetch_object(Team.enabled, 'team')
    @require_verification_token
    @validate_args({
        'description': forms.CharField(required=False, max_length=100),
    })
    def post(self, request, team, description=''):
        """向团队发出加入申请

        :param description: 附带消息
        """
        if request.user == team.owner:
            abort(403, '队长不能申请')

        if team.members.filter(user=request.user).exists():
            abort(403, '已经发送过申请')

        if team.member_requests.filter(user=request.user).exists():
            abort(200)

        if team.invitations.filter(user=request.user).exists():
            abort(403, '团队已经发送过邀请')

        for need in team.needs.all():
            if need.member_requests.filter(sender=request.user).exists():
                abort(403, '已经发送过申请')

        team.member_requests.create(user=request.user, description=description)
        abort(200)


class MemberRequest(View):
    @fetch_object(Team.enabled, 'team')
    @fetch_object(User.enabled, 'user')
    @require_token
    def delete(self, request, team, user):
        """忽略某用户的加团队请求"""

        if request.user != team.owner:
            abort(403, '只有队长可以操作')

        qs = team.member_requests.filter(user=user)
        if not qs.exists():
            abort(404, '申请不存在')
        qs.delete()
        abort(200)


class Invitation(View):
    @fetch_object(Team.enabled, 'team')
    @fetch_object(User.enabled, 'user')
    @require_verification_token
    @validate_args({
        'description': forms.CharField(required=False, max_length=100),
    })
    def post(self, request, team, user, description=''):
        """向用户发出加入团队邀请

        :param description: 附带消息
        """
        if request.user != team.owner:
            abort(403, '只有队长可以操作')

        if user == team.owner:
            abort(403, '对方是本团队队长')

        if team.members.filter(user=user).exists():
            abort(403, '对方已经是团队成员')

        if team.invitations.filter(user=user).exists():
            abort(200)

        if team.member_requests.filter(user=user).exists():
            abort(403, '对方已经发送过申请')

        for need in team.needs.all():
            if need.member_requests.filter(sender=request.user).exists():
                abort(403, '对方已经发送过申请')

        team.invitations.create(user=user, description=description)
        notify_user(user, json.dumps({
            'type': 'invitation'
        }))
        abort(200)


# noinspection PyUnusedLocal
class CompetitionList(View):
    @fetch_object(Team.enabled, 'team')
    @require_token
    @validate_args({
        'offset': forms.IntegerField(required=False, min_value=0),
        'limit': forms.IntegerField(required=False, min_value=0),
    })
    def get(self, request, team, offset=0, limit=10):
        """获取团队的竞赛列表"""

        r = CompetitionTeamParticipator.objects.filter(team=team)
        c = r.count()
        qs = r[offset: offset + limit]
        l = [{'id': a.competition.id,
              'name': a.competition.name,
              'time_started': a.competition.time_started,
              'time_ended': a.competition.time_ended,
              'deadline': a.competition.deadline,
              'team_participator_count':
                  a.competition.team_participators.count(),
              'time_created': a.competition.time_created} for a in qs]
        return JsonResponse({'count': c, 'list': l})


class TeamScoreRecord(View):
    ORDERS = ('time_created', '-time_created')

    @fetch_object(Team.enabled, 'team')
    @require_token
    @validate_args({
        'offset': forms.IntegerField(required=False, min_value=0),
        'limit': forms.IntegerField(required=False, min_value=0),
        'order': forms.IntegerField(required=False, min_value=0, max_value=1),
    })
    def get(self, request, team, offset=0, limit=10, order=1):
        """获取团队的积分明细

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
        r = team.score_records.all()
        c = r.count()
        qs = r.order_by(k)[offset: offset + limit]
        l = [{'description': s.description,
              'score': s.score,
              'type': s.type,
              'time_created': s.time_created} for s in qs]
        return JsonResponse({'count': c, 'list': l})


class TeamAwardList(View):
    @fetch_object(Team.enabled, 'team')
    @require_token
    @validate_args({
        'offset': forms.IntegerField(required=False, min_value=0),
        'limit': forms.IntegerField(required=False, min_value=0),
    })
    def get(self, request, team, offset=0, limit=10):
        """获取团队参加的竞赛评比列表
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

        c = team.awards.count()
        qs = team.awards.all()[offset: offset + limit]
        l = [{'id': p.id,
              'competition_id': p.competition.id,
              'competition_name': p.competition.name,
              'award': p.award,
              'time_started': p.time_started} for p in qs]
        return JsonResponse({'count': c, 'list': l})
