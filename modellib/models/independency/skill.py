from django.db import models


class Skill(models.Model):
    class Meta:
        db_table = 'skill'

    name = models.CharField(max_length=254, default='', unique=True)
    parent = models.ForeignKey('Skill', related_name='children', null=True, default=None)
    enable = models.BooleanField(default=True)
