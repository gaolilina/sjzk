from datetime import datetime

from django.db import models


class UserFriendManager(models.Manager):
    def get_queryset(self):
        return super(UserFriendManager, self).get_queryset().filter(
            user__is_enabled=True, friend__is_enabled=True)


class UserFriend(models.Model):
    """
    用户好友记录

    """
    user = models.ForeignKey('User', models.CASCADE, 'friend_records')
    friend = models.ForeignKey('User', models.CASCADE, '+')
    create_time = models.DateTimeField(
        '建立关系时间', default=datetime.now, db_index=True)

    enabled = UserFriendManager()

    class Meta:
        db_table = 'user_friend'

    @classmethod
    def exist(cls, user, other_user):
        """
        检查user与other_user是否为好友关系

        """
        return cls.enabled.filter(user=user, friend=other_user).exists()


class UserFriendRequestManager(models.Manager):
    def get_queryset(self):
        return super(UserFriendRequestManager, self).get_queryset().filter(
            sender__is_enabled=True, receiver__is_enabled=True)


class UserFriendRequest(models.Model):
    """
    用户好友申请记录

    """
    sender = models.ForeignKey('User', models.CASCADE, '+')
    receiver = models.ForeignKey('User', models.CASCADE, 'friend_requests')

    description = models.TextField(
        '附带消息', max_length=100, db_index=True)
    create_time = models.DateTimeField(
        '申请时间', default=datetime.now, db_index=True)
    is_read = models.BooleanField(
        '该申请是否已读', default=False, db_index=True)

    enabled = UserFriendRequestManager()

    class Meta:
        db_table = 'user_friend_request'
        ordering = ['-create_time']

    @classmethod
    def exist(cls, sender, receiver):
        """
        检查user是否向other_user发送过好友请求

        """
        return cls.enabled.filter(sender=sender, receiver=receiver).exists()
