from datetime import datetime

from django.db import models
from django.db.models import Q


class MessageManager(models.Manager):
    def get_queryset(self):
        return super(MessageManager, self).get_queryset().filter(
            sender__is_enabled=True, receiver__is_enabled=True,
        )

    def related_to(self, user, other_user=None):
        """
        获取与某个或某两个用户相关的消息的 Query Set

        """
        if other_user:
            return self.get_queryset().filter(
                Q(sender=user, receiver=other_user) |
                Q(sender=other_user, receiver=user)
            )
        else:
            return self.get_queryset().filter(
                Q(sender=user) | Q(receiver=user)
            )


class Message(models.Model):
    """
    消息

    """
    sender = models.ForeignKey('User', models.CASCADE, '+')
    receiver = models.ForeignKey('User', models.CASCADE, '+')
    data = models.TextField(max_length=256, db_index=True)
    is_read = models.BooleanField(default=False, db_index=True)
    create_time = models.DateTimeField(default=datetime.now, db_index=True)

    enabled = MessageManager()

    class Meta:
        db_table = 'message'
        ordering = ['-create_time']


class ContactManager(models.Manager):
    def get_queryset(self):
        return super(ContactManager, self).get_queryset().filter(
            user_a__is_enabled=True, user_b__is_enabled=True,
        )

    def related_to(self, user):
        """
        获取与某个用户相关的联系人的 Query Set

        """
        return self.get_queryset().filter(Q(user_a=user) | Q(user_b=user))

    def update_record(self, user, other_user, last_message):
        """
        更新联系人记录

        :param user: 用户
        :param other_user: 另一用户
        :param last_message: 最近一条消息

        """
        qs = self.get_queryset().filter(Q(user_a=user, user_b=other_user) |
                                        Q(user_b=user, user_a=other_user))
        if qs.exists():
            qs[0].last_message = last_message
            qs[0].save()
        else:
            r = self.create(user_a=user, user_b=other_user,
                            last_message=last_message)


class Contact(models.Model):
    """
    联系人记录

    """
    user_a = models.ForeignKey('User', models.CASCADE, '+')
    user_b = models.ForeignKey('User', models.CASCADE, '+')
    last_message = models.ForeignKey('Message', models.CASCADE, '+')
    update_time = models.DateTimeField(auto_now=True, db_index=True)

    enabled = ContactManager()

    class Meta:
        db_table = 'contact'
        ordering = ['-update_time']
