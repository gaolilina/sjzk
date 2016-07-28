from django import forms
from django.http import JsonResponse
from django.views.generic import View

from main.models import User, Team
from main.utils.decorators import validate_args, fetch_object, require_token


class ObjectActions(View):
    get_dict = {
        'offset': forms.IntegerField(required=False, min_value=0),
        'limit': forms.IntegerField(required=False, min_value=0),
    }

    @validate_args(get_dict)
    def get(self, request, obj, offset=0, limit=10):
        """
        获取对象的动态列表

        :param offset: 偏移量
        :param limit: 数量上限
        :return:
            count: 动态总数（包括标记为disabled的内容）
            last_create_time: 最近更新时间
            list: 动态列表
                action: 相关动作
                object_type: 相关对象的类型
                object_id: 相关对象的ID
                object_name: 相关对象的名称
                related_object_type: 额外相关对象的类型
                related_object_id: 额外相关对象的ID
                related_object_name: 额外相关对象的名称
        """
        i, j = offset, offset + limit
        c = obj.actions.count()
        records = (i for i in obj.actions.all()[i:j] if i.is_enabled)
        l = [{'action': r.action,
              'object_type': r.object_type,
              'object_id': r.object_id,
              'object_name': r.object.name,
              'related_object_type': r.related_object_type,
              'related_object_id': r.related_object_id,
              'related_object_name': r.related_object.name,
              } for r in records]
        return JsonResponse({'count': c, 'list': l})


# noinspection PyMethodOverriding
class UserActions(ObjectActions):
    @fetch_object(User.enabled, 'user')
    @require_token
    def get(self, request, user=None):
        user = user or request.user
        return super(UserActions, self).get(request, user)


# noinspection PyMethodOverriding
class TeamActions(ObjectActions):
    @fetch_object(Team.enabled, 'team')
    @require_token
    def get(self, request, team):
        return super(TeamActions, self).get(request, team)
