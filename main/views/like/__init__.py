from django.views.generic import View

from main.models import User, UserAction, Team, TeamAction
from main.utils import abort, get_score_stage
from main.utils.recommender import record_like_user, record_like_team
from util.decorator.auth import app_auth


class LikedEntity(View):
    """与当前用户点赞行为相关的View"""

    @app_auth
    def get(self, request, entity):
        """判断当前用户是否对某个对象点过赞"""

        if entity.likers.filter(liker=request.user).exists():
            abort(200)
        abort(404, '未点过赞')

    @app_auth
    def post(self, request, entity):
        """对某个对象点赞"""

        if not entity.likers.filter(liker=request.user).exists():
            entity.likers.create(liker=request.user)
            # 积分
            request.user.score += get_score_stage(1)
            request.user.score_records.create(
                score=get_score_stage(1), type="活跃度", description="给他人点赞")
            # 特征模型
            if isinstance(entity, User):
                record_like_user(request.user, entity)
            elif isinstance(entity, UserAction):
                record_like_user(request.user, entity.entity)
            elif isinstance(entity, Team):
                record_like_team(request.user, entity)
            elif isinstance(entity, TeamAction):
                record_like_user(request.user, entity.entity)
            else:
                pass

            request.user.save()
        abort(200)

    @app_auth
    def delete(self, request, entity):
        """对某个对象取消点赞"""

        # 积分
        request.user.score -= get_score_stage(1)
        request.user.score_records.create(
            score=-get_score_stage(1), type="活跃度", description="取消给他人点赞")
        request.user.save()
        entity.likers.filter(liker=request.user).delete()
        abort(200)