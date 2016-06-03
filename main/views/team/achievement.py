from django import forms
from django.http import JsonResponse
from django.db import IntegrityError, transaction
from django.views.generic import View

from main.decorators import check_object_id, require_token, validate_input,\
    process_uploaded_image
from main.models import Team
from main.models.team.achievement import TeamAchievement
from main.responses import *


class Achievements(View):
    get_dict = {
        'offset': forms.IntegerField(required=False, min_value=0),
        'limit': forms.IntegerField(required=False, min_value=0),
        'order': forms.IntegerField(required=False, min_value=0, max_value=3),
    }
    available_orders = ('create_time', '-create_time')

    @require_token
    @validate_input(get_dict)
    def get(self, request, offset=0, limit=10, order=1):
        """
        获取所有团队发布的成果

        :param team_id: 团队ID
        :param offset: 偏移量
        :param limit: 数量上限
        :param order: 排序方式
            0: 发布时间升序
            1: 发布时间降序（默认值）
        :return:
            count: 成果总数
            list: 成果列表
                id: 成果ID
                team_id: 团队ID
                team_name: 团队名称
                description: 成果描述
                picture_url: 图片URL
                create_time: 发布时间
        """
        i, j, k = offset, offset + limit, self.available_orders[order]
        c = TeamAchievement.enabled.count()
        achievements = TeamAchievement.enabled.order_by(k)[i:j]
        l = [{'id': a.id,
              'team_id': a.team.id,
              'team_name': a.team.name,
              'description': a.description,
              'picture_url': a.picture_url,
              'create_time': a.create_time} for a in achievements]
        return JsonResponse({'count': c, 'list': l})


class Achievement(View):
    get_dict = {
        'offset': forms.IntegerField(required=False, min_value=0),
        'limit': forms.IntegerField(required=False, min_value=0),
        'order': forms.IntegerField(required=False, min_value=0, max_value=3),
    }
    available_orders = ('create_time', '-create_time')

    @check_object_id(Team.enabled, 'team')
    @require_token
    @validate_input(get_dict)
    def get(self, request, team, offset=0, limit=10, order=1):
        """
        获取团队发布的成果

        :param team_id: 团队ID
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
                picture_url: 图片URL
                create_time: 发布时间
        """
        i, j, k = offset, offset + limit, self.available_orders[order]
        c = TeamAchievement.enabled.filter(team=team).count()
        achievements = TeamAchievement.enabled.\
                           filter(team=team).order_by(k)[i:j]
        l = [{'id': a.id,
              'description': a.description,
              'picture_url': a.picture_url,
              'create_time': a.create_time} for a in achievements]
        return JsonResponse({'count': c, 'list': l})

    post_dict = {
        'description': forms.CharField(min_length=1, max_length=100)
    }

    @check_object_id(Team.enabled, 'team')
    @require_token
    @process_uploaded_image('picture')
    @validate_input(post_dict)
    def post(self, request, team, picture, description=''):
        """
        发布成果

        :param team_id: 团队ID
        :param description: 成果描述
        :param picture: 成果图片
        :return: achievement_id: 成果id
        """
        if request.user != team.owner:
            return Http403('recent user has no authority')
        if description.strip() == '':
            return Http400('require argument description')
        with transaction.atomic():
            achievement = TeamAchievement(team=team, description=description)
            achievement.picture = picture
            achievement.save()
            return JsonResponse({'achievement_id': achievement.id})

    @check_object_id(Team.enabled, 'team')
    @check_object_id(TeamAchievement.enabled, 'achievement')
    @require_token
    def delete(self, request, team, achievement):
        """
        删除成果

        :param team_id: 团队ID
        :param achievement_id: 成果ID
        """
        if request.user != team.owner:
            return Http403('recent user has no authority')
        if achievement.team != team:
            return Http400('related team need not exists')
        try:
            achievement.delete()
            return Http200()
        except IntegrityError:
            return Http400()
