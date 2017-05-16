from ..models.system import System
from ..utils import abort


def get_score_stage(stage=1):
    system = System.objects.get(id=1)
    if stage == 1:
        return system.SCORE_VALUE_ONE
    elif stage == 2:
        return system.SCORE_VALUE_TWO
    elif stage == 3:
        return system.SCORE_VALUE_THREE
    elif stage == 4:
        return system.SCORE_VALUE_FOUR
    elif stage == 5:
        return system.SCORE_VALUE_FIVE
    else:
        abort(400, '系统的积分值获取错误')
