from django.db import models


class Field(models.Model):
    class Meta:
        db_table = 'field'

    name = models.CharField(max_length=254, default='', unique=True)
