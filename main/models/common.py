from datetime import datetime

from django.db import models


__all__ = ['Action']


class Action(models.Model):
    """动态"""

    entity = None
    action = models.CharField(max_length=20)
    time_created = models.DateTimeField(default=datetime.now, db_index=True)
    object_type = models.CharField(max_length=20)
    object_id = models.IntegerField(db_index=True)
    related_object_type = models.CharField(default=None, null=True, max_length=20)
    related_object_id = models.IntegerField(default=None, null=True, db_index=True)

    class Meta:
        abstract = True
        ordering = ['-create_time']
