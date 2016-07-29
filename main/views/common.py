from django import forms
from django.http import JsonResponse
from django.views.generic import View

from ..models import User, Team, UserComment as UserCommentModel, \
    TeamComment as TeamCommentModel
from ..utils import abort
from ..utils.decorators import *


class Actions(View):
    @validate_args({
        'offset': forms.IntegerField(required=False, min_value=0),
    })
    def get(self, request, entity, offset=0, limit=10):
        """获取对象的动态列表

        :param offset: 偏移量
        :param limit: 数量上限
        :return:
            count: 动态总数（包括标记为disabled的内容）
            last_create_time: 最近更新时间
            list: 动态列表
                action: 相关动作
                object_type: 相关对象的类型
                object_id: 相关对象的ID
                related_object_type: 额外相关对象的类型
                related_object_id: 额外相关对象的ID
        """
        c = entity.actions.count()
        records = (i for i in entity.actions.all()[offset:offset + limit])
        l = [{'action': i.action,
              'object_type': i.object_type,
              'object_id': i.object_id,
              'object_name': i.object.name,
              'related_object_type': i.related_object_type,
              'related_object_id': i.related_object_id,
              'related_object_name': i.related_object.name,
              } for i in records]
        return JsonResponse({'count': c, 'list': l})


# noinspection PyMethodOverriding
class UserActions(Actions):
    @fetch_object(User, 'user')
    @require_token
    def get(self, request, user=None):
        user = user or request.user
        return super().get(request, user)


# noinspection PyMethodOverriding
class TeamActions(Actions):
    @fetch_object(Team, 'team')
    @require_token
    def get(self, request, team):
        return super(TeamActions, self).get(request, team)


class Comments(View):
    @validate_args({
        'offset': forms.IntegerField(required=False, min_value=0),
    })
    def get(self, request, entity=None, offset=0, limit=10):
        """获取对象的评论列表

        :param offset: 偏移量
        :return:
            count: 评论总数
            list: 评论列表
                id: 评论ID
                author_id: 评论者ID
                author_name: 评论者昵称
                content: 内容
                time_created: 发布时间
        """
        qs = entity.comments
        c = qs.count()
        l = [{'id': r.id,
              'author_id': r.author.id,
              'author_name': r.author.name,
              'content': r.content,
              'time_created': r.time_created
              } for r in qs.all()[offset:offset + limit]]
        return JsonResponse({'count': c, 'list': l})

    @validate_args({'content': forms.CharField(max_length=100)})
    def post(self, request, obj, content):
        """评论某个对象"""

        obj.comments.create(author=request.user, content=content)
        abort(200)


# noinspection PyMethodOverriding
class UserComments(Comments):
    @fetch_object(User, 'user')
    @require_token
    def get(self, request, user=None):
        user = user or request.user
        return super().get(request, user)

    @fetch_object(User, 'user')
    @require_token
    def post(self, request, user=None):
        user = user or request.user
        return super().post(request, user)


class UserComment(View):
    @fetch_object(UserCommentModel, 'comment')
    @require_token
    def delete(self, request, comment):
        """删除用户评论"""

        if comment.entity == request.user or comment.author == request.user:
            comment.delete()
            abort(200)
        abort(403)


# noinspection PyMethodOverriding
class TeamComments(Comments):
    @fetch_object(Team.enabled, 'team')
    @require_token
    def get(self, request, team):
        """获取团队的评论信息列表

        :return:
            count: 评论总数
            list: 评论列表
                id: 评论ID
                author_id: 评论者ID
                author_name: 评论者昵称
                content: 内容
                time_created: 发布时间
        """
        return super().get(request, team)

    @fetch_object(Team.enabled, 'team')
    @require_token
    def post(self, request, team):
        """当前用户对团队进行评论"""

        return super().post(request, team)


class TeamComment(View):
    @fetch_object(TeamCommentModel, 'comment')
    @require_token
    def delete(self, request, team, comment):
        """删除团队评论"""

        if comment.entity.owner == request.user \
                or comment.author == request.user:
            comment.delete()
            abort(200)
        abort(403)
