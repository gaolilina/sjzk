from django import forms
from django.db import IntegrityError, transaction
from django.views.generic import View
from django.http import JsonResponse

from main.decorators import require_token, check_object_id, \
    validate_input, validate_json_input
from main.models.team.need import TeamMemberNeed, \
    TeamOutsourceNeed, TeamUndertakeNeed
from main.models.location import TeamNeedLocation
from main.models.action import ActionManager
from main.models.team import Team
from main.responses import *


'''
class Needs(View):
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
        获取所有团队发布的需求

        :param offset: 偏移量
        :param limit: 数量上限
        :param order: 排序方式
            0: 发布时间升序
            1: 发布时间降序（默认值）
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
                location: 地区要求，格式：[province, city, county]
                create_time: 发布时间
                deadline: 截止时间
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
              'create_time': n.create_time,
              'deadline': n.deadline} for n in needs]
        return JsonResponse({'count': c, 'list': l})


class Need(View):
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
        获取团队发布的需求

        :param team_id: 团队ID
        :param offset: 偏移量
        :param limit: 数量上限
        :param order: 排序方式
            0: 发布时间升序
            1: 发布时间降序（默认值）

        :return:
            count: 需求总数
            list: 需求列表
                id: 需求ID
                description: 需求描述
                status: 需求状态(未满足:0,已满足:1)
                number: 需求人数(若干:-1)
                gender: 性别要求(不限:0,男:1,女:2)
                location: 地区要求，格式：[province, city, county]
                create_time: 发布时间
                deadline: 截止时间
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
              'create_time': n.create_time,
              'deadline': n.deadline} for n in needs]
        return JsonResponse({'count': c, 'list': l})

    post_dict = {
        'description': forms.CharField(min_length=1, max_length=100),
        'number': forms.IntegerField(required=False, min_value=1),
        'gender': forms.IntegerField(required=False),
        'province': forms.CharField(required=False),
        'city': forms.CharField(required=False),
        'deadline': forms.DateTimeField(required=False),
    }

    @check_object_id(Team.enabled, 'team')
    @require_token
    @validate_json_input(post_dict)
    def post(self, request, team, data):
        """
        发布需求

        :param team_id: 团队ID
        :param data:
            description: 需求描述
            number: 所需人数(默认为-1,若干)
            gender: 性别要求(默认为0,不限)
            location: 地区要求(默认为空,不限)，格式：[province, city, county]
            deadline: 截止时间(默认为空)
        :return: need_id: 需求id
        """
        if request.user != team.owner:
            return Http403('recent user has no authority')

        description = data.pop('description') if 'description' in data else ''
        number = data.pop('number') if 'number' in data else -1
        gender = data.pop('gender') if 'gender' in data else 0

        deadline = data.pop('deadline') if 'deadline' in data else None
        location = data.pop('location') if 'location' in data else None

        error = ''
        try:
            with transaction.atomic():
                need = TeamNeed(team=team, description=description,
                                number=number, gender=gender, deadline=deadline)
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
                # 创建发布需求的动态
                ActionManager.create_need(team, need)
                return JsonResponse({'need_id': need.id})
        except IntegrityError:
            return Http400(error)


class NeedSelf(View):
    @check_object_id(Team.enabled, 'team')
    @check_object_id(TeamNeed.enabled, 'need')
    @require_token
    def post(self, request, team, need):
        """
        需求状态设置为已满足

        :param team_id: 团队ID
        :param need_id: 需求ID
        """
        if request.user != team.owner:
            return Http403('recent user has no authority')
        if need.team != team:
            return Http400('related team need not exists')
        try:
            with transaction.atomic():
                need.status = 1
                need.save()
                # 发布需求满足动态
                ActionManager.meet_need(team, need)
                return Http200()
        except IntegrityError:
            return Http400()

    @check_object_id(Team.enabled, 'team')
    @check_object_id(TeamNeed.enabled, 'need')
    @require_token
    def delete(self, request, team, need):
        """
        删除需求

        :param team_id: 团队ID
        :param need_id: 需求ID
        """
        if request.user != team.owner:
            return Http403('recent user has no authority')
        if need.team != team:
            return Http400('related team need not exists')
        try:
            need.delete()
            return Http200()
        except IntegrityError:
            return Http400()
'''


class MemberNeed(View):
    post_dict = {
        'number': forms.IntegerField(min_value=1),
        'field': forms.CharField(max_length=10),
        'skill': forms.CharField(max_length=10),
        'age_min': forms.IntegerField(
            required=False, min_value=0, max_value=99),
        'age_max': forms.IntegerField(
            required=False, min_value=1, max_value=100),
        'deadline': forms.DateTimeField(),
    }

    @check_object_id(Team.enabled, 'team')
    @require_token
    @validate_json_input(post_dict)
    def post(self, request, team, data):
        """
        发布人员需求

        :param team_id: 团队ID
        :param data:
            number: 所需人数(必填)
            age_min: 最小年龄
            age_max: 最大年龄
            gender: 性别要求(默认为0,不限)
            location: 地区要求(默认为空,不限)，格式：[province, city, county]
            field: 领域(必填)
            skill: 技能(必填)
            degree: 学历(默认为0, ('其他', 0), ('初中', 1), ('高中', 2),
                    ('大专', 3), ('本科', 4), ('硕士', 5), ('博士', 6))
            major: 专业
            graduate_time: 毕业时间
            work_experience: 工作经历
            practice_experience: 实习经历
            project_experience: 项目经历
            deadline: 截止时间(必填)
        :return: need_id: 需求id
        """
        if request.user != team.owner:
            return Http403('recent user has no authority')

        number = data.pop('number')
        age_min = data.pop('age_min') if 'age_min' in data else ''
        age_max = data.pop('age_max') if 'age_max' in data else ''
        gender = data.pop('gender') if 'gender' in data else 0
        location = data.pop('location') if 'location' in data else None
        field = data.pop('field')
        skill = data.pop('skill')
        degree = data.pop('degree') if 'degree' in data else ''
        major = data.pop('major') if 'major' in data else ''
        graduate_time = data.pop('graduate_time') \
            if 'graduate_time' in data else ''
        work_experience = data.pop('work_experience') \
            if 'work_experience' in data else ''
        practice_experience = data.pop('practice_experience') \
            if 'practice_experience' in data else ''
        project_experience = data.pop('project_experience') \
            if 'project_experience' in data else ''
        deadline = data.pop('deadline')

        error = ''
        try:
            with transaction.atomic():
                need = TeamMemberNeed(team=team, number=number, field=field,
                                      skill=skill, deadline=deadline)
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
                if degree:
                    need.degree = degree
                if major:
                    need.major = major
                if graduate_time:
                    need.graduate_time = graduate_time
                if age_min and age_max:
                    if age_min > age_max:
                        error = 'invalid age'
                        raise IntegrityError
                    else:
                        need.age_min = age_min
                        need.age_max = age_max
                elif age_min:
                    need.age_min = age_min
                elif age_max:
                    need.age_max = age_max
                if gender:
                    need.gender = gender
                if work_experience:
                    need.work_experience = work_experience
                if practice_experience:
                    need.practice_experience = practice_experience
                if project_experience:
                    need.project_experience = practice_experience
                need.save()
                # 创建发布需求的动态
                ActionManager.create_need(team, need)
                return JsonResponse({'need_id': need.id})
        except IntegrityError:
            return Http400(error)


class OutsourceNeed(View):
    post_dict = {
        'number': forms.IntegerField(min_value=1),
        'field': forms.CharField(max_length=10),
        'skill': forms.CharField(max_length=10),
        'age_min': forms.IntegerField(
            required=False, min_value=0, max_value=99),
        'age_max': forms.IntegerField(
            required=False, min_value=1, max_value=100),
        'expend': forms.IntegerField(
            required=False, min_value=-1),
        'expend_unit': forms.IntegerField(
            required=False, min_value=0, max_value=2),
        'start_time': forms.DateTimeField(),
        'end_time': forms.DateTimeField(),
        'description': forms.CharField(required=False, max_length=100),
        'deadline': forms.DateTimeField(),
    }

    @check_object_id(Team.enabled, 'team')
    @require_token
    @validate_json_input(post_dict)
    def post(self, request, team, data):
        """
        发布外包需求

        :param team_id: 团队ID
        :param data:
            number: 所需人数(必填)
            age_min: 最小年龄
            age_max: 最大年龄
            gender: 性别要求(默认为0,不限)
            location: 地区要求(默认为空,不限)，格式：[province, city, county]
            field: 领域(必填)
            skill: 技能(必填)
            degree: 学历(默认为0, ('其他', 0), ('初中', 1), ('高中', 2),
                    ('大专', 3), ('本科', 4), ('硕士', 5), ('博士', 6))
            major: 专业
            expend: 费用(默认为-1, 面谈)
            expend_unit: 费用单位(默认为0, ('项', 0), ('天', 1), ('人', 2))
            start_time: 外包任务开始时间(必填)
            end_time: 外包任务结束时间(必填)
            description: 需求描述
            deadline: 截止时间(必填)
        :return: need_id: 需求id
        """
        if request.user != team.owner:
            return Http403('recent user has no authority')

        number = data.pop('number')
        age_min = data.pop('age_min') if 'age_min' in data else ''
        age_max = data.pop('age_max') if 'age_max' in data else ''
        gender = data.pop('gender') if 'gender' in data else 0
        location = data.pop('location') if 'location' in data else None
        field = data.pop('field')
        skill = data.pop('skill')
        degree = data.pop('degree') if 'degree' in data else ''
        major = data.pop('major') if 'major' in data else ''
        expend = data.pop('expend') if 'expend' in data else -1
        expend_unit = data.pop('expend_unit') if 'expend_unit' in data else 0
        start_time = data.pop('start_time')
        end_time = data.pop('end_time')
        description = data.pop('description') if 'description' in data else ''
        deadline = data.pop('deadline')

        if start_time > end_time:
            return Http400('invalid time stage')
        error = ''
        try:
            with transaction.atomic():
                need = TeamOutsourceNeed(
                    team=team, number=number, field=field, skill=skill,
                    expend=expend, expend_unit=expend_unit,
                    start_time=start_time, end_time=end_time, deadline=deadline)
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
                if degree:
                    need.degree = degree
                if major:
                    need.major = major
                if age_min and age_max:
                    if age_min > age_max:
                        error = 'invalid age'
                        raise IntegrityError
                    else:
                        need.age_min = age_min
                        need.age_max = age_max
                elif age_min:
                    need.age_min = age_min
                elif age_max:
                    need.age_max = age_max
                if gender:
                    need.gender = gender
                if description:
                    need.description = description
                need.save()

                # 创建发布需求的动态
                ActionManager.create_need(team, need)
                return JsonResponse({'need_id': need.id})
        except IntegrityError:
            return Http400(error)


class UndertakeNeed(View):
    post_dict = {
        'field': forms.CharField(max_length=10),
        'skill': forms.CharField(max_length=10),
        'expend': forms.IntegerField(
            required=False, min_value=-1),
        'expend_unit': forms.IntegerField(
            required=False, min_value=0, max_value=2),
        'start_time': forms.DateTimeField(),
        'end_time': forms.DateTimeField(),
        'description': forms.CharField(required=False, max_length=100),
        'deadline': forms.DateTimeField(),
    }

    @check_object_id(Team.enabled, 'team')
    @require_token
    @validate_json_input(post_dict)
    def post(self, request, team, data):
        """
        发布承接需求

        :param team_id: 团队ID
        :param data:
            location: 地区要求(默认为空,不限)，格式：[province, city, county]
            field: 领域(必填)
            skill: 技能(必填)
            degree: 学历(默认为0, ('其他', 0), ('初中', 1), ('高中', 2),
                    ('大专', 3), ('本科', 4), ('硕士', 5), ('博士', 6))
            major: 专业
            expend: 费用(默认为-1, 面谈)
            expend_unit: 费用单位(默认为0, ('项', 0), ('天', 1), ('人', 2))
            start_time: 承接开始时间(必填)
            end_time: 承接结束时间(必填)
            description: 需求描述
            deadline: 截止时间(必填)
        :return: need_id: 需求id
        """
        if request.user != team.owner:
            return Http403('recent user has no authority')

        location = data.pop('location') if 'location' in data else None
        field = data.pop('field')
        skill = data.pop('skill')
        expend = data.pop('expend') if 'expend' in data else -1
        expend_unit = data.pop('expend_unit') if 'expend_unit' in data else 0
        start_time = data.pop('start_time')
        end_time = data.pop('end_time')
        description = data.pop('description') if 'description' in data else ''
        deadline = data.pop('deadline')

        if start_time > end_time:
            return Http400('invalid time stage')
        number = team.member_records.count()
        error = ''
        try:
            with transaction.atomic():
                need = TeamUndertakeNeed(
                    team=team, number=number, field=field, skill=skill,
                    expend=expend, expend_unit=expend_unit,
                    start_time=start_time, end_time=end_time, deadline=deadline)
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
                if description:
                    need.description = description
                need.save()

                # 创建发布需求的动态
                ActionManager.create_need(team, need)
                return JsonResponse({'need_id': need.id})
        except IntegrityError:
            return Http400(error)