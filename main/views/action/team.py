from django import forms
from django.db.models import Q
from django.http import JsonResponse
from django.views.generic import View

from main.models import TeamAction
from main.utils import action
from util.decorator.auth import app_auth
from util.decorator.param import validate_args


class FollowedTeamActionList(View):
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

        r = TeamAction.objects.filter(
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


class ScreenTeamActionList(View):
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

        r = TeamAction.objects
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