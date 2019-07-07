from django.db import models


class AppLog(models.Model):
    class Meta:
        db_table = 'log_app'

    url = models.CharField(max_length=256, default='')
    event = models.CharField(max_length=256, default='', null=True)
    user = models.ForeignKey('main.User', related_name='logs', null=True, default=None)
    time = models.DateTimeField(auto_now_add=True)
