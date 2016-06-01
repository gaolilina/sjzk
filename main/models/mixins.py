class IconMixin(object):
    """
    图标/头像 Mixin

    """
    # noinspection PyUnresolvedReferences
    @property
    def icon_url(self):
        return self.icon.url if self.icon else None


class LikeMixin(object):
    """
    点赞数 Mixin

    """
    # noinspection PyUnresolvedReferences
    @property
    def like_count(self):
        return self.liker_records.filter(liker__is_enabled=True).count()


class FollowMixin(object):
    """
    粉丝数 Mixin

    """
    # noinspection PyUnresolvedReferences
    @property
    def fan_count(self):
        return self.follower_records.filter(follower__is_enabled=True).count()
