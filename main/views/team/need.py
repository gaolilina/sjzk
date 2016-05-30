from django import forms
from django.db import IntegrityError, transaction
from django.views.generic import View
from django.http import JsonResponse

from main.decorators import require_token, check_object_id, \
    validate_input, validate_json_input
from main.models.team.need import TeamNeed
from main.models.location import TeamNeedLocation
from main.models.team import Team
from main.responses import *


class Needs(View):
    get_dict = {
        'offset': forms.IntegerField(required=False, min_value=0),
        'limit': forms.IntegerField(required=False, min_value=0),
        'order': forms.IntegerField(required=False, min_value=0, max_value=3),
    }
    available_orders = ('create_time', '-create_time', 'name', '-name')

    @require_token
    @validate_input(get_dict)
    def get(self, request, offset=0, limit=10, order=1):
        """
        获取所有团队发布的需求

        :param offset: 偏移量
        :param limit: 数量上限
        :param order: 排序方式
            0: 注册时间升序
            1: 注册时间降序（默认值）
            2: 昵称升序
            3: 昵称降序
        :return:
            count: 需求总数
            list: 需求列表
                id: 需求ID
                team_id: 团队ID
                team_name: 团队名称
                description: 需求描述
                status: 需求状态(未满足:0,已满足:1)
                number: 需求人数(若干:-1)
                gender: 性别要求(不限:0,男:1,女:2)
                location: 地区要求，格式：[province_id, city_id]
                create_time: 发布时间
        """
        i, j, k = offset, offset + limit, self.available_orders[order]
        c = TeamNeed.enabled.count()
        needs = TeamNeed.enabled.order_by(k)[i:j]
        l = [{'id': n.id,
              'team_id': n.team.id,
              'team_name': n.team.name,
              'description': n.description,
              'status': n.status,
              'number': n.number,
              'gender': n.gender,
              'location': TeamNeedLocation.objects.get_location(n),
              'create_time': n.create_time} for n in needs]
        return JsonResponse({'count': c, 'list': l})


class NeedSelf(View):
    get_dict = {
        'offset': forms.IntegerField(required=False, min_value=0),
        'limit': forms.IntegerField(required=False, min_value=0),
        'order': forms.IntegerField(required=False, min_value=0, max_value=3),
    }
    available_orders = ('create_time', '-create_time', 'name', '-name')

    @check_object_id(Team.enabled, 'team')
    @require_token
    @validate_input(get_dict)
    def get(self, request, team, offset=0, limit=10, order=1):
        """
        获取团队发布的需求

        :param team_id: 团队ID
        :param offset: 偏移量
        :param limit: 数量上限
        :param order: 排序方式
            0: 注册时间升序
            1: 注册时间降序（默认值）
            2: 昵称升序
            3: 昵称降序
        :return:
            count: 需求总数
            list: 需求列表
                id: 需求ID
                description: 需求描述
                status: 需求状态(未满足:0,已满足:1)
                number: 需求人数(若干:-1)
                gender: 性别要求(不限:0,男:1,女:2)
                location: 地区要求，格式：[province_id, city_id]
                create_time: 发布时间
        """
        i, j, k = offset, offset + limit, self.available_orders[order]
        c = TeamNeed.enabled.filter(team=team).count()
        needs = TeamNeed.enabled.filter(team=team).order_by(k)[i:j]
        l = [{'id': n.id,
              'description': n.description,
              'status': n.status,
              'number': n.number,
              'gender': n.gender,
              'location': TeamNeedLocation.objects.get_location(n),
              'create_time': n.create_time} for n in needs]
        return JsonResponse({'count': c, 'list': l})

    post_dict = {
        'description': forms.CharField(min_length=1, max_length=100),
        'number': forms.IntegerField(required=False, min_value=1),
        'gender': forms.IntegerField(required=False),
        'province': forms.CharField(required=False),
        'city': forms.CharField(required=False),
    }

    @check_object_id(Team.enabled, 'team')
    @require_token
    @validate_json_input(get_dict)
    def post(self, request, team, data):
        """
        发布需求

        :param team_id: 团队ID
        :param data:
            description: 需求描述
            number: 所需人数(默认为-1,若干)
            gender: 性别要求(默认为0,不限)
            location: 地区要求(默认为空,不限)，格式：[province_id, city_id]
        :return: need_id: 需求id
        """
        description = data.pop('description') if 'description' in data else ''
        number = data.pop('number') if 'number' in data else -1
        gender = data.pop('gender') if 'gender' in data else 0

        location = data.pop('location') if 'location' in data else None

        error = ''
        try:
            with transaction.atomic():
                need = TeamNeed.object.create(
                        team=team, description=description, number=number,
                        gender=gender)
                need.save()
                if location:
                    try:
                        TeamNeedLocation.objects.set_location(need, location)
                    except TypeError:
                        error = 'invalid location'
                        raise IntegrityError
                    except ValueError as e:
                        error = str(e)
                        raise IntegrityError
                return JsonResponse({'need_id': need.id})
        except IntegrityError:
            return Http400(error)

    @check_object_id(Team.enabled, 'team')
    @require_token
    def delete(self, request, team, need_id):
        """
        删除需求

        :param team_id: 团队ID
        :param need_id: 需求ID
        """
        if request.user != team.owner:
            return Http403('recent user has no authority')
        try:
            team.needs.get(id=need_id).delete()
            return Http200()
        except IntegrityError:
            return Http400('related team need not exists')
