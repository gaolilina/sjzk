from django.db import models


__all__ = ['System']


class System(models.Model):
    """系统设定量"""

    # 版本号
    VERSION_NUMBER = models.FloatField(max_length=10, default=1.0)
    # 最近来访的时间设定
    RECENT_VISITOR_TIME = models.IntegerField(max_length=2, default=24)
    # 积分阶段分值
    SCORE_STAGE_ONE = models.IntegerField(default=5)
    SCORE_STAGE_TWO = models.IntegerField(default=10)
    SCORE_STAGE_THREE = models.IntegerField(default=20)
    SCORE_STAGE_FOUR = models.IntegerField(default=50)
    SCORE_STAGE_FIVE = models.IntegerField(default=100)

    class Meta:
        db_table = 'system'
