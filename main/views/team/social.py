from django.views.generic import View

from main.models import Team, TeamComment as TeamCommentModel, User
from main.utils import abort
from main.utils.decorators import require_verification_token
from main.views.common import ActionList, CommentList, FollowerList, Follower, Liker, VisitorList, LikerList
from util.decorator.auth import app_auth
from util.decorator.param import fetch_object


class TeamActionList(ActionList):
    @fetch_object(Team.enabled, 'team')
    @app_auth
    def get(self, request, team):
        return super(TeamActionList, self).get(request, team)


class TeamCommentList(CommentList):
    @fetch_object(Team.enabled, 'team')
    @app_auth
    def get(self, request, team):
        """获取团队的评论信息列表

        :return:
            count: 评论总数
            list: 评论列表
                id: 评论ID
                author_id: 评论者ID
                author_name: 评论者昵称
                icon_url: 头像
                content: 内容
                time_created: 发布时间
        """
        return super().get(request, team)

    @fetch_object(Team.enabled, 'team')
    @require_verification_token
    def post(self, request, team):
        """当前用户对团队进行评论"""

        return super().post(request, team)


class TeamComment(View):
    @fetch_object(TeamCommentModel.objects, 'comment')
    @require_verification_token
    def delete(self, request, comment):
        """删除团队评论"""

        if comment.entity.owner == request.user \
                or comment.author == request.user:
            comment.delete()
            abort(200)
        abort(403, '非法操作')


class TeamFollowerList(FollowerList):
    @fetch_object(Team.enabled, 'team')
    @app_auth
    def get(self, request, team):
        return super().get(request, team)


class TeamFollower(Follower):
    @fetch_object(Team.enabled, 'team')
    @app_auth
    def get(self, request, team):
        return super().get(request, team)


class TeamLiker(Liker):
    @fetch_object(Team.enabled, 'team')
    @fetch_object(User.enabled, 'other_user')
    @app_auth
    def get(self, request, team, other_user):
        return super(TeamLiker, self).get(request, team, other_user)


class TeamVisitorList(VisitorList):
    @app_auth
    @fetch_object(Team.enabled, 'team')
    def get(self, request, team):
        return super().get(request, team)


class TeamLikerList(LikerList):
    @app_auth
    @fetch_object(Team.enabled, 'team')
    def get(self, request, team):
        return super().get(request, team)
