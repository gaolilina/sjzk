from django import forms
from django.db.models import Q
from django.http import JsonResponse
from django.views.generic import View

from main.models import UserAction
from main.utils import action
from util.decorator.param import validate_args


class ScreenUserActionList(View):
    @validate_args({
        'offset': forms.IntegerField(required=False, min_value=0),
        'limit': forms.IntegerField(required=False, min_value=0),
        'name': forms.CharField(required=False, max_length=20),
        'gender': forms.IntegerField(required=False, min_value=0, max_value=2),
        'province': forms.CharField(required=False, max_length=20),
        'city': forms.CharField(required=False, max_length=20),
        'county': forms.CharField(required=False, max_length=20),
        'role': forms.CharField(required=False, max_length=20),
        'unit1': forms.CharField(required=False, max_length=20),
        'action': forms.CharField(required=False, max_length=20),
    })
    def get(self, request, offset=0, limit=10, **kwargs):
        """筛选与用户名或者动态名相关的动态列表

        :param offset: 偏移量
        :param limit: 数量上限
        :param kwargs: 筛选条件
            name: 用户名或动态名包含字段
            gender: 主体的性别
            province: 主体的省
            city: 主体的市
            county: 主体的区/县
            role: 主体的角色
            unit1: 主体的机构
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

        r = UserAction.objects
        name = kwargs.pop('name', '')
        if name:
            # 按用户昵称或动态名检索
            r = r.filter(Q(entity__name__icontains=name) |
                         Q(action__icontains=name))
        gender = kwargs.pop('gender', None)
        if gender is not None:
            # 按性别筛选
            r = r.filter(entity__gender=gender)
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
        role = kwargs.pop('role', '')
        if role:
            # 按角色筛选
            r = r.filter(entity__role=role)
        unit1 = kwargs.pop('unit1', '')
        if unit1:
            # 按机构筛选
            r = r.filter(entity__unit1=unit1)
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