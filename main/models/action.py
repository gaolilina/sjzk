from datetime import datetime

from django.core.exceptions import ObjectDoesNotExist
from django.db import models


class Action(models.Model):
    """动态

    Examples:
        * 用户A创建了团队B
            subject = user_a, action = 'create_team', object = team_b
        * 团队C向用户D提供了服务E
            subject = team_c, action = 'provide_service', object = user_e,
            related_object = service_e
    """
    action = models.CharField(max_length=20)

    subject_type = models.CharField(max_length=20)
    subject_id = models.IntegerField(db_index=True)

    object_type = models.CharField(max_length=20)
    object_id = models.IntegerField(db_index=True)

    related_object_type = models.CharField(default=None, null=True, max_length=20)
    related_object_id = models.IntegerField(default=None, null=True, db_index=True)

    time_created = models.DateTimeField(default=datetime.now, db_index=True)

    class Meta:
        db_table = 'action'
        ordering = ['-create_time']

    # noinspection PyShadowingBuiltins
    def _get_entity(self, type, id):
        """根据类型、ID获取对象"""

        from ..models import User, Team, TeamAchievement, TeamNeed, TeamTask

        # 有关对象类型与模型Manager对应表
        # TODO: 补充其他类型
        types = {
            'user': User,
            'team': Team,
            'teamachievement': TeamAchievement,
            'teamneed': TeamNeed,
            'teamtask': TeamTask
        }
        if not id:
            return None
        try:
            return self.types[type].objects.get(id=id)
        except (KeyError, ObjectDoesNotExist):
            return None

    @property
    def subject(self):
        return self._get_entity(self.subject_type, self.subject_id)

    @subject.setter
    def subject(self, obj):
        self.subject_id = obj.id
        self.subject_type = obj.__class__.__name__.lower()

    @property
    def object(self):
        return self._get_entity(self.object_type, self.object_id)

    @object.setter
    def object(self, obj):
        self.object_id = obj.id
        self.object_type = obj.__class__.__name__.lower()

    @property
    def related_object(self):
        return self._get_entity(self.related_object_type, self.related_object_id)

    @related_object.setter
    def related_object(self, obj):
        self.related_object_id = obj.id
        self.related_object_type = obj.__class__.__name__.lower()
