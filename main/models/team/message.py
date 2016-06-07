from datetime import datetime

from django.core.exceptions import ObjectDoesNotExist
from django.db import models

from main.models import User, Team


class TeamContactManager(models.Manager):
    def get_queryset(self):
        return super(TeamContactManager, self).get_queryset().filter(
            team__is_enabled=True, contact__is_enabled=True)


class TeamContact(models.Model):
    """
    团队的用户联系记录

    """
    team = models.ForeignKey('Team', models.CASCADE, 'user_contacts')
    contact = models.ForeignKey('User', models.CASCADE, '+')
    last_message = models.ForeignKey('Message', models.CASCADE, '+')
    update_time = models.DateTimeField(auto_now=True, db_index=True)

    enabled = TeamContactManager()

    class Meta:
        db_table = 'team_contact'
        ordering = ['-update_time']


class UserContactManager(models.Manager):
    def get_queryset(self):
        return super(UserContactManager, self).get_queryset().filter(
            user__is_enabled=True, contact__is_enabled=True)


class UserContact(models.Model):
    """
    用户的团队联系记录

    """
    user = models.ForeignKey('User', models.CASCADE, 'team_contacts')
    contact = models.ForeignKey('Team', models.CASCADE, '+')
    last_message = models.ForeignKey('Message', models.CASCADE, '+')
    update_time = models.DateTimeField(auto_now=True, db_index=True)

    enabled = UserContactManager()

    class Meta:
        db_table = 'user_contact'
        ordering = ['-update_time']


class TeamMessageManager(models.Manager):
    def get_queryset(self):
        return super(TeamMessageManager, self).get_queryset().filter(
            team__is_enabled=True, other_user__is_enabled=True)


class TeamMessage(models.Model):
    """
    团队发给用户的消息

    """
    team = models.ForeignKey('Team', models.CASCADE, 'user_messages')
    other_user = models.ForeignKey('User', models.CASCADE, '+')
    direction = models.IntegerField(choices=(('收', 0), ('发', 1)))
    is_read = models.BooleanField(default=False, db_index=True)
    create_time = models.DateTimeField(default=datetime.now, db_index=True)

    content = models.TextField(default='', max_length=256, db_index=True)
    is_sharing = models.BooleanField(default=False, db_index=True)
    sharing_object_type = models.TextField(default=None, null=True)
    sharing_object_id = models.IntegerField(default=None, null=True)

    enabled = TeamMessageManager()

    class Meta:
        db_table = 'team_message_receipt'
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


class UserMessageManager(models.Manager):
    def get_queryset(self):
        return super(UserMessageManager, self).get_queryset().filter(
            user__is_enabled=True, other_team__is_enabled=True)


class UserMessage(models.Model):
    """
    用户发给团队的消息

    """
    user = models.ForeignKey('User', models.CASCADE, 'team_messages')
    other_team = models.ForeignKey('Team', models.CASCADE, '+')
    direction = models.IntegerField(choices=(('收', 0), ('发', 1)))
    is_read = models.BooleanField(default=False, db_index=True)
    create_time = models.DateTimeField(default=datetime.now, db_index=True)

    content = models.TextField(default='', max_length=256, db_index=True)
    is_sharing = models.BooleanField(default=False, db_index=True)
    sharing_object_type = models.TextField(default=None, null=True)
    sharing_object_id = models.IntegerField(default=None, null=True)

    enabled = UserMessageManager()

    class Meta:
        db_table = 'user_message_receipt'
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
