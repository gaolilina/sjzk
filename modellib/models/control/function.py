from django.db import models


class Function(models.Model):
    class Meta:
        abstract = True

    id = models.CharField(max_length=100, null=False, primary_key=True)
    name = models.CharField(max_length=100, null=False)
    enable = models.NullBooleanField(default=True)
    needVerify = models.NullBooleanField(default=True)
    category = models.CharField(max_length=100, default='')


class CMSFunction(Function):
    ''' cms 上的功能'''

    class Meta:
        db_table = 'function_cms'
