from django.db import models

from . import Action, Liker, Comment, Favorer

__all__ = ['System', 'IllegalWord', 'SystemAction', 'SystemActionLiker',
           'SystemActionComment', 'SystemActionFavorer']


class System(models.Model):
    """系统设定量"""

    # 版本号
    VERSION_NUMBER = models.FloatField(default=1.0)
    # 积分分值1
    SCORE_VALUE_ONE = models.IntegerField(default=10)
    # 积分分值2
    SCORE_VALUE_TWO = models.IntegerField(default=20)
    # 积分分值3
    SCORE_VALUE_THREE = models.IntegerField(default=50)
    # 积分分值4
    SCORE_VALUE_FOUR = models.IntegerField(default=100)
    # 积分分值5
    SCORE_VALUE_FIVE = models.IntegerField(default=200)

    class Meta:
        db_table = 'system'


class IllegalWord(models.Model):
    """系统过滤词"""

    # 非法词汇
    word = models.CharField(max_length=20, unique=True)

    class Meta:
        db_table = 'illegal_word'


class SystemAction(Action):
    """系统动态"""

    entity = models.CharField(max_length=10, default='system')

    class Meta:
        db_table = 'system_action'


class SystemActionLiker(Liker):
    """系统动态点赞记录"""

    liked = models.ForeignKey('SystemAction', models.CASCADE, 'likers')
    liker = models.ForeignKey('User', models.CASCADE, 'liked_system_actions')

    class Meta:
        db_table = 'system_action_liker'


class SystemActionComment(Comment):
    """系统动态评论记录"""

    entity = models.ForeignKey('SystemAction', models.CASCADE, 'comments')

    class Meta:
        db_table = 'system_action_comment'

class SystemActionFavorer(Favorer):
    """系统动态收藏记录"""

    favored = models.ForeignKey('SystemAction', models.CASCADE, 'favorers')
    favorer = models.ForeignKey('User', models.CASCADE, 'favored_system_actions')

    class Meta:
        db_table = 'system_action_favorer'
