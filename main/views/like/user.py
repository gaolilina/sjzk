from main.models import User
from main.utils import get_score_stage
from main.views.common import LikerList, Liker
from main.views.like import LikedEntity
from util.decorator.auth import app_auth
from util.decorator.param import fetch_object


class LikedUser(LikedEntity):
    @fetch_object(User.enabled, 'user')
    def get(self, request, user):
        return super().get(request, user)

    @fetch_object(User.enabled, 'user')
    def post(self, request, user):
        # 积分
        user.score += get_score_stage(1)
        user.score_records.create(
            score=get_score_stage(1), type="受欢迎度", description="他人点赞")
        user.save()
        return super().post(request, user)

    @fetch_object(User.enabled, 'user')
    def delete(self, request, user):
        # 积分
        user.score -= get_score_stage(1)
        user.score_records.create(
            score=-get_score_stage(1), type="受欢迎度", description="他人取消点赞")
        user.save()
        return super().delete(request, user)


class UserLikerList(LikerList):
    @app_auth
    @fetch_object(User.enabled, 'user')
    def get(self, request, user=None):
        user = user or request.user
        return super().get(request, user)


class UserLiker(Liker):
    @fetch_object(User.enabled, 'user')
    @fetch_object(User.enabled, 'other_user')
    @app_auth
    def get(self, request, other_user, user=None):
        user = user or request.user
        return super(UserLiker, self).get(request, user, other_user)