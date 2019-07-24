#! /usr/bin/env python3
# -*- coding: utf-8 -*-
from django import forms
from django.core.exceptions import ObjectDoesNotExist
from django.http import JsonResponse
from django.utils import timezone
from django.views.generic import View

from main.models import Team, User
from main.models.task import InternalTask, ExternalTask
from main.utils import abort, get_score_stage, action
from main.utils.decorators import require_token, require_verification_token
from main.utils.dfa import check_bad_words
from util.decorator.param import fetch_object, validate_args


class InternalTaskList(View):
    @fetch_object(Team.enabled, 'team')
    @require_token
    @validate_args({
        'offset': forms.IntegerField(required=False, min_value=0),
        'limit': forms.IntegerField(required=False, min_value=0),
        'sign': forms.IntegerField(required=False, min_value=0, max_value=2),
    })
    def get(self, request, team, sign=None, offset=0, limit=10):
        """获取团队的内部任务列表
        :param offset: 偏移量
        :param sign: 任务状态 - 0: pending, 1: completed, 2: terminated
        :return:
            count: 任务总数
            list: 任务列表
                id: 任务ID
                status: 任务状态 - ('等待接受', 0), ('再派任务', 1),
                                  ('等待完成', 2), ('等待验收', 3),
                                  ('再次提交', 4), ('按时结束', 5),
                                  ('超时结束', 6), ('终止', 7)
                title: 任务标题
                executor_id: 执行者ID
                executor_name: 执行者昵称
                icon_url: 执行者头像
                time_created: 发布时间
        """
        qs = team.internal_tasks
        if sign is not None:
            if sign == 0:
                qs = qs.filter(status__range=[0, 4])
            elif sign == 1:
                qs = qs.filter(status__in=[5, 6])
            else:
                qs = qs.filter(status=7)
            tasks = qs[offset:offset + limit]
        else:
            tasks = qs.all()[offset:offset + limit]
        c = qs.count()
        l = [{'id': t.id,
              'status': t.status,
              'title': t.title,
              'executor_id': t.executor.id,
              'executor_name': t.executor.name,
              'icon_url': t.executor.icon,
              'time_created': t.time_created} for t in tasks]
        return JsonResponse({'count': c, 'list': l})

    @fetch_object(Team.enabled, 'team')
    @require_verification_token
    @validate_args({
        'executor_id': forms.IntegerField(),
        'title': forms.CharField(max_length=20),
        'content': forms.CharField(max_length=200),
        'deadline': forms.DateField(),
    })
    def post(self, request, team, **kwargs):
        """发布内部任务

        :param: executor_id: 执行者ID
        :param: title: 标题
        :param: content: 内容
        :param；deadline: 截止时间
        """
        if check_bad_words(kwargs["title"]) or check_bad_words(kwargs["content"]):
            abort(403, '含有非法词汇')
        if request.user != team.owner:
            abort(403, '只有队长可以操作')
        executor_id = kwargs.pop('executor_id')
        executor = None
        try:
            executor = User.enabled.get(id=executor_id)
        except ObjectDoesNotExist:
            abort(401, '执行者不存在')

        if not team.members.filter(user=executor).exists():
            abort(404, '执行者非团队成员')
        t = team.internal_tasks.create(status=0, executor=executor,
                                       deadline=kwargs['deadline'])
        for k in kwargs:
            setattr(t, k, kwargs[k])
        t.save()
        request.user.score += get_score_stage(1)
        request.user.score_records.create(
            score=get_score_stage(1), type="能力",
            description="发布一个内部任务")
        team.score += get_score_stage(1)
        team.score_records.create(
            score=get_score_stage(1), type="活跃度",
            description="发布一个内部任务")
        request.user.save()
        team.save()
        abort(200)


class InternalTasks(View):
    @require_token
    @validate_args({
        'offset': forms.IntegerField(required=False, min_value=0),
        'limit': forms.IntegerField(required=False, min_value=0),
        'sign': forms.IntegerField(required=False, min_value=0, max_value=2),
    })
    def get(self, request, sign=None, offset=0, limit=10):
        """获取用户的内部任务列表
        :param offset: 偏移量
        :param sign: 任务状态 - 0: pending, 1: completed, 2: terminated
        :return:
            count: 任务总数
            list: 任务列表
                id: 任务ID
                team_id: 团队ID
                team_name: 团队名称
                icon_url: 团队头像
                status: 任务状态 - ('等待接受', 0), ('再派任务', 1),
                                  ('等待完成', 2), ('等待验收', 3),
                                  ('再次提交', 4), ('按时结束', 5),
                                  ('超时结束', 6), ('终止', 7)
                title: 任务标题
                time_created: 发布时间
        """
        qs = request.user.internal_tasks
        if sign is not None:
            if sign == 0:
                qs = qs.filter(status__range=[0, 4])
            elif sign == 1:
                qs = qs.filter(status__in=[5, 6])
            else:
                qs = qs.filter(status=7)
            tasks = qs[offset:offset + limit]
        else:
            tasks = qs.all()[offset:offset + limit]

        c = qs.count()
        l = [{'id': t.id,
              'team_id': t.team.id,
              'team_name': t.team.name,
              'icon_url': t.team.icon,
              'status': t.status,
              'title': t.title,
              'time_created': t.time_created} for t in tasks]
        return JsonResponse({'count': c, 'list': l})

    @fetch_object(InternalTask.objects, 'task')
    @require_verification_token
    @validate_args({
        'title': forms.CharField(required=False, max_length=20),
        'content': forms.CharField(required=False, max_length=200),
        'deadline': forms.DateField(required=False),
    })
    def post(self, request, task, **kwargs):
        """再派任务状态下的任务修改
        :param task_id: 任务ID
        :param title: 任务标题
        :param content: 任务内容
        :param deadline: 任务期限

        """
        if check_bad_words(kwargs["title"]) or check_bad_words(kwargs["content"]):
            abort(403, '含有非法词汇')
        if request.user != task.team.owner:
            abort(403, '不能给自己发送任务')
        if task.status != 1:
            abort(404, '任务状态错误')

        for k in kwargs:
            setattr(task, k, kwargs[k])
        task.save()
        abort(200)


class TeamInternalTask(View):
    keys = ('id', 'title', 'content', 'status', 'deadline', 'assign_num',
            'submit_num', 'finish_time', 'time_created')

    @fetch_object(InternalTask.objects, 'task')
    @require_token
    def get(self, request, task):
        """获取内部任务详情

        :return:
            id: 任务id
            executor_id: 执行者ID
            executor_name: 执行者名称
            team_id: 团队ID
            team_name: 团队名称
            icon_url: 团队头像
            title: 任务标题
            content: 任务内容
            status: 任务状态 - ('等待接受', 0), ('再派任务', 1),
                              ('等待完成', 2), ('等待验收', 3),
                              ('再次提交', 4), ('按时结束', 5),
                              ('超时结束', 6), ('终止', 7)
            deadline: 任务期限
            assign_num: 任务分派次数
            submit_num: 任务提交次数
            finish_time: 任务完成时间
            time_created: 任务创建时间
        """

        d = {'executor_id': task.executor.id,
             'executor_name': task.executor.name,
             'team_id': task.team.id,
             'team_name': task.team.name,
             'icon_url': task.team.icon}

        # noinspection PyUnboundLocalVariable
        for k in self.keys:
            d[k] = getattr(task, k)

        return JsonResponse(d)

    @fetch_object(InternalTask.objects, 'task')
    @require_verification_token
    @validate_args({
        'status': forms.IntegerField(required=False, min_value=0, max_value=7),
    })
    def post(self, request, task, status=None):
        """
        修改内部任务的状态(默认为None, 后台确认任务是按时还是超时完成)
        :param status:
        要修改的任务状态 - ('等待接受', 0), ('再派任务', 1),
                          ('等待完成', 2), ('等待验收', 3),
                          ('再次提交', 4), ('按时结束', 5),
                          ('超时结束', 6), ('终止', 7)
        """
        if request.user != task.team.owner and request.user != task.executor:
            abort(403, '非法操作')

        # 任务已经终止，不允许操作
        if task.status == 7:
            abort(404, '任务已结束')

        if status is None:
            if request.user != task.team.owner or task.status != 3:
                abort(403, '非法操作')
            task.finish_time = timezone.now()
            if task.finish_time.date() > task.deadline:
                task.status = 6
            else:
                task.status = 5
            # 积分
            task.executor.score += get_score_stage(1)
            task.executor.score_records.create(
                score=get_score_stage(1), type="能力",
                description="完成一个内部任务")
            task.team.score += get_score_stage(1)
            task.team.score_records.create(
                score=get_score_stage(1), type="能力",
                description="队友完成一个内部任务")
            task.executor.save()
            task.team.save()
            task.save()
            abort(200)
        elif status == 0:
            if request.user != task.team.owner or task.status != 1:
                abort(403, '非法操作')
            else:
                # 如果任务状态为再派任务-->等待接受，则分派次数+1
                task.assign_num += 1
        elif status == 1:
            if request.user != task.executor or task.status != 0:
                abort(403, '非法操作')
        elif status == 2:
            if request.user != task.executor or task.status != 0:
                abort(403, '非法操作')
        elif status == 3:
            if request.user != task.executor or (task.status not in [2, 4]):
                abort(403, '非法操作')
            elif task.status == 4:
                # 如果任务状态为再次提交-->等待验收，则提交次数+1
                task.submit_num += 1
        elif status == 4:
            if request.user != task.team.owner or task.status != 3:
                abort(403, '非法操作')
        elif status == 7:
            if request.user != task.team.owner or task.status != 1:
                abort(403, '非法操作')
        else:
            abort(403, '状态参数错误')

        task.status = status
        task.save()
        abort(200)


class ExternalTaskList(View):
    @fetch_object(Team.enabled, 'team')
    @require_token
    @validate_args({
        'offset': forms.IntegerField(required=False, min_value=0),
        'limit': forms.IntegerField(required=False, min_value=0),
        'sign': forms.IntegerField(required=False, min_value=0, max_value=1),
        'type': forms.IntegerField(required=False, min_value=0, max_value=1),
    })
    def get(self, request, team, sign=None, type=0, offset=0, limit=10):
        """获取团队的外包/承接任务列表
        :param offset: 偏移量
        :param type: 任务类型 - 0: outsource, 1: undertake
        :param sign: 任务状态 - 0: pending, 1: completed
        :return:
            count: 任务总数
            list: 任务列表
                if type==0（团队的外包任务）
                    id: 任务ID
                    status: 任务状态 - ('等待接受', 0), ('再派任务', 1),
                                      ('等待完成', 2), ('等待验收', 3),
                                      ('再次提交', 4), ('等待支付', 6),
                                      ('再次支付', 7), ('等待确认', 8),
                                      ('按时结束', 9),('超时结束', 10)
                    title: 任务标题
                    executor_id: 执行团队ID
                    executor_name: 执行团队昵称
                    icon_url: 执行团队头像
                    time_created: 发布时间
                if type==1（团队的承接任务）
                    id: 任务ID
                    status: 任务状态 - ('等待接受', 0), ('再派任务', 1),
                                      ('等待完成', 2), ('等待验收', 3),
                                      ('再次提交', 4), ('等待支付', 6),
                                      ('再次支付', 7), ('等待确认', 8),
                                      ('按时结束', 9),('超时结束', 10)
                    title: 任务标题
                    team_id: 外包团队ID
                    team_name: 外包团队昵称
                    icon_url: 外包团队头像
                    time_created: 发布时间
        """
        if type == 0:
            qs = team.outsource_external_tasks
            if sign is not None:
                if sign == 0:
                    qs = qs.filter(status__range=[0, 8])
                else:
                    qs = qs.filter(status__in=[9, 10])
                tasks = qs[offset:offset + limit]
            else:
                tasks = qs.all()[offset:offset + limit]
            c = qs.count()
            l = [{'id': t.id,
                  'status': t.status,
                  'title': t.title,
                  'executor_id': t.executor.id,
                  'executor_name': t.executor.name,
                  'icon_url': t.executor.icon,
                  'time_created': t.time_created} for t in tasks]
            return JsonResponse({'count': c, 'list': l})
        else:
            qs = team.undertake_external_tasks
            if sign is not None:
                if sign == 0:
                    qs = qs.filter(status__range=[0, 8])
                else:
                    qs = qs.filter(status__in=[9, 10])

            c = qs.count()
            tasks = qs[offset:offset + limit]
            l = [{'id': t.id,
                  'status': t.status,
                  'title': t.title,
                  'team_id': t.team.id,
                  'team_name': t.team.name,
                  'icon_url': t.team.icon,
                  'time_created': t.time_created} for t in tasks]
            return JsonResponse({'count': c, 'list': l})

    @fetch_object(Team.enabled, 'team')
    @require_verification_token
    @validate_args({
        'executor_id': forms.IntegerField(),
        'title': forms.CharField(max_length=20),
        'content': forms.CharField(max_length=200),
        'expend': forms.IntegerField(required=False, min_value=1),
        'deadline': forms.DateField(),
    })
    def post(self, request, team, **kwargs):
        """发布外包任务

        :param: executor_id: 执行者ID
        :param: title: 标题
        :param: content: 内容
        :param: expend: 预计费用
        :param；deadline: 截止时间
        """
        if check_bad_words(kwargs["title"]) or check_bad_words(kwargs["content"]):
            abort(403, '含有非法词汇')
        if request.user != team.owner:
            abort(403, '只有队长可以操作')
        executor_id = kwargs.pop('executor_id')
        executor = None
        try:
            executor = Team.enabled.get(id=executor_id)
        except ObjectDoesNotExist:
            abort(403, '执行者不存在')

        if not team.members.filter(user=executor.owner).exists():
            abort(404, '执行者非团队成员')
        t = team.outsource_external_tasks.create(
            status=0, executor=executor, deadline=kwargs['deadline'])
        for k in kwargs:
            setattr(t, k, kwargs[k])
        t.save()
        request.user.score += get_score_stage(1)
        request.user.score_records.create(
            score=get_score_stage(1), type="能力",
            description="发布一个外部任务")
        team.score += get_score_stage(1)
        team.score_records.create(
            score=get_score_stage(1), type="能力",
            description="发布一个外部任务")
        request.user.save()
        team.save()
        abort(200)


class ExternalTasks(View):
    @fetch_object(ExternalTask.objects, 'task')
    @require_verification_token
    @validate_args({
        'title': forms.CharField(required=False, max_length=20),
        'content': forms.CharField(required=False, max_length=200),
        'deadline': forms.DateField(required=False),
        'expend': forms.IntegerField(required=False, min_value=1),
    })
    def post(self, request, task, **kwargs):
        """再派任务状态下的任务修改
        :param task_id: 任务ID
        :param title: 任务标题
        :param content: 任务内容
        :param deadline: 任务期限

        """
        if check_bad_words(kwargs["title"]) or check_bad_words(kwargs["content"]):
            abort(403, '含有非法词汇')
        if request.user != task.team.owner:
            abort(403, '只有队长可以操作')
        if task.status != 1:
            abort(404, '任务状态错误')

        for k in kwargs:
            setattr(task, k, kwargs[k])
        task.save()
        abort(200)


class TeamExternalTask(View):
    keys = ('id', 'title', 'content', 'status', 'expend', 'expend_actual',
            'deadline', 'assign_num', 'submit_num', 'pay_num', 'finish_time',
            'time_created')

    @fetch_object(ExternalTask.objects, 'task')
    @require_token
    def get(self, request, task):
        """获取外部任务详情

        :return:
            id: 任务id
            executor_id: 执行团队ID
            executor_name: 执行团队名称
            team_id: 团队ID
            team_name: 团队名称
            icon_url: 团队头像
            title: 任务标题
            content: 任务内容
            status: 任务状态 - ('等待接受', 0), ('再派任务', 1),
                              ('等待完成', 2), ('等待验收', 3),
                              ('再次提交', 4), ('等待支付', 6),
                              ('再次支付', 7), ('等待确认', 8),
                              ('按时结束', 9),('超时结束', 10)
            expend: 预计费用
            expend_actual: 实际费用
            assign_num: 分派次数
            submit_num: 提交次数
            pay_num: 支付次数
            deadline: 任务期限
            finish_time: 任务完成时间
            time_created: 任务创建时间
        """

        d = {'executor_id': task.executor.id,
             'executor_name': task.executor.name,
             'team_id': task.team.id,
             'team_name': task.team.name,
             'icon_url': task.team.icon}

        # noinspection PyUnboundLocalVariable
        for k in self.keys:
            d[k] = getattr(task, k)

        return JsonResponse(d)

    @fetch_object(ExternalTask.objects, 'task')
    @require_verification_token
    @validate_args({
        'expend_actual': forms.IntegerField(required=False, min_value=0),
        'pay_time': forms.DateField(required=False),
        'status': forms.IntegerField(required=False, min_value=0, max_value=8),
    })
    def post(self, request, task, expend_actual=None, pay_time=None,
             status=None):
        """
        修改外部任务的状态(默认为None, 后台确认任务是按时还是超时完成)
        :param expend_actual: 实际支付金额(确认支付时传)
        :param pay_time: 支付时间(确认支付时传)
        :param status:
            任务状态 - ('等待接受', 0), ('再派任务', 1),
                      ('等待完成', 2), ('等待验收', 3),
                      ('再次提交', 4), ('等待支付', 6),
                      ('再次支付', 7), ('等待确认', 8),
                      ('按时结束', 9),('超时结束', 10)
        """
        if request.user != task.team.owner \
                and request.user != task.executor.owner:
            abort(403, '非法操作')

        if status is None:
            if request.user != task.executor.owner or task.status != 8:
                abort(403, '非法操作')
            task.finish_time = timezone.now()
            if task.finish_time.date() > task.deadline:
                task.status = 10
            else:
                task.status = 9
            # 积分
            task.executor.score += get_score_stage(1)
            task.executor.score_records.create(
                score=get_score_stage(1), type="能力",
                description="完成一个外部任务")
            task.team.score += get_score_stage(1)
            task.team.score_records.create(
                score=get_score_stage(1), type="能力",
                description="队友完成一个外部任务")
            task.executor.save()
            task.team.save()
            task.save()
            # 发动态
            action.finish_external_task(task.executor, task)
            abort(200)
        elif status == 0:
            if request.user != task.team.owner or task.status != 1:
                abort(403, '非法操作')
            else:
                # 如果任务状态为再派任务-->等待接受，则分派次数+1
                task.assign_num += 1
        elif status == 1:
            if request.user != task.executor.owner or task.status != 0:
                abort(403, '非法操作')
        elif status == 2:
            if request.user != task.executor.owner or task.status != 0:
                abort(403, '非法操作')
        elif status == 3:
            if request.user != task.executor.owner \
                    or (task.status not in [2, 4]):
                abort(403, '非法操作')
            elif task.status == 4:
                # 如果任务状态为再次提交-->等待验收，则提交次数+1
                task.submit_num += 1
        elif status == 4:
            if request.user != task.team.owner or task.status != 3:
                abort(403, '非法操作')
        elif status == 6:
            if request.user != task.team.owner or task.status != 3:
                abort(403, '非法操作')
        elif status == 7:
            if request.user != task.executor.owner or task.status != 8:
                abort(403, '非法操作')
        elif status == 8:
            if request.user != task.team.owner or (task.status not in [6, 7]):
                abort(403, '非法操作')
            elif task.status == 7:
                # 如果任务状态为再次支付-->等待确认，则支付次数+1
                task.pay_num += 1
            # 获取任务的支付信息
            if expend_actual is None or pay_time is None:
                abort(404, '参数不全')
            else:
                task.expend_actual = expend_actual
                task.pay_time = pay_time
        else:
            abort(403, '状态参数错误')

        task.status = status
        task.save()
        abort(200)