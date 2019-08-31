from main.models import Team, User
from main.utils import get_score_stage
from main.views.like import ILikeSomething, Liker, SomethingLikers
from util.decorator.auth import app_auth
from util.decorator.param import fetch_object


class LikedTeam(ILikeSomething):
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


class TeamLiker(Liker):
    @fetch_object(Team.enabled, 'team')
    @fetch_object(User.enabled, 'other_user')
    @app_auth
    def get(self, request, team, other_user):
        return super(TeamLiker, self).get(request, team, other_user)


class TeamLikerList(SomethingLikers):
    @app_auth
    @fetch_object(Team.enabled, 'team')
    def get(self, request, team):
        return super().get(request, team)
