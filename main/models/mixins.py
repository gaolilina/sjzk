from django.db import models


class IconMixin(models.Model):
    """
    图标/头像 Mixin

    """
    icon = models.ImageField(db_index=True)

    @property
    def icon_url(self):
        return self.icon.url if self.icon else None
