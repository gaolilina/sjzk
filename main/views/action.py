from django import forms
from django.http import JsonResponse
from django.views.generic import View

from ..models import User, Team
from ..utils.decorators import *


class Actions(View):
    @validate_args({
        'offset': forms.IntegerField(required=False, min_value=0),
    })
    def get(self, request, entity, offset=0, limit=10):
        """获取对象的动态列表

        :param offset: 偏移量
        :param limit: 数量上限
        :return:
            count: 动态总数（包括标记为disabled的内容）
            last_create_time: 最近更新时间
            list: 动态列表
                action: 相关动作
                object_type: 相关对象的类型
                object_id: 相关对象的ID
                related_object_type: 额外相关对象的类型
                related_object_id: 额外相关对象的ID
        """
        i, j = offset, offset + limit
        c = entity.actions.count()
        records = (i for i in entity.actions.all()[i:j] if i.is_enabled)
        l = [{'action': i.action,
              'object_type': i.object_type,
              'object_id': i.object_id,
              'object_name': i.object.name,
              'related_object_type': i.related_object_type,
              'related_object_id': i.related_object_id,
              'related_object_name': i.related_object.name,
              } for i in records]
        return JsonResponse({'count': c, 'list': l})


# noinspection PyMethodOverriding
class UserActions(Actions):
    @fetch_object(User, 'user')
    @require_token
    def get(self, request, user=None):
        user = user or request.user
        return super().get(request, user)


# noinspection PyMethodOverriding
class TeamActions(Actions):
    @fetch_object(Team, 'team')
    @require_token
    def get(self, request, team):
        return super(TeamActions, self).get(request, team)
