from django.db import models


__all__ = ['System', 'IllegalWord']


class System(models.Model):
    """系统设定量"""

    # 版本号
    VERSION_NUMBER = models.FloatField(default=1.0)
    # 最近来访的时间设定
    RECENT_VISITOR_TIME = models.IntegerField(default=24)
    # 积分阶段分值1
    SCORE_STAGE_ONE = models.IntegerField(default=10)
    # 积分阶段分值2
    SCORE_STAGE_TWO = models.IntegerField(default=20)
    # 积分阶段分值3
    SCORE_STAGE_THREE = models.IntegerField(default=50)
    # 积分阶段分值4
    SCORE_STAGE_FOUR = models.IntegerField(default=100)
    # 积分阶段分值5
    SCORE_STAGE_FIVE = models.IntegerField(default=200)

    class Meta:
        db_table = 'system'


class IllegalWord(models.Model):
    """系统过滤词"""

    # 非法词汇
    word = models.CharField(max_length=20, unique=True)

    class Meta:
        db_table = 'illegal_word'
