from django import forms
from datetime import datetime
from django.db import transaction, IntegrityError
from django.core.exceptions import ObjectDoesNotExist
from django.views.generic import View
from django.http import JsonResponse

from main.decorators import require_token, check_object_id, \
    validate_input, validate_json_input
from main.models.user_ import User
from main.models.team import Team
from main.models.team.member import TeamMember
from main.models.team.task import TeamTask, TeamTaskMarker
from main.models.action import ActionManager
from main.responses import *


class Tasks(View):
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
        获取团队发布的所有任务

        :param offset: 偏移量
        :param limit: 数量上限
        :param order: 排序方式
            0: 发布时间升序
            1: 发布时间降序（默认值）
            2: 名称升序
            3: 名称降序
        :return:
            count: 任务总数
            list: 任务列表
                id: 任务ID
                name: 任务名称
                team_id: 团队ID
                team_name: 团队名称
                executors: 执行者字典，格式{user_id:user_name,...}
                description: 任务描述
                status: 任务状态(未完成:0,已完成:1,已取消:2,全部标记完成:3)
                expected_time: 预计完成时间
                finish_time: 实际完成时间
                create_time: 发布时间
        """
        # 访问者不能查看团队任务列表
        if (request.user != team.owner) & TeamMember.exist(request.user, team):
            return Http403('recent user has no authority')
        i, j, k = offset, offset + limit, self.available_orders[order]
        c = TeamTask.enabled.count()
        tasks = TeamTask.enabled.order_by(k)[i:j]
        l = [{'id': t.id,
              'name': t.name,
              'team_id': t.team.id,
              'team_name': t.team.name,
              'executors': [{e.id: e.name} for e in t.executors.all()],
              'description': t.description,
              'status': t.status,
              'expected_time': t.expected_time,
              'finish_time': t.finish_time,
              'create_time': t.create_time} for t in tasks]
        return JsonResponse({'count': c, 'list': l})

    post_dict = {
        'name': forms.CharField(min_length=1, max_length=20),
        'description': forms.CharField(min_length=1, max_length=100),
        'expected_time': forms.DateTimeField(required=False),
    }

    @check_object_id(Team.enabled, 'team')
    @require_token
    @validate_json_input(post_dict)
    def post(self, request, team, data):
        """
        发布任务

        :param team_id: 团队ID
        :param data:
            name: 任务名称
            description: 任务描述
            expected_time: 预计完成时间
            executors_id: 执行者ID列表，格式：[user_id1, user_id2,...]
        :return: task_id: 任务ID
        """
        # 只有团队创始人才能发布任务
        if request.user != team.owner:
            return Http403('recent user has no authority')
        if 'executors_id' not in data:
            return Http400('require executors_id')
        executors_id = data['executors_id']
        name = data['name']
        description = data['description']
        if 'expected_time' in data:
            expected_time = data['expected_time']
            if expected_time < datetime.now():
                return Http400('expected time can not earlier than recent time')
        else:
            expected_time = None
        try:
            with transaction.atomic():
                task = TeamTask(
                    team=team, name=name, description=description)
                task.save()
                for user_id in executors_id:
                    try:
                        user = User.enabled.get(id=user_id)
                    except ObjectDoesNotExist:
                        return Http400('related executor not exists')
                    if user == team.owner:
                        return Http403('cannot send task to self')
                    if not TeamMember.exist(user, team):
                        return Http403('only can send task to team member')

                    task.executors.add(user)
                if expected_time:
                    task.expected_time = expected_time
                    task.save()
                # 创建发布任务的动态
                ActionManager.create_task(team, task)
                return JsonResponse({'task_id': task.id})
        except IntegrityError:
            return Http400('task create failed')


class TaskSelf(View):
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
        获取用户收到的所有任务

        :param offset: 偏移量
        :param limit: 数量上限
        :param order: 排序方式
            0: 发布时间升序
            1: 发布时间降序（默认值）
            2: 名称升序
            3: 名称降序
        :return:
            count: 任务总数
            list: 任务列表
                id: 任务ID
                name: 任务名称
                team_id: 团队ID
                team_name: 团队名称
                executors: 执行者字典，格式{user_id:user_name,...}
                description: 任务描述
                status: 任务状态(未完成:0,已完成:1,已取消:2,全部标记完成:3)
                expected_time: 预计完成时间
                finish_time: 实际完成时间
                create_time: 发布时间
        """
        i, j, k = offset, offset + limit, self.available_orders[order]
        c = TeamTask.enabled.filter(executors=request.user).count()
        tasks = TeamTask.enabled.filter(
                executors=request.user).order_by(k)[i:j]
        l = [{'id': t.id,
              'name': t.name,
              'team_id': t.team.id,
              'team_name': t.team.name,
              'executors': [{e.id: e.name} for e in t.executors.all()],
              'description': t.description,
              'status': t.status,
              'expected_time': t.expected_time,
              'finish_time': t.finish_time,
              'create_time': t.create_time} for t in tasks]
        return JsonResponse({'count': c, 'list': l})


class TaskMarker(TaskSelf):
    post_dict = {
        'description': forms.CharField(required=False, min_length=1,
                                       max_length=100)
    }

    @check_object_id(Team.enabled, 'team')
    @check_object_id(TeamTask.enabled, 'task')
    @require_token
    @validate_input(post_dict)
    def post(self, request, team, task, description=''):
        """
        用户标记任务为已完成
        :param team_id: 团队ID
        :param task_id: 任务ID
        :param description: 备注(默认为空)

        """
        if request.user not in task.executors.all():
            return Http403('user is not the executor of the task')
        if task.team != team:
            return Http400('related task of the team not exists')
        if TeamTaskMarker.exist(request.user, task):
            return Http400('related task marker already exists')
        if task.status != 0:
            if task.status == 1:
                return Http400('task already finished')
            if task.status == 2:
                return Http400('task already canceled')
            else:
                return Http400('task has already finished marking')
        task_marker = TeamTaskMarker(task=task, user=request.user,
                                     description=description)
        task_marker.save()
        for u in task.executors.all():
            if not TeamTaskMarker.exist(u, task):
                return Http200()
        # 若所有执行者都标记任务为已完成,则改变任务状态为全部标记完成
        task.status = 3
        task.save()
        return Http200()


class Task(View):
    @check_object_id(Team.enabled, 'team')
    @check_object_id(TeamTask.enabled, 'task')
    @require_token
    def post(self, request, team, task):
        """
        对用户标记过的任务进行确认

        :param team_id: 团队ID
        :param task_id: 任务ID
        """
        if request.user != team.owner:
            return Http403('recent user has no authority')
        if task.team != team:
            return Http400('related task of the team not exists')
        if task.status != 3:
            if task.status == 0:
                return Http400('task has not finish marking')
            if task.status == 1:
                return Http400('task already finished')
            else:
                return Http400('task already canceled')

        with transaction.atomic():
            task.status = 1
            task.save()
            # 发布任务已完成的动态
            ActionManager.finish_task(team, task)
        return Http200()

    @check_object_id(Team.enabled, 'team')
    @check_object_id(TeamTask.enabled, 'task')
    @require_token
    def delete(self, request, team, task):
        """
        取消任务

        :param team_id: 团队ID
        :param task_id: 任务ID
        """
        if request.user != team.owner:
            return Http403('recent user has no authority')
        if task.team != team:
            return Http400('related task of the team not exists')
        if task.status == 1:
            return Http400('task already finished')
        if task.status == 2:
            return Http400('task already canceled')

        task.status = 2
        task.save()
        return Http200()
