from django import forms
from django.db import IntegrityError, transaction
from django.http import JsonResponse
from django.views.generic import View
from main.models.action import ActionManager
from main.models.location import TeamNeedLocation
from main.models.team.need import TeamNeed, TeamMemberNeed, \
    TeamOutsourceNeed, TeamUndertakeNeed
from main.responses import *

from main.models.team import Team
from main.utils.decorators import require_token, fetch_object, \
    validate_json_input


class Needs(View):
    get_dict = {
        'offset': forms.IntegerField(required=False, min_value=0),
        'limit': forms.IntegerField(required=False, min_value=0),
        'order': forms.IntegerField(required=False, min_value=0, max_value=1),
        'type': forms.IntegerField(required=False, min_value=1, max_value=3),
    }
    available_orders = ('create_time', '-create_time')

    @require_token
    @validate_json_input(get_dict)
    def get(self, request, offset=0, limit=10, order=1, type=0):
        """
        获取发布中的需求列表

        :param offset: 偏移量
        :param limit: 数量上限
        :param order: 排序方式
            0: 发布时间升序
            1: 发布时间降序（默认值）
        :param type: 需求类型
            0: 全部(默认值)
            1: 人员需求
            2: 外包需求
            3: 承接需求
        :return:
            count: 需求总数
            list: 需求列表
                need_id: 需求ID
                team_id: 团队ID
                team_name: 团队名称
                icon_url: 团队头像
                status: 需求状态
                title: 需求标题
                create_time: 发布时间
        """
        i, j, k = offset, offset + limit, self.available_orders[order]
        if type == 0:
            c = TeamMemberNeed.enabled.count()
            needs = TeamMemberNeed.enabled.order_by(k)[i:j]
        else:
            c = TeamNeed.enabled.filter(type=type).count()
            needs = TeamNeed.enabled.filter(type=type).order_by(k)[i:j]
        l = [{'need_id': n.id,
              'team_id': n.team.id,
              'team_name': n.team.name,
              'icon_url': n.team.icon_url,
              'status': n.status,
              'title': n.title,
              'create_time': n.create_time} for n in needs]
        return JsonResponse({'count': c, 'list': l})


class NeedSelf(View):
    get_dict = {
        'offset': forms.IntegerField(required=False, min_value=0),
        'limit': forms.IntegerField(required=False, min_value=0),
        'order': forms.IntegerField(required=False, min_value=0, max_value=1),
        'type': forms.IntegerField(required=False, min_value=1, max_vale=3),
    }
    available_orders = ('create_time', '-create_time')

    @fetch_object(Team.enabled, 'team')
    @require_token
    @validate_json_input(get_dict)
    def get(self, request, team, offset=0, limit=10, order=1, type=0):
        """
        获取团队的需求列表

        :param team_id: 团队ID
        :param offset: 偏移量
        :param limit: 数量上限
        :param order: 排序方式
            0: 发布时间升序
            1: 发布时间降序（默认值）
        :param type: 需求类型
            0: 全部(默认值)
            1: 人员需求
            2: 外包需求
            3: 承接需求
        :return:
            count: 需求总数
            list: 需求列表
                need_id: 需求ID
                team_id: 团队ID
                team_name: 团队名称
                icon_url: 团队头像
                status: 需求状态
                title: 需求标题
                create_time: 发布时间
        """
        i, j, k = offset, offset + limit, self.available_orders[order]
        if type == 0:
            c = TeamMemberNeed.enabled.filter(team=team).count()
            needs = TeamMemberNeed.enabled.filter(team=team).order_by(k)[i:j]
        else:
            c = TeamNeed.enabled.filter(team=team, type=type).count()
            needs = TeamNeed.enabled.filter(team=team, type=type).order_by(k)[i:j]
        l = [{'need_id': n.id,
              'team_id': n.team.id,
              'team_name': n.team.name,
              'icon_url': n.team.icon_url,
              'status': n.status,
              'title': n.title,
              'create_time': n.create_time} for n in needs]
        return JsonResponse({'count': c, 'list': l})

    @fetch_object(Team.enabled, 'team')
    @fetch_object(TeamNeed.enabled, 'need')
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

    @fetch_object(Team.enabled, 'team')
    @fetch_object(TeamNeed.enabled, 'need')
    @require_token
    def delete(self, request, team, need):
        """
        需求状态设置为已删除

        :param team_id: 团队ID
        :param need_id: 需求ID
        """
        if request.user != team.owner:
            return Http403('recent user has no authority')
        if need.team != team:
            return Http400('related team need not exists')
        try:
            need.status = 1
            need.save()
            return Http200()
        except IntegrityError:
            return Http400()


class NeedDetail(View):
    @fetch_object(Team.enabled, 'team')
    @fetch_object(TeamNeed.enabled, 'need')
    @require_token
    def get(self, request, team, need):
        """
        获取人员需求详情

        :param team_id: 团队ID
        :param need_id: 需求ID
        :return:
            if type==1(人员需求)：
                need_id: 需求id
                team_id: 团队ID
                team_name: 团队名称
                icon_url: 团队头像
                number: 所需人数
                age_min: 最小年龄
                age_max: 最大年龄
                gender: 性别要求(0为不限)
                location: 地区要求，格式：[province, city, county]
                field: 领域
                skill: 技能
                degree: 学历(('其他', 0), ('初中', 1), ('高中', 2),
                        ('大专', 3), ('本科', 4), ('硕士', 5), ('博士', 6))
                major: 专业
                graduate_time: 毕业时间
                work_experience: 工作经历
                practice_experience: 实习经历
                project_experience: 项目经历
                deadline: 截止时间
            if type==2(外包需求):
                need_id: 需求id
                team_id: 团队ID
                team_name: 团队名称
                icon_url: 团队头像
                number: 所需人数
                age_min: 最小年龄
                age_max: 最大年龄
                gender: 性别要求
                location: 地区要求, 格式：[province, city, county]
                field: 领域
                skill: 技能
                degree: 学历(('其他', 0), ('初中', 1), ('高中', 2),
                        ('大专', 3), ('本科', 4), ('硕士', 5), ('博士', 6))
                major: 专业
                expend: 费用(-1为面谈)
                expend_unit: 费用单位(('项', 0), ('天', 1), ('人', 2))
                start_time: 外包任务开始时间
                end_time: 外包任务结束时间
                description: 需求描述
                deadline: 截止时间
            if type==3(承接需求):
                need_id: 需求id
                team_id: 团队ID
                team_name: 团队名称
                icon_url: 团队头像
                number: 团队人数
                location: 地区要求，格式：[province, city, county]
                field: 领域
                skill: 技能
                degree: 学历(('其他', 0), ('初中', 1), ('高中', 2),
                        ('大专', 3), ('本科', 4), ('硕士', 5), ('博士', 6))
                major: 专业
                expend: 费用(-1为面谈)
                expend_unit: 费用单位(('项', 0), ('天', 1), ('人', 2))
                start_time: 承接开始时间
                end_time: 承接结束时间
                description: 需求描述
                deadline: 截止时间
        """
        r = dict()
        t = need.type
        if t == 1:
            r['need_id'] = need.id
            r['team_id'] = need.team.id
            r['team_name'] = need.team.name
            r['icon_url'] = need.team.icon_url
            r['number'] = need.number
            r['age_min'] = need.age_min
            r['age_max'] = need.age_max
            r['gender'] = need.gender
            r['location'] = TeamNeedLocation.objects.get_location(need)
            r['field'] = need.field
            r['skill'] = need.skill
            r['degree'] = need.degree
            r['major'] = need.major
            r['graduate_time'] = need.graduate_time
            r['work_experience'] = need.work_experience
            r['practice_experience'] = need.practice_experience
            r['project_experience'] = need.project_experience
            r['deadline'] = need.deadline
        elif t == 2:
            r['need_id'] = need.id
            r['team_id'] = need.team.id
            r['team_name'] = need.team.name
            r['icon_url'] = need.team.icon_url
            r['number'] = need.number
            r['age_min'] = need.age_min
            r['age_max'] = need.age_max
            r['gender'] = need.gender
            r['location'] = TeamNeedLocation.objects.get_location(need)
            r['field'] = need.field
            r['skill'] = need.skill
            r['degree'] = need.degree
            r['major'] = need.major
            r['expend'] = need.expend
            r['expend_unit'] = need.expend_unit
            r['start_time'] = need.start_time
            r['end_time'] = need.end_time
            r['description'] = need.description
            r['deadline'] = need.deadline
        else:
            r['need_id'] = need.id
            r['team_id'] = need.team.id
            r['team_name'] = need.team.name
            r['icon_url'] = need.team.icon_url
            r['number'] = need.number
            r['location'] = TeamNeedLocation.objects.get_location(need)
            r['field'] = need.field
            r['skill'] = need.skill
            r['degree'] = need.degree
            r['major'] = need.major
            r['expend'] = need.expend
            r['expend_unit'] = need.expend_unit
            r['start_time'] = need.start_time
            r['end_time'] = need.end_time
            r['description'] = need.description
            r['deadline'] = need.deadline
        return JsonResponse(r)


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

    @fetch_object(Team.enabled, 'team')
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
                    need.time_graduated = graduate_time
                if age_min and age_max:
                    if age_min > age_max:
                        error = 'invalid age'
                        raise IntegrityError
                    else:
                        need.min_age = age_min
                        need.max_age = age_max
                elif age_min:
                    need.min_age = age_min
                elif age_max:
                    need.max_age = age_max
                if gender:
                    need.gender = gender
                if work_experience:
                    need.work_experience = work_experience
                if practice_experience:
                    need.fieldwork_experience = practice_experience
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

    @fetch_object(Team.enabled, 'team')
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

    @fetch_object(Team.enabled, 'team')
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
