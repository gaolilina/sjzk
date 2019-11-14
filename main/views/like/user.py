from main.models import User, UserExperience
from main.utils import get_score_stage
from main.views.like import ILikeSomething, SomethingLikers, Liker, ILikeSomethingSimple
from util.decorator.auth import app_auth
from util.decorator.param import fetch_object


class LikedUser(ILikeSomething):
    """点赞和取消点赞"""

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


class UserLikerList(SomethingLikers):
    @app_auth
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


class ILikeUserExperience(ILikeSomethingSimple):
    @fetch_object(UserExperience.objects, 'experience')
    def post(self, request, experience):
        return super().post(request, experience)

    @fetch_object(UserExperience.objects, 'experience')
    def delete(self, request, experience):
        return super().delete(request, experience)
