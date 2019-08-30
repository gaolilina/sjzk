from main.models import Competition
from main.utils.decorators import require_verification_token
from main.views.common import CommentList
from util.decorator.auth import app_auth
from util.decorator.param import fetch_object


class CompetitionCommentList(CommentList):
    @fetch_object(Competition.enabled, 'competition')
    @app_auth
    def get(self, request, competition):
        """获取竞赛的评论信息列表

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
        return super().get(request, competition)

    @fetch_object(Competition.enabled, 'competition')
    @require_verification_token
    def post(self, request, competition):
        """当前用户对竞赛进行评论"""

        return super().post(request, competition)