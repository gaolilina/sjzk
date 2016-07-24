from django.db import models


class EnabledManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(is_enabled=True)


from .user import *
