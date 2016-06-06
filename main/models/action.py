from datetime import datetime

from django.core.exceptions import ObjectDoesNotExist
from django.db import models, transaction

from main.models import User, Team
from main.models.team.need import TeamNeed
from main.models.team.achievement import TeamAchievement
from main.models.team.task import TeamTask


class ActionManager(object):
    @staticmethod
    def participate_in_activity(obj, activity):
        """
        记录参加活动事件

        """
        obj.actions.create(action='participate_in_activity',
                           object=activity)

    @staticmethod
    def participate_in_contest(obj, contest):
        """
        记录参赛事件

        """
        obj.actions.create(action='participate_in_contest',
                           object=contest)

    @staticmethod
    @transaction.atomic
    def create_team(user, team):
        """
        记录创建团队事件

        """
        user.actions.create(action='create_team', object=team)
        team.actions.create(action='create_team', object=user)

    @staticmethod
    @transaction.atomic
    def join_team(user, team):
        """
        记录参加团队事件

        """
        user.actions.create(action='join_team', object=team)
        team.actions.create(action='join_team', object=user)

    @staticmethod
    @transaction.atomic
    def leave_team(user, team):
        """
        记录退出团队事件

        """
        user.actions.create(action='leave_team', object=team)
        team.actions.create(action='leave_team', object=user)

    @staticmethod
    def create_need(team, need):
        """
        记录发布需求事件

        """
        team.actions.create(action='create_need', object=need)

    @staticmethod
    def meet_need(team, need):
        """
        记录需求满足事件

        """
        team.actions.create(action='meet_need', object=need)

    @staticmethod
    def create_achievement(team, achievement):
        """
        记录发布成果事件

        """
        team.actions.create(action='create_achievement', object=achievement)

    @staticmethod
    def create_service(team, service):
        """
        记录发布服务事件

        """
        team.actions.create(action='create_service', object=service)

    @staticmethod
    def provide_service(team, obj, service):
        """
        记录提供服务事件

        """
        team.actions.create(action='provide_service', object=obj,
                            related_object=service)

    @staticmethod
    def create_task(team, task):
        """
        记录创建任务事件

        """
        team.actions.create(action='create_service', object=task)

    @staticmethod
    def finish_task(team, task):
        """
        记录完成任务事件

        """
        team.actions.create(action='create_service', object=task)


class Action(models.Model):
    """
    动态

    Examples:
        * 用户A创建了团队B（作为用户动态）
            subject = user_a, action = 'create_team', object = team_b
        * 用户A键入了团队B（作为团队动态）
            subject = team_b, action = 'join_team', object = user_a
        * 团队C向用户D提供了服务E（作为团队动态）
            subject = team_c, action = 'provide_service', object = user_e,
            related_object = service_e
    """
    # 主语
    subject = None
    # 谓语
    action = models.CharField(max_length=20)
    # 宾语
    object_id = models.IntegerField(db_index=True)
    object_type = models.CharField(max_length=10)
    # 额外的相关对象
    related_object_id = models.IntegerField(
        default=None, null=True, db_index=True)
    related_object_type = models.CharField(
        default=None, null=True, max_length=10)
    create_time = models.DateTimeField(default=datetime.now, db_index=True)

    class Meta:
        abstract = True
        ordering = ['-create_time']

    @property
    def is_enabled(self):
        c = True if self.related_object is None \
            else self.related_object.is_enabled
        return self.subject.is_enabled and self.object.is_enabled and c

    # 有关对象类型与模型Manager对应表
    # TODO: 补充其他类型
    _type_managers = {
        'user': User.enabled,
        'team': Team.enabled,
        'need': TeamNeed.enabled,
        'achievement': TeamAchievement.enabled,
        'task': TeamTask.enabled,
    }

    def _get_object(self, type, id):
        """
        根据类型、ID获取对象

        """
        if not id:
            return None
        try:
            return self._type_managers[type].get(id=id)
        except (KeyError, ObjectDoesNotExist):
            return None

    @property
    def object(self):
        return self._get_object(self.object_type, self.object_id)

    @object.setter
    def object(self, obj):
        self.object_id = obj.id
        self.object_type = obj.__class__.__name__.lower()

    @property
    def related_object(self):
        return self._get_object(self.related_object_type,
                                self.related_object_id)

    @related_object.setter
    def related_object(self, obj):
        self.related_object_id = obj.id
        self.related_object_type = obj.__class__.__name__.lower()


class UserAction(Action):
    """
    用户动态

    """
    subject = models.ForeignKey('User', models.CASCADE, 'actions')

    class Meta:
        db_table = 'user_action'


class TeamAction(Action):
    """
    团队动态

    """
    subject = models.ForeignKey('Team', models.CASCADE, 'actions')

    class Meta:
        db_table = 'team_action'
