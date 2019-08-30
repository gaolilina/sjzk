from main.models import TeamAction
from main.utils.decorators import require_verification_token
from main.views.common import CommentList
from util.decorator.auth import app_auth
from util.decorator.param import fetch_object


class TeamActionCommentList(CommentList):
    @fetch_object(TeamAction.objects, 'action')
    @app_auth
    def get(self, request, action):
        """获取团队动态的评论信息列表

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
        return super().get(request, action)

    @fetch_object(TeamAction.objects, 'action')
    @require_verification_token
    def post(self, request, action):
        """当前用户对团队动态进行评论"""

        return super().post(request, action)