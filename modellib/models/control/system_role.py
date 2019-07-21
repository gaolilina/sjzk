import sys

from django.db import models


class SystemRole(models.Model):
    class Meta:
        abstract = True

    name = models.CharField(max_length=100, null=False)
    enable = models.BooleanField(default=True)
    category = models.CharField(max_length=100, default='')


class CMSRole(SystemRole):
    ID_ADMIN = 1

    class Meta:
        db_table = 'role_cms'

    functions = models.ManyToManyField('CMSFunction', related_name='+')
    level = models.IntegerField(default=10000)
    # 默认是超管的下级角色
    parent_role = models.ForeignKey('CMSRole', related_name='child_roles', default=ID_ADMIN)

    def is_admin(self):
        return self.id == self.ID_ADMIN
