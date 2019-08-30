from main.models import Team
from main.utils import get_score_stage
from main.views.like import LikedEntity
from util.decorator.param import fetch_object


class LikedTeam(LikedEntity):
    @fetch_object(Team.enabled, 'team')
    def get(self, request, team):
        return super().get(request, team)

    @fetch_object(Team.enabled, 'team')
    def post(self, request, team):
        # 积分
        team.score += get_score_stage(1)
        team.score_records.create(
            score=get_score_stage(1), type="受欢迎度", description="他人点赞")
        team.save()
        return super().post(request, team)

    @fetch_object(Team.enabled, 'team')
    def delete(self, request, team):
        # 积分
        team.score -= get_score_stage(1)
        team.score_records.create(
            score=-get_score_stage(1), type="受欢迎度", description="他人取消点赞")
        team.save()
        return super().delete(request, team)