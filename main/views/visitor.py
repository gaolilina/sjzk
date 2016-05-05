from datetime import datetime

from django import forms
from django.http import JsonResponse
from django.views.generic import View

from main.decorators import require_token, validate_input, check_object_id
from main.models import User


# todo: test
class Visitors(View):
    get_dict = {
        'offset': forms.IntegerField(required=False, min_value=0),
        'limit': forms.IntegerField(required=False, min_value=0),
    }

    @require_token
    @validate_input(get_dict)
    def get(self, request, obj, offset=0, limit=10, days=7):
        """
        获取对象一段时间内的访客列表

        :param offset: 偏移量
        :param limit: 数量上限
        :param days: 从几天前开始计算
        :return:
            count: 一段时间内的访客人数
            list: 访客列表
                id: 用户ID
                username: 用户名
                name: 用户昵称
                icon_url: 用户头像URL
                update_time: 来访时间
        """
        # 起始时间为days天前0时
        now = datetime.now()
        t = datetime(now.year, now.month, now.day - days)
        qs = obj.visitors.filter(update_time__gte=t)

        c = qs.count()

        i, j = offset, offset + limit
        qs = qs.all()[i:j]
        l = [{'id': i.visitor.id,
              'username': i.visitor.username,
              'name': i.visitor.name,
              'icon_url': i.visitor.icon_url,
              'update_time': i.update_time} for i in qs]

        return JsonResponse({'count': c, 'list': l})


# noinspection PyMethodOverriding
class UserVisitor(Visitors):
    @check_object_id(User.enabled, 'user')
    def get(self, request, user=None):
        if not user:
            user = request.user

        return super(UserVisitor, self).get(request, user)
