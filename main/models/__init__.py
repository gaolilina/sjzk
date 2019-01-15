from django.db import models


class EnabledManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(is_enabled=True)


from .common import *
from .user import *
from .team import *
from .forum import *
from .activity import *
from .competition import *
from .system import *
from .report import *
from .lab import *
from .topic import *
from .vote import *
from .achievement import *
