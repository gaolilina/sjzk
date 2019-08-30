from django.views.generic import View

from main.models import User, UserAction, UserComment as UserCommentModel
from main.utils import abort
from main.utils.decorators import require_verification_token
from main.views.common import CommentList
from util.decorator.auth import app_auth
from util.decorator.param import fetch_object


class UserCommentList(CommentList):
    @fetch_object(User.enabled, 'user')
    @app_auth
    def get(self, request, user=None):
        user = user or request.user
        return super().get(request, user)

    @fetch_object(User.enabled, 'user')
    @require_verification_token
    def post(self, request, user=None):
        user = user or request.user
        return super().post(request, user)


class UserActionCommentList(CommentList):
    @fetch_object(UserAction.objects, 'action')
    @app_auth
    def get(self, request, action):
        """获取用户动态的评论信息列表

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

    @fetch_object(UserAction.objects, 'action')
    @require_verification_token
    def post(self, request, action):
        """当前用户对用户动态进行评论"""

        return super().post(request, action)


class UserComment(View):
    @fetch_object(UserCommentModel.objects, 'comment')
    @require_verification_token
    def delete(self, request, comment):
        """删除用户评论"""

        if comment.entity == request.user or comment.author == request.user:
            comment.delete()
            abort(200)
        abort(403, '非法操作')