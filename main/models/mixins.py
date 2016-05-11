class IconMixin(object):
    """
    图标/头像 Mixin

    """
    icon = None

    @property
    def icon_url(self):
        return self.icon.url if self.icon else None
