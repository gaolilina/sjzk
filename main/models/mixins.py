class IconMixin(object):
    """
    图标/头像 Mixin

    """
    # noinspection PyUnresolvedReferences
    @property
    def icon_url(self):
        return self.icon.url if self.icon else None


# noinspection PyUnresolvedReferences
class CountMixin(object):
    """
    各种计数

    """
    @property
    def fan_count(self):
        return self.follower_records.filter(follower__is_enabled=True).count()

    @property
    def followed_count(self):
        return self.followed_user_records.filter(followed__is_enabled=True).count() + \
               self.followed_team_records.filter(followed__is_enabled=True).count()

    @property
    def friend_count(self):
        return self.friend_records.count()

    @property
    def like_count(self):
        return self.liker_records.filter(liker__is_enabled=True).count()

    @property
    def visitor_count(self):
        return self.visitor_records.filter(visitor__is_enabled=True).count()
