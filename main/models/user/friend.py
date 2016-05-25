from datetime import datetime

from django.db import models, transaction
from django.db.models import Q


class UserFriendManager(models.Manager):
    def get_queryset(self):
        return super(UserFriendManager, self).get_queryset().filter(
            user__is_enabled=True, friend__is_enabled=True)

    def exist(self, user, other_user):
        """
        检查任意两个用户是否为好友关系

        """
        return self.get_queryset().filter(user=user, friend=other_user).exists()

    def create_relation(self, user, other_user):
        """
        建立好友关系，要求user收到过other_user的好友申请

        """
        with transaction.atomic():
            user.friend_requests.get(sender=other_user).delete()
            self.create(user=user, friend=other_user)
            self.create(user=other_user, friend=user)

    def remove_relation(self, user, other_user):
        """
        移除好友关系

        """
        self.get_queryset().filter(
            Q(user=user, friend=other_user) |
            Q(user=other_user, friend=user)).delete()


class UserFriend(models.Model):
    """
    用户好友记录

    """
    user = models.ForeignKey('User', models.CASCADE, 'friend_records')
    friend = models.ForeignKey('User', models.CASCADE, '+')
    create_time = models.DateTimeField(default=datetime.now, db_index=True)

    enabled = UserFriendManager()

    class Meta:
        db_table = 'user_friend'


class UserFriendRequestManager(models.Manager):
    def get_queryset(self):
        return super(UserFriendRequestManager, self).get_queryset().filter(
            sender__is_enabled=True, receiver__is_enabled=True)

    def exist(self, sender, receiver):
        """
        检查一个用户是否向另一个用户发送过好友请求

        """
        return self.get_queryset().filter(
            sender=sender, receiver=receiver).exists()


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
