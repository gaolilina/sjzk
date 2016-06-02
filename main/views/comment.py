from django import forms
from django.http import JsonResponse
from django.views.generic import View

from main.decorators import check_object_id, require_token, validate_input
from main.models import User, UserComment as UserCommentModel
from main.models import Team, TeamComment as TeamCommentModel
from main.responses import Http200, Http403


class Comments(View):
    get_dict = {
        'offset': forms.IntegerField(required=False, min_value=0),
        'limit': forms.IntegerField(required=False, min_value=0),
    }

    @validate_input(get_dict)
    def get(self, request, obj=None, offset=0, limit=10):
        """
        获取对象的评论列表

        :param offset: 偏移量
        :param limit: 数量上限
        :return:
            count: 评论总数
            list: 评论列表
                id: 评论ID
                author_id: 评论者ID
                author_name: 评论者昵称
                author_icon_url: 评论者头像URL
                content: 内容
                create_time: 发布时间
        """
        i, j = offset, offset + limit
        qs = obj.comments
        c = qs.count()
        l = [{'id': r.id,
              'author_id': r.author.id,
              'author_name': r.author.name,
              'author_icon_url': r.author.icon_url,
              'content': r.content,
              'create_time': r.create_time} for r in qs.all()[i:j]]
        return JsonResponse({'count': c, 'list': l})

    post_dict = {'content': forms.CharField(max_length=100)}

    @validate_input(post_dict)
    def post(self, request, obj, content):
        """
        评论某个对象

        """
        obj.comments.create(author=request.user, content=content)
        return Http200()


# noinspection PyMethodOverriding
class UserComments(Comments):
    @check_object_id(User.enabled, 'user')
    @require_token
    def get(self, request, user=None):
        user = user or request.user
        return super(UserComments, self).get(request, user)

    @check_object_id(User.enabled, 'user')
    @require_token
    def post(self, request, user=None):
        user = user or request.user
        return super(UserComments, self).post(request, user)


class UserComment(View):
    @check_object_id(UserCommentModel.enabled, 'comment')
    @require_token
    def delete(self, request, comment):
        """
        删除针对自己的某条评论

        """
        if comment.object == request.user:
            comment.delete()
            return Http200()
        else:
            return Http403('cannot delete other\'s item')


# noinspection PyMethodOverriding
class TeamComments(Comments):
    @check_object_id(Team.enabled, 'team')
    @require_token
    def get(self, request, team):
        """
        获取团队的评论信息列表

        :param team_id: 团队ID
        :param offset: 偏移量
        :param limit: 数量上限
        :return:
            count: 评论总数
            list: 评论列表
                id: 评论ID
                author_id: 评论者ID
                author_name: 评论者昵称
                author_icon_url: 评论者头像URL
                content: 内容
                create_time: 发布时间
        """
        return super(TeamComments, self).get(request, team)

    @check_object_id(Team.enabled, 'team')
    @require_token
    def post(self, request, team):
        """
        当前用户对团队进行评论

        :param team_id: 团队ID
        :param content: 评论内容
        """
        return super(TeamComments, self).post(request, team)


class TeamComment(View):
    @check_object_id(Team.enabled, 'team')
    @check_object_id(TeamCommentModel.enabled, 'comment')
    @require_token
    def delete(self, request, team, comment):
        """
        删除针对团队的某条评论

        """
        if request.user != team.owner:
            return Http403('recent user has not authority')
        if comment.object == team:
            comment.delete()
            return Http200()
        else:
            return Http403('cannot delete other\'s item')