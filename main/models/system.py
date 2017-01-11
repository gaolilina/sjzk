from django.db import models


__all__ = ['System']


class System(models.Model):
    """系统设定量"""

    VERSION_NUMBER = models.CharField(max_length=20)

    class Meta:
        db_table = 'system'
