from django import forms
from django.db import IntegrityError, transaction
from django.http import JsonResponse
from django.views.generic import View

from main.decorators import require_token, check_object_id, \
    validate_input, validate_json_input
from main.models import Team, User
from main.models.location import Location
from main.responses import *


class Teams(View):
    get_dict = {
        'offset': forms.IntegerField(required=False, min_value=0),
        'limit': forms.IntegerField(required=False, min_value=0),
        'order': forms.IntegerField(required=False, min_value=0, max_value=3),
    }
    available_orders = [
        'create_time', '-create_time',
        'name', '-name',
    ]

    @require_token
    @validate_input(get_dict)
    def get(self, request, offset=0, limit=10, order=1):
        """
        获取团队列表

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
                icon_url: 团队头像URL
                is_recruiting: 是否招募新成员
                create_time: 注册时间
        """
        i, j, k = offset, offset + limit, self.available_orders[order]
        c = Team.enabled.count()
        teams = Team.enabled.order_by(k)[i:j]
        l = [{'id': t.id,
              'name': t.name,
              'icon_url': t.icon_url,
              'is_recruiting': t.is_recruiting,
              'create_time': t.create_time} for t in teams]
        return JsonResponse({'count': c, 'list': l})

    post_dict = {
        'user_id': forms.IntegerField(min_value=0),
        'name': forms.CharField(),
        'description': forms.CharField(required=False),
    }

    @validate_input(post_dict)
    def post(self, request, user_id, name, description=''):
        """
        新建团队

        :param user_id: 用户id
        :param name: 团队名称
        :param description: 团队描述（默认为空）
        :return: 200 | 400 | 403
        """
        try:
            user = User.objects.get(id=user_id)
        except ValueError as e:
            return Http400(e)
        try:
            same_team_num = Team.enabled.filter(name=name).count()
        except ValueError as e:
            return Http400(e)
        if same_team_num > 0:
            return Http403('team already exists')
        try:
            Team.create(user, name, description=description)
            return Http200()
        except ValueError as e:
            return Http400(e)


class Profile(View):
    pass