import hashlib

from django.db import models
from django.utils import timezone

from ..models import EnabledManager, Action, Comment, Follower, Liker, Tag,\
    Visitor


__all__ = ['User', 'UserAction', 'UserActionLiker', 'UserActionComment',
           'UserComment', 'UserExperience', 'UserFollower', 'UserFriend',
           'UserFriendRequest', 'UserLiker', 'UserTag', 'UserValidationCode',
           'UserVisitor', 'UserFeedback', 'UserFeature', 'UserBehavior',
           'UserScore']


class User(models.Model):
    """用户模型"""

    is_enabled = models.BooleanField(default=True, db_index=True)
    username = models.CharField(
        max_length=20, default=None, null=True, unique=True)
    password = models.CharField(max_length=128)
    phone_number = models.CharField(max_length=11, unique=True)
    token = models.CharField(max_length=256)
    time_created = models.DateTimeField(default=timezone.now, db_index=True)

    name = models.CharField(max_length=15)
    description = models.CharField(max_length=100, default='')
    icon = models.CharField(max_length=100, default='')
    # 性别,0：未知，1：男，2：女
    gender = models.IntegerField(default=0, db_index=True)
    qq = models.CharField(max_length=20, default='')
    wechat = models.CharField(max_length=20, default='')
    email = models.EmailField(default='')
    birthday = models.DateField(default=None, null=True, db_index=True)
    province = models.CharField(max_length=20, default='')
    city = models.CharField(max_length=20, default='')
    county = models.CharField(max_length=20, default='')
    adept_field = models.CharField(default='', max_length=20)
    adept_skill = models.CharField(default='', max_length=20)
    expect_role = models.CharField(max_length=20, default='')
    follow_field = models.CharField(default='', max_length=20)
    follow_skill = models.CharField(default='', max_length=20)


    # 是否通过实名验证,0:未提交, 1:待审核, 2:身份证审核通过, 3:审核未通过,请重新提交,
    # 4:Eid审核通过
    is_verified = models.IntegerField(default=0, db_index=True)
    real_name = models.CharField(max_length=20, default='')
    id_number = models.CharField(max_length=18, default='')
    id_card = models.CharField(max_length=100, default='')

    # 是否通过身份验证，0:未提交, 1:待审核, 2:审核通过, 3:审核未通过,请重新提交
    is_role_verified = models.IntegerField(default=0, db_index=True)
    role = models.CharField(max_length=20, default='')
    other_number = models.CharField(max_length=20, default='')
    other_card = models.CharField(max_length=100, default='')
    # 学校或公司
    unit1 = models.CharField(max_length=20, default='')
    # 学院或子部门
    unit2 = models.CharField(max_length=20, default='')
    # 专业或职业
    profession = models.CharField(max_length=20, default='')

    # 用户积分
    score = models.IntegerField(default=0, db_index=True)

    # 用户eID信息
    eid_issuer = models.CharField(max_length=20, default='')
    eid_issuer_sn = models.CharField(max_length=20, default='')
    eid_sn = models.CharField(max_length=50, default='')

    # 邀请码
    invitation_code = models.CharField(max_length=8)
    used_invitation_code = models.CharField(max_length=8, default='')

    objects = models.Manager()
    enabled = EnabledManager()

    class Meta:
        db_table = 'user'
        ordering = ['-time_created']

    def set_password(self, password):
        """设置密码"""

        # hasher = PBKDF2PasswordHasher()
        # self.password = hasher.encode(password, hasher.salt())
        # 加密方式改为MD5
        hasher = hashlib.md5(password.encode(encoding='utf-8'))
        self.password = hasher.hexdigest()

    def check_password(self, password):
        """检查密码"""

        # hasher = PBKDF2PasswordHasher()
        # return hasher.verify(password, self.password)
        # 验证方式也改为MD5
        hasher = hashlib.md5(password.encode(encoding='utf-8'))
        password1 = hasher.hexdigest()
        return password1 == self.password

    def update_token(self):
        """更新用户令牌"""

        random_content = self.phone_number + timezone.now().isoformat()
        hasher = hashlib.md5()
        hasher.update(random_content.encode())
        self.token = hasher.hexdigest()

    def save_and_generate_name(self):
        """保存当前实例并生成序列用户名"""

        self.save()
        self.name = '创易汇用户 #{}'.format(self.id)
        self.save()

    def create_invitation_code(self):
        """生成邀请码"""

        code = ''
        while True:
            random_content = self.phone_number + timezone.now().isoformat()
            hasher = hashlib.md5()
            hasher.update(random_content.encode())
            code = hasher.hexdigest()[:8]
            c = User.objects.filter(invitation_code=code).count()
            if c == 0:
                break
        self.invitation_code = code


class UserComment(Comment):
    """用户评论"""

    entity = models.ForeignKey('User', models.CASCADE, 'comments')

    class Meta:
        db_table = 'user_comment'


class UserAction(Action):
    """用户动态"""

    entity = models.ForeignKey('User', models.CASCADE, 'actions')

    class Meta:
        db_table = 'user_action'


class UserActionLiker(Liker):
    """用户动态点赞记录"""

    liked = models.ForeignKey('UserAction', models.CASCADE, 'likers')
    liker = models.ForeignKey('User', models.CASCADE, 'liked_user_actions')

    class Meta:
        db_table = 'user_action_liker'


class UserActionComment(Comment):
    """用户动态评论记录"""

    entity = models.ForeignKey('UserAction', models.CASCADE, 'comments')

    class Meta:
        db_table = 'user_action_comment'


class UserExperience(models.Model):
    """用户经历资料"""

    user = models.ForeignKey('User', models.CASCADE, 'experiences')
    # education, work or fieldwork
    type = models.CharField(max_length=20)
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
        db_table = 'user_experience'
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

    # send from other_user
    user = models.ForeignKey('User', models.CASCADE, 'friend_requests')
    other_user = models.ForeignKey('User', models.CASCADE, '+')
    description = models.CharField(max_length=100)
    time_created = models.DateTimeField(default=timezone.now, db_index=True)

    class Meta:
        db_table = 'user_friend_request'
        ordering = ['-time_created']


class UserLiker(Liker):
    """用户点赞记录"""

    liked = models.ForeignKey('User', models.CASCADE, 'likers')
    liker = models.ForeignKey('User', models.CASCADE, 'liked_users')

    class Meta:
        db_table = 'user_liker'


class UserTag(Tag):
    """用户标签"""

    entity = models.ForeignKey('User', models.CASCADE, 'tags')

    class Meta:
        db_table = 'user_tag'


class UserValidationCode(models.Model):
    """验证码"""

    phone_number = models.CharField(max_length=11, primary_key=True)
    code = models.CharField(max_length=6, default=None)
    time_expired = models.DateTimeField()

    class Meta:
        db_table = 'user_validation_code'

    @classmethod
    def verify(cls, phone_number, code):
        """校验验证码"""

        try:
            now = timezone.now()
            r = cls.objects.get(phone_number=phone_number)
        except cls.DoesNotExist:
            return False
        else:
            return True if code == r.code and now <= r.time_expired else False

    @classmethod
    def generate(cls, phone_number, minutes=3):
        """为某个手机号生成验证码"""

        from datetime import timedelta
        from random import Random

        try:
            r = cls.objects.get(phone_number=phone_number)
        except cls.DoesNotExist:
            r = cls(phone_number)
        r.time_expired = timezone.now() + timedelta(minutes=minutes)
        random = Random()
        while True:
            code = ''
            for i in range(6):
                code += str(random.choice(range(0, 10)))
            if code != r.code:
                r.code = code
                break
        r.save()
        return r.code


class UserVisitor(Visitor):
    """用户访客"""

    visited = models.ForeignKey('User', models.CASCADE, 'visitors')
    visitor = models.ForeignKey('User', models.CASCADE, 'visited_users')

    class Meta:
        db_table = 'user_visitor'


class UserFeedback(models.Model):
    """用户意见反馈"""
    user = models.ForeignKey('User', models.CASCADE, 'feedback')
    content = models.TextField(max_length=100)
    time_created = models.DateTimeField(default=timezone.now, db_index=True)

    class Meta:
        db_table = 'user_feedback'
        ordering = ['-time_created']


class UserScore(models.Model):
    """用户积分明细"""

    user = models.ForeignKey('User', models.CASCADE, 'score_records')
    score = models.IntegerField(db_index=True)
    description = models.CharField(max_length=100, default='')
    type = models.CharField(max_length=10, default='')
    time_created = models.DateTimeField(default=timezone.now, db_index=True)

    class Meta:
        db_table = 'user_score_record'


class UserFeature(models.Model):
    """用户特征模型"""

    user = models.OneToOneField('User', models.CASCADE,
                                related_name='feature_model')
    data = models.TextField(default="{}")

    class Meta:
        db_table = 'user_feature'


class UserBehavior(models.Model):
    """用户行为记录"""

    user = models.ForeignKey('User', models.CASCADE, 'behaviors')
    # like, view
    behavior = models.CharField(max_length=10)
    # user, team
    object_type = models.CharField(max_length=20)
    object_id = models.IntegerField()
    time_created = models.DateTimeField(default=timezone.now, db_index=True)

    class Meta:
        db_table = 'user_behavior'
        ordering = ['-time_created']
