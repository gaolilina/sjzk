from django import forms
from datetime import datetime, timedelta
from django.db import IntegrityError, transaction
from django.http import JsonResponse
from django.views.generic import View

from main.decorators import require_token, check_object_id, \
    validate_input, validate_json_input, process_uploaded_image
from main.models.location import TeamLocation
from main.models.tag import TeamTag
from main.models.like import TeamLiker
from main.models.team import Team, TeamProfile
from main.models.visitor import TeamVisitor
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
                owner_id: 创建者ID
                icon_url: 团队头像URL
                liker_count: 点赞数
                visitor_count: 最近7天访问数
                member_count: 团队成员人数
                fields: 所属领域，格式：['field1', 'field2']
                tags: 标签，格式：['tag1', 'tag2', ...]
                create_time: 注册时间
        """
        i, j, k = offset, offset + limit, self.available_orders[order]
        time = datetime.now() - timedelta(days=7)

        c = Team.enabled.count()
        teams = Team.enabled.order_by(k)[i:j]
        l = [{'id': t.id,
              'name': t.name,
              'icon_url': t.icon_url,
              'owner_id': t.owner.id,
              'liker_count': TeamLiker.enabled.filter(liked=t).count(),
              'visitor_count': t.visitor_records.filter(
                      update_time__gte=time).count(),
              'member_count': t.member_records.count(),
              'fields': TeamProfile.get_fields(t),
              'tags': TeamTag.objects.get_tags(t),
              'create_time': t.create_time} for t in teams]
        return JsonResponse({'count': c, 'list': l})


class TeamsSelf(View):
    get_dict = {
        'offset': forms.IntegerField(required=False, min_value=0),
        'limit': forms.IntegerField(required=False, min_value=0),
        'order': forms.IntegerField(required=False, min_value=0, max_value=3),
        'is_owner': forms.BooleanField(required=False),
    }
    available_orders = [
        'create_time', '-create_time',
        'name', '-name',
    ]

    @require_token
    @validate_input(get_dict)
    def get(self, request, offset=0, limit=10, order=1, is_owner=True):
        """
        获取自己创建（或参加）的团队列表
        :param offset: 偏移量
        :param limit: 数量上限
        :param order: 排序方式
            0: 注册时间升序
            1: 注册时间降序（默认值）
            2: 昵称升序
            3: 昵称降序
        :param is_owner: 是否为自己创建(默认为True)
            True：是
            False：否
        :return:
            count: 团队总数
            list: 团队列表
                id: 团队ID
                name: 团队名
                owner_id: 创建者ID
                icon_url: 团队头像URL
                liker_count: 点赞数
                visitor_count: 最近7天访问数
                member_count: 团队成员人数
                fields: 所属领域，格式：['field1', 'field2']
                tags: 标签，格式：['tag1', 'tag2', ...]
                create_time: 注册时间
        """
        i, j, k = offset, offset + limit, self.available_orders[order]
        time = datetime.now() - timedelta(days=7)

        if is_owner:
            c = Team.enabled.filter(owner=request.user).count()
            teams = Team.enabled.filter(owner=request.user).order_by(k)[i:j]
        else:
            c = Team.enabled.filter(member_records__member=request.user).count()
            teams = Team.enabled.filter(
                    member_records__member=request.user).order_by(k)[i:j]
        l = [{'id': t.id,
              'name': t.name,
              'icon_url': t.icon_url,
              'owner_id': t.owner.id,
              'liker_count': TeamLiker.enabled.filter(liked=t).count(),
              'visitor_count': t.visitor_records.filter(
                      update_time__gte=time).count(),
              'member_count': t.member_records.count(),
              'fields': TeamProfile.get_fields(t),
              'tags': TeamTag.objects.get_tags(t),
              'create_time': t.create_time} for t in teams]
        return JsonResponse({'count': c, 'list': l})

    post_dict = {
        'name': forms.CharField(),
    }

    @require_token
    @validate_json_input(post_dict)
    def post(self, request, data):
        """
        新建团队

        :param data:
            name: 团队名称
            description: 团队描述（默认为空）
            url: 团队链接（默认为空）
            location: 所在地区（默认为空），格式：[province, city, county]
            fields: 团队领域（默认为空,最多2个），格式:['field1', 'field2']
            tags: 标签（默认为空），格式：['tag1', 'tag2', ...]
        :return: team_id: 团队id
        """
        name = data['name']
        description = data.pop('description') if 'description' in data else ''
        url = data.pop('url') if 'url' in data else ''

        location = data.pop('location') if 'location' in data else None
        fields = data.pop('fields') if 'fields' in data else None
        tags = data.pop('tags') if 'tags' in data else None

        error = ''
        try:
            with transaction.atomic():
                team = Team(owner=request.user, name=name)
                team.save()
                profile = TeamProfile(team=team)
                if description:
                    profile.description = description
                if url:
                    profile.url = url
                if fields:
                    if len(fields) > 2:
                        raise ValueError('too many fields')
                    for i, name in enumerate(fields):
                        name = name.strip().lower()
                        if not name:
                            raise ValueError('blank tag is not allowed')
                        fields[i] = name
                    profile.field1 = fields.pop()
                    if len(fields) > 1:
                        profile.field2 = fields.pop()
                if location:
                    try:
                        TeamLocation.objects.set_location(team, location)
                    except TypeError:
                        error = 'invalid location'
                        raise IntegrityError
                    except ValueError as e:
                        error = str(e)
                        raise IntegrityError
                if tags:
                    try:
                        TeamTag.objects.set_tags(team, tags)
                    except TypeError:
                        error = 'invalid tag list'
                        raise IntegrityError
                    except ValueError as e:
                        error = str(e)
                        raise IntegrityError
                profile.save()
                return JsonResponse({'team_id': team.id})
        except IntegrityError:
            return Http400(error)


class Profile(View):
    @check_object_id(Team.enabled, 'team')
    @require_token
    def get(self, request, team):
        """
        获取团队的基本资料

        :param: team_id : 团队ID
        :return:
            id: 团队ID
            name: 团队名
            owner_id: 创始人id
            icon_url: 团队头像URL
            create_time: 注册时间
            is_recruiting：是否招募新成员
            description: 团队简介
            url: 团队链接
            location: 所在地区，格式：[province, city, county]
            fields: 所属领域，格式：['field1', 'field2']
            tags: 标签，格式：['tag1', 'tag2', ...]
        """
        owner = team.owner

        # 更新访客记录
        if owner != request.user:
            TeamVisitor.enabled.update_visitor(team, request.user)

        r = dict()
        r['id'] = team.id
        r['name'] = team.name
        r['owner_id'] = team.owner.id
        r['icon_url'] = team.icon_url
        r['create_time'] = team.create_time
        r['is_recruiting'] = team.is_recruiting
        r['description'] = team.profile.description
        r['url'] = team.profile.url
        r['fields'] = TeamProfile.get_fields(team)
        r['location'] = TeamLocation.objects.get_location(team)
        r['tags'] = TeamTag.objects.get_tags(team)

        return JsonResponse(r)

    post_dict = {
        'name': forms.CharField(required=False, min_length=1, max_length=20),
        'is_recruiting': forms.BooleanField(required=False),
        'description': forms.CharField(required=False, max_length=100),
        'url': forms.CharField(required=False, max_length=100),
    }

    @check_object_id(Team.enabled, 'team')
    @require_token
    @validate_json_input(post_dict)
    def post(self, request, team, data):
        """
        修改团队资料

        :param team: 团队ID
        :param data:
            name: 团队名
            description: 团队简介
            is_recruiting：是否招募新成员
            url: 团队链接
            location: 所在地区，格式：[province, city, county]
            fields: 所属领域，格式：['field1', 'field2']
            tags: 标签，格式：['tag1', 'tag2', ...]

        """
        if request.user != team.owner:
            return Http400('Editing is limited for current user')

        team_name = data.pop('name') if 'name' in data else ''
        location = data.pop('location') if 'location' in data else None
        fields = data.pop('fields') if 'fields' in data else None
        tags = data.pop('tags') if 'tags' in data else None
        profile = team.profile
        for k, v in data.items():
            setattr(profile, k, v)

        error = ''
        try:
            with transaction.atomic():
                if location:
                    try:
                        TeamLocation.objects.set_location(team, location)
                    except TypeError:
                        error = 'invalid location'
                        raise IntegrityError
                    except ValueError as e:
                        error = str(e)
                        raise IntegrityError
                if fields:
                    if len(fields) > 2:
                        return Http400('too many fields')
                    for i, name in enumerate(fields):
                        name = name.strip().lower()
                        if not name:
                            return Http400('blank tag is not allowed')
                        fields[i] = name
                    team.profile.field1 = fields[0]
                    if len(fields) > 1:
                        team.profile.field2 = fields[1]
                if tags:
                    try:
                        TeamTag.objects.set_tags(team, tags)
                    except TypeError:
                        error = 'invalid tag list'
                        raise IntegrityError
                    except ValueError as e:
                        error = str(e)
                        raise IntegrityError
                if team_name:
                    team.name = team_name
                    team.save()
                profile.save()
                return Http200()
        except IntegrityError:
            return Http400(error)


class Icon(View):
    @check_object_id(Team.enabled, 'team')
    @require_token
    def get(self, request, team):
        """
        获取团队头像URL

        :param team: 团队
        :return:
            icon_url: url | null
        """
        url = team.icon_url
        return JsonResponse({'icon_url': url})

    @check_object_id(Team.enabled, 'team')
    @require_token
    @process_uploaded_image('icon')
    def post(self, request, team, icon):
        """
        设置团队的头像

        :param team: 团队

        """
        if request.user != team.owner:
            return Http400('Editing is limited for current user')
        if team.icon:
            team.icon.delete()
        team.icon = icon
        team.save()
        return Http200()
