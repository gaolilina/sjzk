from django.db import models


class UserNeed(models.Model):
    """用户需求信息"""

    user = models.ForeignKey('main.User', models.CASCADE, 'needs')
    desc = models.CharField(max_length=256)
    # 领域
    field = models.CharField(default='', max_length=256)
    # 点赞
    likers = models.ManyToManyField('main.User', related_name='likeUserNeeds')
    time_created = models.DateTimeField(auto_now_add=True, null=True, default=None)

    class Meta:
        db_table = 'need_user'
        ordering = ['-time_created']
