from datetime import datetime

from django.core.exceptions import ObjectDoesNotExist
from django.db import models

from main.models import User, Team


class ContactManager(models.Manager):
    def get_queryset(self):
        return super(ContactManager, self).get_queryset().filter(
            user__is_enabled=True, contact__is_enabled=True)


class Contact(models.Model):
    """
    联系记录

    """
    user = models.ForeignKey('User', models.CASCADE, 'contacts')
    contact = models.ForeignKey('User', models.CASCADE, '+')
    last_message = models.ForeignKey('Message', models.CASCADE, '+')
    update_time = models.DateTimeField(auto_now=True, db_index=True)

    enabled = ContactManager()

    class Meta:
        db_table = 'contact'
        ordering = ['-update_time']


class MessageManager(models.Manager):
    def get_queryset(self):
        return super(MessageManager, self).get_queryset().filter(
            user__is_enabled=True, other_user__is_enabled=True)


class Message(models.Model):
    """
    消息

    """
    user = models.ForeignKey('User', models.CASCADE, 'messages')
    other_user = models.ForeignKey('User', models.CASCADE, '+')
    direction = models.IntegerField(choices=(('收', 0), ('发', 1)))
    is_read = models.BooleanField(default=False, db_index=True)
    create_time = models.DateTimeField(default=datetime.now, db_index=True)

    content = models.TextField(default='', max_length=256, db_index=True)
    is_sharing = models.BooleanField(default=False, db_index=True)
    sharing_object_type = models.TextField(default=None, null=True)
    sharing_object_id = models.IntegerField(default=None, null=True)

    enabled = MessageManager()

    class Meta:
        db_table = 'message_receipt'
        ordering = ['-create_time']

    @property
    def sharing_object_name(self):
        """
        被分享对象的名称

        """
        try:
            if self.sharing_type == 'user':
                return User.enabled.get(id=self.sharing_object_id).name
            elif self.sharing_type == 'team':
                return Team.enabled.get(id=self.sharing_object_name).name
            else:
                return None
        except ObjectDoesNotExist:
            return None

    @property
    def sharing_object_icon_url(self):
        """
        被分享对象的图标URL

        """
        try:
            if self.sharing_type == 'user':
                return User.enabled.get(id=self.sharing_object_id).icon_url
            elif self.sharing_type == 'team':
                return Team.enabled.get(id=self.sharing_object_name).icon_url
            else:
                return None
        except ObjectDoesNotExist:
            return None
