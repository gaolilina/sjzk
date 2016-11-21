from django.db import models
from django.utils import timezone

__all__ = ['OperationLog']


class OperationLog(models.Model):
    """活动创建者"""

    time = models.DateTimeField(default=timezone.now, db_index=True)
    table = models.CharField(max_length=128)
    data_id = models.IntegerField()
    operate_type = models.IntegerField()
    user = models.ForeignKey('AdminUser', models.CASCADE, '+')

    class Meta:
        db_table = 'operation_log'
