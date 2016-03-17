from django.db import models

from user.models import User


class UserFriendRelationship(models.Model):
    """
    APP好友关系

    """
    user = models.ForeignKey(
        User, models.CASCADE, related_name='friend_relationship')
    friend = models.ForeignKey(User, models.CASCADE)
    create_time = models.DateTimeField('建立关系时间', db_index=True)

    class Meta:
        db_table = 'user_friend'

    def __repr__(self):
        return '<Friend - %s / %s>' % (self.user.name, self.friend.name)


class UserFriendRequest(models.Model):
    """
    好友申请信息

    """
    requested = models.ForeignKey(
        User, models.CASCADE, related_name='friend_requester_info',
        verbose_name='被申请者')
    requester = models.ForeignKey(
        User, models.CASCADE, related_name='friend_requested_info',
        verbose_name='申请者')
    description = models.TextField('附带消息', max_length=100, db_index=True)
    create_time = models.DateTimeField('申请时间', db_index=True)
    is_read = models.BooleanField(
        '该申请是否已读', default=False, db_index=True)
    is_ignored = models.BooleanField(
        '该申请者是否已被忽略', default=False, db_index=True)

    class Meta:
        db_table = 'user_friend_request'
        ordering = ['-create_time']

    def __repr__(self):
        return '<Friend Request - %s / %s>' % (
            self.requested.name, self.requester.name)
