import hashlib

from django.contrib.auth.hashers import PBKDF2PasswordHasher
from django.db import models
from django.utils import timezone

from ..models import EnabledManager, Action, Comment, Follower, Liker, Tag,\
    Visitor


__all__ = ['User', 'UserAction', 'UserComment', 'UserContact', 'UserExperience',
           'UserFollower', 'UserFriend', 'UserFriendRequest', 'UserLiker',
           'UserMessage', 'UserTag', 'UserVisitor']


class User(models.Model):
    """用户模型"""

    is_enabled = models.BooleanField(default=True, db_index=True)
    username = models.CharField(
        max_length=20, default=None, null=True, unique=True)
    password = models.CharField(max_length=128)
    phone_number = models.CharField(max_length=11, unique=True)
    token = models.CharField(max_length=32, unique=True)
    time_created = models.DateTimeField(default=timezone.now, db_index=True)

    name = models.CharField(max_length=15, db_index=True)
    description = models.CharField(max_length=100, default='')
    icon = models.CharField(max_length=100)
    gender = models.CharField(max_length=1, default='')
    qq = models.CharField(max_length=20, default='')
    wechat = models.CharField(max_length=20, default='')
    email = models.EmailField(default='')
    birthday = models.DateField(default=None, null=True, db_index=True)
    province = models.CharField(max_length=20, default='', db_index=True)
    city = models.CharField(max_length=20, default='', db_index=True)
    county = models.CharField(max_length=20, default='', db_index=True)

    is_verified = models.BooleanField(default=False, db_index=True)
    real_name = models.CharField(max_length=20, default='', db_index=True)
    id_number = models.CharField(max_length=18, default='', db_index=True)
    id_card = models.CharField(max_length=100)

    is_role_verified = models.BooleanField(default=False, db_index=True)
    role = models.CharField(max_length=20, default='', db_index=True)
    other_number = models.CharField(max_length=20, default='')
    other_card = models.CharField(max_length=100)
    # 学校或公司
    unit1 = models.CharField(max_length=20, default='')
    # 学院或子部门
    unit2 = models.CharField(max_length=20, default='')
    # 专用或职业
    profession = models.CharField(max_length=20, default='')

    objects = models.Manager()
    enabled = EnabledManager()

    class Meta:
        db_table = 'user'
        ordering = ['-time_created']

    def set_password(self, password):
        hasher = PBKDF2PasswordHasher()
        self.password = hasher.encode(password, hasher.salt())

    def check_password(self, password):
        hasher = PBKDF2PasswordHasher()
        return hasher.verify(password, self.password)

    def update_token(self):
        random_content = self.user.phone_number + timezone.now().isoformat()
        hasher = hashlib.md5()
        hasher.update(random_content.encode())
        self.token = hasher.hexdigest()


class UserAction(Action):
    """用户动态"""

    entity = models.ForeignKey('User', models.CASCADE, 'actions')

    class Meta:
        db_table = 'user_action'


class UserComment(Comment):
    """用户评论"""

    entity = models.ForeignKey('User', models.CASCADE, 'comments')

    class Meta:
        db_table = 'user_comment'


class UserContact(models.Model):
    """用户联系人"""

    user = models.ForeignKey('User', models.CASCADE, 'contacts')
    other_user = models.ForeignKey('User', models.CASCADE, '+')
    last_message = models.ForeignKey('Message', models.CASCADE, '+')
    time_updated = models.DateTimeField(auto_now=True, db_index=True)

    class Meta:
        db_table = 'user_contact'
        ordering = ['-time_updated']


class UserExperience(models.Model):
    """用户经历资料"""

    # education, work or fieldwork
    type = models.CharField(max_length=20, db_index=True)
    # 学校或公司
    unit = models.CharField(max_length=20, default='')
    # 职位或专业
    profession = models.CharField(max_length=20, default='')
    degree = models.CharField(max_length=20, default='')
    description = models.CharField(max_length=100, default='')
    time_in = models.DateField(default=None, null=True)
    time_out = models.DateField(default=None, null=True)
    time_created = models.DateTimeField(default=timezone.now, db_index=True)

    class Meta:
        db_table = 'user_follower'
        ordering = ['-time_created']


class UserFollower(Follower):
    """用户关注记录"""

    followed = models.ForeignKey('User', models.CASCADE, 'followers')
    follower = models.ForeignKey('User', models.CASCADE, 'followed_users')

    class Meta:
        db_table = 'user_follower'


class UserFriend(models.Model):
    """用户好友记录"""

    user = models.ForeignKey('User', models.CASCADE, 'friends')
    other_user = models.ForeignKey('User', models.CASCADE, '+')
    time_created = models.DateTimeField(default=timezone.now, db_index=True)

    class Meta:
        db_table = 'user_friend'
        ordering = ['-time_created']


class UserFriendRequest(models.Model):
    """用户好友申请记录"""

    # from user to other_user
    user = models.ForeignKey('User', models.CASCADE, '+')
    other_user = models.ForeignKey('User', models.CASCADE, 'friend_requests')
    description = models.CharField(max_length=100, db_index=True)
    time_created = models.DateTimeField(default=timezone.now, db_index=True)
    is_read = models.BooleanField(default=False, db_index=True)

    class Meta:
        db_table = 'user_friend_request'
        ordering = ['-time_created']


class UserLiker(Liker):
    """用户点赞记录"""

    liked = models.ForeignKey('User', models.CASCADE, 'likers')
    liker = models.ForeignKey('User', models.CASCADE, 'liked_users')

    class Meta:
        db_table = 'user_liker'


class UserMessage(models.Model):
    """消息"""

    user = models.ForeignKey('User', models.CASCADE, 'messages')
    other_user = models.ForeignKey('User', models.CASCADE, '+')
    direction = models.IntegerField(choices=(('收', 0), ('发', 1)))
    content = models.TextField(default='', max_length=100)
    is_read = models.BooleanField(default=False, db_index=True)
    time_created = models.DateTimeField(default=timezone.now, db_index=True)

    is_sharing = models.BooleanField(default=False, db_index=True)
    sharing_object_type = models.TextField(default=None, null=True)
    sharing_object_id = models.IntegerField(default=None, null=True)

    class Meta:
        db_table = 'user_message'
        ordering = ['-time_created']


class UserTag(Tag):
    entity = models.ForeignKey('User', models.CASCADE, 'tags')

    class Meta:
        db_table = 'user_tag'


class UserVisitor(Visitor):
    visited = models.ForeignKey('User', models.CASCADE, 'visitors')
    visitor = models.ForeignKey('User', models.CASCADE, 'visited_users')

    class Meta:
        db_table = 'user_visitor'
