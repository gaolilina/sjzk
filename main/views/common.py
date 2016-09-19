from django import forms
from django.http import JsonResponse
from django.views.generic import View

from ..models import User, Team, UserComment as UserCommentModel, \
    TeamComment as TeamCommentModel, \
    Activity, ActivityComment as ActivityCommentModel
from ..utils import abort
from ..utils.decorators import *


__all__ = ['UserActionList', 'TeamActionList', 'UserCommentList',
           'TeamCommentList', 'UserComment', 'TeamComment', 'UserFollowerList',
           'TeamFollowerList', 'UserFollower', 'TeamFollower',
           'UserLikerList', 'TeamLikerList', 'UserLiker', 'TeamLiker',
           'UserVisitorList', 'TeamVisitorList',
           'ActivityCommentList', 'ActivityComment']


class ActionList(View):
    @validate_args({
        'offset': forms.IntegerField(required=False, min_value=0),
    })
    def get(self, request, entity, offset=0, limit=10):
        """获取对象的动态列表

        :param offset: 偏移量
        :param limit: 数量上限
        :return:
            count: 动态总数（包括标记为disabled的内容）
            last_time_created: 最近更新时间
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
class UserActionList(ActionList):
    @fetch_object(User.enabled, 'user')
    @require_token
    def get(self, request, user=None):
        user = user or request.user
        return super().get(request, user)


# noinspection PyMethodOverriding
class TeamActionList(ActionList):
    @fetch_object(Team.enabled, 'team')
    @require_token
    def get(self, request, team):
        return super(TeamActionList, self).get(request, team)


class CommentList(View):
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
class UserCommentList(CommentList):
    @fetch_object(User.enabled, 'user')
    @require_token
    def get(self, request, user=None):
        user = user or request.user
        return super().get(request, user)

    @fetch_object(User.enabled, 'user')
    @require_token
    def post(self, request, user=None):
        user = user or request.user
        return super().post(request, user)


# noinspection PyMethodOverriding
class TeamCommentList(CommentList):
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


# noinspection PyMethodOverriding
class ActivityCommentList(CommentList):
    @fetch_object(Activity.enabled, 'activity')
    @require_token
    def get(self, request, activity):
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
        return super().get(request, activity)

    @fetch_object(Activity.enabled, 'activity')
    @require_token
    def post(self, request, activity):
        """当前用户对活动进行评论"""

        return super().post(request, activity)


class UserComment(View):
    @fetch_object(UserCommentModel.objects, 'comment')
    @require_token
    def delete(self, request, comment):
        """删除用户评论"""

        if comment.entity == request.user or comment.author == request.user:
            comment.delete()
            abort(200)
        abort(403)


class TeamComment(View):
    @fetch_object(TeamCommentModel.objects, 'comment')
    @require_token
    def delete(self, request, comment):
        """删除团队评论"""

        if comment.entity.owner == request.user \
                or comment.author == request.user:
            comment.delete()
            abort(200)
        abort(403)


class ActivityComment(View):
    @fetch_object(ActivityCommentModel.objects, 'comment')
    @require_token
    def delete(self, request, comment):
        """删除活动评论"""

        if comment.author == request.user:
            comment.delete()
            abort(200)
        abort(403)


class FollowerList(View):
    get_dict = {
        'offset': forms.IntegerField(required=False, min_value=0),
        'limit': forms.IntegerField(required=False, min_value=0),
        'order': forms.IntegerField(required=False, min_value=0, max_value=3),
    }
    ORDERS = ('time_created', '-time_created',
              'follower__name', '-follower__name')

    @validate_args(get_dict)
    def get(self, request, obj, offset=0, limit=10, order=1):
        """获取粉丝列表

        :param offset: 偏移量
        :param order: 排序方式
            0: 关注时间升序
            1: 关注时间降序（默认值）
            2: 昵称升序
            3: 昵称降序
        :return:
            count: 粉丝总数
            list: 粉丝列表
                id: 用户ID
                username: 用户名
                name: 用户昵称
                time_created: 关注时间
        """
        c = obj.followers.count()
        qs = obj.followers.order_by(self.ORDERS[order])[offset:offset + limit]
        l = [{'id': r.follower.id,
              'username': r.follower.username,
              'name': r.follower.name,
              'time_created': r.time_created} for r in qs]
        return JsonResponse({'count': c, 'list': l})


# noinspection PyMethodOverriding
class UserFollowerList(FollowerList):
    @fetch_object(User.enabled, 'user')
    @require_token
    def get(self, request, user=None):
        user = user or request.user
        return super().get(request, user)


# noinspection PyMethodOverriding
class TeamFollowerList(FollowerList):
    @fetch_object(Team.enabled, 'team')
    @require_token
    def get(self, request, team):
        return super().get(request, team)


class Follower(View):
    @fetch_object(User.enabled, 'other_user')
    def get(self, request, entity, other_user):
        """检查某实体的粉丝是否包含other_user"""

        if entity.followers.filter(follower=other_user).exists():
            abort(200)
        abort(404)


# noinspection PyMethodOverriding
class UserFollower(Follower):
    @fetch_object(User.enabled, 'user')
    @require_token
    def get(self, request, user=None):
        user = user or request.user
        return super().get(request, user)


# noinspection PyMethodOverriding
class TeamFollower(Follower):
    @fetch_object(Team.enabled, 'team')
    @require_token
    def get(self, request, team):
        return super().get(request, team)


class LikerList(View):
    ORDERS = (
        'time_created', '-time_created',
        'follower__name', '-follower__name',
    )

    @validate_args({
        'offset': forms.IntegerField(required=False, min_value=0),
        'order': forms.IntegerField(required=False, min_value=0, max_value=3),
    })
    def get(self, request, obj, offset=0, limit=10, order=1):
        """获取对象的点赞者列表

        :param offset: 偏移量
        :param order: 排序方式
            0: 点赞时间升序
            1: 点赞时间降序（默认值）
            2: 昵称升序
            3: 昵称降序
        :return:
            count: 总点赞量
            list: 点赞者列表
                id: 用户ID
                username: 用户名
                name: 用户昵称
                icon_url: 用户头像URL
                time_created: 点赞时间
        """
        i, j, k = offset, offset + limit, self.ORDERS[order]
        c = obj.likers.count()
        qs = obj.likers.order_by(k)[i:j]
        l = [{'id': r.liker.id,
              'username': r.liker.username,
              'name': r.liker.name,
              'time_created': r.time_created} for r in qs]
        return JsonResponse({'count': c, 'list': l})


# noinspection PyMethodOverriding
class UserLikerList(LikerList):
    @require_token
    @fetch_object(User.enabled, 'user')
    def get(self, request, user=None):
        user = user or request.user
        return super().get(request, user)


# noinspection PyMethodOverriding
class TeamLikerList(LikerList):
    @require_token
    @fetch_object(Team.enabled, 'team')
    def get(self, request, team):
        return super().get(request, team)


class Liker(View):
    def get(self, request, entity, other_user):
        """判断other_user是否对某个实体点过赞"""

        if entity.likers.filter(liker=other_user).exists():
            abort(200)
        abort(404)


class UserLiker(Liker):
    @fetch_object(User.enabled, 'user')
    @fetch_object(User.enabled, 'other_user')
    @require_token
    def get(self, request, other_user, user=None):
        user = user or request.user
        return super(UserLiker, self).get(request, user, other_user)


class TeamLiker(Liker):
    @fetch_object(Team.enabled, 'team')
    @fetch_object(User.enabled, 'other_user')
    @require_token
    def get(self, request, team, other_user):
        return super(TeamLiker, self).get(request, team, other_user)


class VisitorList(View):
    @validate_args({'offset': forms.IntegerField(required=False, min_value=0)})
    def get(self, request, entity, offset=0, limit=10):
        """获取对象的访客列表

        :param offset: 偏移量
        :param limit: 数量上限
        :return:
            count: 一段时间内的访客人数
            list: 访客列表
                id: 用户ID
                username: 用户名
                name: 用户昵称
                time_updated: 来访时间
        """
        c = entity.visitors.count()
        qs = entity.visitors.all()[offset:offset + limit]
        l = [{'id': i.visitor.id,
              'username': i.visitor.username,
              'name': i.visitor.name,
              'update_time': i.time_updated} for i in qs]
        return JsonResponse({'count': c, 'list': l})


# noinspection PyMethodOverriding
class UserVisitorList(VisitorList):
    @require_token
    @fetch_object(User.enabled, 'user')
    def get(self, request, user=None):
        user = user or request.user
        return super().get(request, user)


# noinspection PyMethodOverriding
class TeamVisitorList(VisitorList):
    @require_token
    @fetch_object(Team.enabled, 'team')
    def get(self, request, team):
        return super().get(request, team)
