from ..models.system import System
from ..utils import abort


def get_score_stage(stage=1):
    system = System.objects.get(id=1)
    if stage == 1:
        return system.SCORE_STAGE_ONE
    elif stage == 2:
        return system.SCORE_STAGE_TWO
    elif stage == 3:
        return system.SCORE_STAGE_THREE
    elif stage == 4:
        return system.SCORE_STAGE_FOUR
    elif stage == 5:
        return system.SCORE_STAGE_FIVE
    else:
        abort(400, 'wrong score stage')
