from django import forms
from django.http import JsonResponse
from django.views.generic import View

from main.views.follow import SomethingFollower
from main.views.like import SomethingLikers, Liker
from util.decorator.auth import app_auth
from util.decorator.param import validate_args, fetch_object
from ..models import User, Lab, LabComment as LabCommentModel, \
    Activity, ActivityComment as ActivityCommentModel, \
    Competition, CompetitionComment as CompetitionCommentModel, \
    SystemAction, \
    LabAchievementLiker, \
    Achievement, LabAchievement
from main.models.need import TeamNeed
from ..utils import abort, action
from ..utils.decorators import *
from ..utils.dfa import check_bad_words


# __all__ = ['UserActionList', 'TeamActionList', 'ActionsList',
#            'LabActionList',
#            'SearchUserActionList', 'SearchTeamActionList',
#            'SearchLabActionList',
#            'ScreenUserActionList', 'ScreenTeamActionList',
#            'ScreenLabActionList',
#            'UserActionsList', 'TeamActionsList', 'UserCommentList',
#            'LabActionsList', 'LabCommentList', 'LabComment',
#            'TeamCommentList', 'UserComment', 'TeamComment', 'UserFollowerList',
#            'TeamFollowerList', 'UserFollower', 'TeamFollower',
#            'LabFollowerList', 'LabFollower',
#            'UserLikerList', 'TeamLikerList', 'UserLiker', 'TeamLiker',
#            'LabLikerList', 'LabLiker',
#            'UserVisitorList', 'TeamVisitorList', 'CompetitionFollowerList',
#            'LabVisitorList',
#            'ActivityCommentList', 'ActivityComment', 'ActivityFollowerList',
#            'CompetitionCommentList', 'CompetitionComment',
#            'UserActionCommentList', 'TeamActionCommentList',
#            'LabActionCommentList',
#            'TeamNeedFollowerList', 'SearchSystemActionList', 'SystemActionsList'
#            , 'SystemActionCommentList', 'SystemActionComment',
#            'FavoredUserActionList', 'FavoredTeamActionList', 'FavoredSystemActionList',
#            'FavoredLabActionList',
#            'FavoredActivityList', 'FavoredCompetitionList']


class ActionList(View):
    @validate_args({
        'offset': forms.IntegerField(required=False, min_value=0),
        'limit': forms.IntegerField(required=False, min_value=0),
    })
    def get(self, request, entity=None, offset=0, limit=10):
        """获取对象的动态列表

        :param offset: 偏移量
        :param limit: 数量上限
        :return:
            count: 动态总数（包括标记为disabled的内容）
            last_time_created: 最近更新时间
            list: 动态列表
                action_id: 动态id
                id: 主语的id
                name: 主语的名称
                icon: 主语的头像
                action: 相关动作
                object_type: 相关对象的类型
                object_id: 相关对象的ID
                object_name: 相关对象名称
                icon_url: 头像
                related_object_type: 额外相关对象的类型
                related_object_id: 额外相关对象的ID
                related_object_name: 额外相关对象的名称
                liker_count: 点赞数
                comment_count: 评论数
                time_created: 创建时间
        """

        # 获取与对象相关的动态
        c = entity.actions.count()
        records = (i for i in entity.actions.all()[offset:offset + limit])
        l = [{'id': i.entity.id,
              'action_id': i.id,
              'name': i.entity.name,
              'icon': i.entity.icon,
              'action': i.action,
              'object_type': i.object_type,
              'object_id': i.object_id,
              'object_name': action.get_object_name(i),
              'icon_url': action.get_object_icon(i),
              'related_object_type': i.related_object_type,
              'related_object_id': i.related_object_id,
              'related_object_name': action.get_related_object_name(i),
              'liker_count': i.likers.count(),
              'comment_count': i.comments.count(),
              'time_created': i.time_created,
              } for i in records]
        return JsonResponse({'count': c, 'list': l})


class SystemActionsList(View):
    @validate_args({
        'offset': forms.IntegerField(required=False, min_value=0),
        'limit': forms.IntegerField(required=False, min_value=0),
    })
    def get(self, request, entity=None, offset=0, limit=10):
        """获取系统的动态列表

        :param offset: 偏移量
        :param limit: 数量上限
        :return:
            count: 动态总数（包括标记为disabled的内容）
            last_time_created: 最近更新时间
            list: 动态列表
                id: 主语的id
                action_id: 动态id
                name: 主语的名称
                icon: 主语的头像
                action: 相关动作
                object_type: 相关对象的类型
                object_id: 相关对象的ID
                object_name: 相关对象名称
                icon_url: 头像
                related_object_type: 额外相关对象的类型
                related_object_id: 额外相关对象的ID
                related_object_name: 额外相关对象的名称
                liker_count: 点赞数
                comment_count: 评论数
                time_created: 创建时间
        """

        # 获取主语是系统的动态
        c = SystemAction.objects.count()
        records = (i for i in SystemAction.objects.all()[offset:offset + limit])
        l = [{'id': i.entity.id,
              'action_id': i.id,
              'name': i.entity.name,
              'icon': i.entity.icon,
              'action': i.action,
              'object_type': i.object_type,
              'object_id': i.object_id,
              'object_name': action.get_object_name(i),
              'icon_url': action.get_object_icon(i),
              'related_object_type': i.related_object_type,
              'related_object_id': i.related_object_id,
              'related_object_name': action.get_related_object_name(i),
              'liker_count': i.likers.count(),
              'comment_count': i.comments.count(),
              'time_created': i.time_created,
              } for i in records]
        return JsonResponse({'count': c, 'list': l})


# noinspection PyMethodOverriding
class LabActionList(ActionList):
    @fetch_object(Lab.enabled, 'lab')
    @app_auth
    def get(self, request, lab):
        return super(LabActionList, self).get(request, lab)


# noinspection PyMethodOverriding
class ActionsList(ActionList):
    @app_auth
    def get(self, request):
        return super(ActionsList, self).get(request)


class CommentList(View):
    @validate_args({
        'offset': forms.IntegerField(required=False, min_value=0),
        'limit': forms.IntegerField(required=False, min_value=0),
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
              'icon_url': r.author.icon,
              'content': r.content,
              'time_created': r.time_created
              } for r in qs.all()[offset:offset + limit]]
        return JsonResponse({'count': c, 'list': l})

    @validate_args({'content': forms.CharField(max_length=100)})
    def post(self, request, obj, content):
        """评论某个对象"""

        if check_bad_words(content):
            abort(403, '含有非法词汇')
        obj.comments.create(author=request.user, content=content)
        request.user.score += 10
        request.user.save()
        abort(200)


# noinspection PyMethodOverriding


# noinspection PyMethodOverriding


# noinspection PyMethodOverriding
class LabCommentList(CommentList):
    @fetch_object(Lab.enabled, 'lab')
    @app_auth
    def get(self, request, lab):
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
        return super().get(request, lab)

    @fetch_object(Lab.enabled, 'lab')
    @require_verification_token
    def post(self, request, team):
        """当前用户对团队进行评论"""

        return super().post(request, lab)


# noinspection PyMethodOverriding
class ActivityCommentList(CommentList):
    @fetch_object(Activity.enabled, 'activity')
    @app_auth
    def get(self, request, activity):
        """获取活动的评论信息列表

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
        return super().get(request, activity)

    @fetch_object(Activity.enabled, 'activity')
    @require_verification_token
    def post(self, request, activity):
        """当前用户对活动进行评论"""

        return super().post(request, activity)


class LabComment(View):
    @fetch_object(LabCommentModel.objects, 'comment')
    @require_verification_token
    def delete(self, request, comment):
        """删除团队评论"""

        if comment.entity.owner == request.user \
                or comment.author == request.user:
            comment.delete()
            abort(200)
        abort(403, '非法操作')


class ActivityComment(View):
    @fetch_object(ActivityCommentModel.objects, 'comment')
    @require_verification_token
    def delete(self, request, comment):
        """删除活动评论"""

        if comment.author == request.user:
            comment.delete()
            abort(200)
        abort(403, '非法操作')


class CompetitionComment(View):
    @fetch_object(CompetitionCommentModel.objects, 'comment')
    @require_verification_token
    def delete(self, request, comment):
        """删除竞赛评论"""

        if comment.author == request.user:
            comment.delete()
            abort(200)
        abort(403, '非法操作')


# noinspection PyMethodOverriding


# noinspection PyMethodOverriding


# noinspection PyMethodOverriding
class LabFollowerList(SomethingFollower):
    @fetch_object(Lab.enabled, 'lab')
    @app_auth
    def get(self, request, lab):
        return super().get(request, lab)


# noinspection PyMethodOverriding
class TeamNeedFollowerList(SomethingFollower):
    @fetch_object(TeamNeed.objects, 'need')
    @app_auth
    def get(self, request, need):
        return super().get(request, need)


# noinspection PyMethodOverriding
class ActivityFollowerList(SomethingFollower):
    @fetch_object(Activity.enabled, 'activity')
    @app_auth
    def get(self, request, activity):
        return super().get(request, activity)


# noinspection PyMethodOverriding
class CompetitionFollowerList(SomethingFollower):
    @fetch_object(Competition, 'competition')
    @app_auth
    def get(self, request, competition):
        return super().get(request, competition)


class Follower(View):
    @fetch_object(User.enabled, 'other_user')
    def get(self, request, entity, other_user):
        """检查某实体的粉丝是否包含other_user"""

        if entity.followers.filter(follower=other_user).exists():
            abort(200)
        abort(404, '对方不是你的粉丝')


# noinspection PyMethodOverriding
class UserFollower(Follower):
    @fetch_object(User.enabled, 'user')
    @app_auth
    def get(self, request, user=None):
        user = user or request.user
        return super().get(request, user)


# noinspection PyMethodOverriding


# noinspection PyMethodOverriding
class LabFollower(Follower):
    @fetch_object(Lab.enabled, 'lab')
    @app_auth
    def get(self, request, lab):
        return super().get(request, lab)


# noinspection PyMethodOverriding


# noinspection PyMethodOverriding


# noinspection PyMethodOverriding
class LabLikerList(SomethingLikers):
    @app_auth
    @fetch_object(Lab.enabled, 'lab')
    def get(self, request, lab):
        return super().get(request, lab)


# noinspection PyMethodOverriding
class LabAchievementLikerList(SomethingLikers):
    @app_auth
    @fetch_object(LabAchievement.objects, 'achievement')
    def get(self, request, achievement):
        return super().get(request, achievement)


class LabLiker(Liker):
    @fetch_object(Lab.enabled, 'lab')
    @fetch_object(User.enabled, 'other_user')
    @app_auth
    def get(self, request, lab, other_user):
        return super(LabLiker, self).get(request, lab, other_user)


class UserAchievementLiker(Liker):
    @fetch_object(Achievement.objects, 'achievement')
    @fetch_object(User.enabled, 'other_user')
    @app_auth
    def get(self, request, achievement, other_user):
        return super(UserAchievementLiker, self).get(request, achievement, other_user)


class LabAchievementLiker(Liker):
    @fetch_object(LabAchievement.objects, 'achievement')
    @fetch_object(User.enabled, 'other_user')
    @app_auth
    def get(self, request, achievement, other_user):
        return super(LabAchievementLiker, self).get(request, achievement, other_user)


class VisitorList(View):
    @validate_args({
        'offset': forms.IntegerField(required=False, min_value=0),
        'limit': forms.IntegerField(required=False, min_value=0),
    })
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
                icon_url: 头像
                time_updated: 来访时间
        """
        c = entity.visitors.count()
        qs = entity.visitors.all()[offset:offset + limit]
        l = [{'id': i.visitor.id,
              'username': i.visitor.username,
              'name': i.visitor.name,
              'icon_url': i.visitor.icon,
              'update_time': i.time_updated} for i in qs]
        return JsonResponse({'count': c, 'list': l})


# noinspection PyMethodOverriding
class UserVisitorList(VisitorList):
    @app_auth
    @fetch_object(User.enabled, 'user')
    def get(self, request, user=None):
        user = user or request.user
        return super().get(request, user)


# noinspection PyMethodOverriding


# noinspection PyMethodOverriding
class LabVisitorList(VisitorList):
    @app_auth
    @fetch_object(Lab.enabled, 'lab')
    def get(self, request, lab):
        return super().get(request, lab)

# noinspection PyMethodOverriding


# noinspection PyMethodOverriding


# noinspection PyMethodOverriding


# noinspection PyMethodOverriding


