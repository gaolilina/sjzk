from django import forms
from django.db import transaction
from django.http import JsonResponse, HttpResponseRedirect
from django.views.generic import View

from ChuangYi.settings import UPLOADED_URL
from main.models import Team
from main.utils import abort, save_uploaded_image
from main.utils.decorators import require_verification_token
from main.utils.dfa import check_bad_words
from main.utils.recommender import record_view_team
from util.decorator.auth import app_auth
from util.decorator.param import fetch_object, validate_args


class Profile(View):
    @app_auth
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
        r['group_id'] = team.group_id
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
                    abort(400, '团队名含非法词汇')
            if k == "description":
                if check_bad_words(kwargs['description']):
                    abort(400, '含有非法词汇')
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
        abort(500, '头像保存失败')


class TeamScoreRecord(View):
    ORDERS = ('time_created', '-time_created')

    @fetch_object(Team.enabled, 'team')
    @app_auth
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
        return JsonResponse({'count': c, 'list': l, 'code': 0})