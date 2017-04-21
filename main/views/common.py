from django import forms
from django.db.models import Q
from django.http import JsonResponse
from django.views.generic import View

from ..models import User, Team, UserComment as UserCommentModel, \
    TeamComment as TeamCommentModel, \
    Activity, ActivityComment as ActivityCommentModel, \
    Competition, CompetitionComment as CompetitionCommentModel, \
    UserAction, TeamAction

from ..utils import abort, action
from ..utils.decorators import *


__all__ = ['UserActionList', 'TeamActionList', 'ActionsList',
           'SearchUserActionList', 'SearchTeamActionList',
           'ScreenUserActionList', 'ScreenTeamActionList'
           'UserActionsList', 'TeamActionsList', 'UserCommentList',
           'TeamCommentList', 'UserComment', 'TeamComment', 'UserFollowerList',
           'TeamFollowerList', 'UserFollower', 'TeamFollower',
           'UserLikerList', 'TeamLikerList', 'UserLiker', 'TeamLiker',
           'UserVisitorList', 'TeamVisitorList',
           'ActivityCommentList', 'ActivityComment',
           'CompetitionCommentList', 'CompetitionComment',
           'UserActionCommentList', 'TeamActionCommentList']


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


class UserActionsList(View):
    @validate_args({
        'offset': forms.IntegerField(required=False, min_value=0),
        'limit': forms.IntegerField(required=False, min_value=0),
    })
    def get(self, request, entity=None, offset=0, limit=10):
        """获取用户的动态列表

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

        # 获取主语是用户的动态
        c = UserAction.objects.count()
        records = (i for i in UserAction.objects.all()[offset:offset + limit])
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


class TeamActionsList(View):
    @validate_args({
        'offset': forms.IntegerField(required=False, min_value=0),
        'limit': forms.IntegerField(required=False, min_value=0),
    })
    def get(self, request, entity=None, offset=0, limit=10):
        """获取团队的动态列表

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

        # 获取主语是团队的动态
        c = TeamAction.objects.count()
        records = (i for i in TeamAction.objects.all()[offset:offset + limit])
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


class FollowedUserActionList(View):
    @require_token
    @validate_args({
        'offset': forms.IntegerField(required=False, min_value=0),
        'limit': forms.IntegerField(required=False, min_value=0),
    })
    def get(self, request, offset=0, limit=10):
        """获取当前用户所关注的用户的动态列表

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

        r = UserAction.objects.filter(Q(
            entity__followers__follower=request.user))
        c = r.count()
        records = (i for i in r[offset:offset + limit])
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


class FollowedTeamActionList(View):
    @require_token
    @validate_args({
        'offset': forms.IntegerField(required=False, min_value=0),
        'limit': forms.IntegerField(required=False, min_value=0),
    })
    def get(self, request, offset=0, limit=10):
        """获取当前用户所关注的团队的动态列表

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

        r = TeamAction.objects.filter(
            Q(entity__followers__follower=request.user))
        c = r.count()
        records = (i for i in r[offset:offset + limit])
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


class SearchUserActionList(View):
    @validate_args({
        'offset': forms.IntegerField(required=False, min_value=0),
        'limit': forms.IntegerField(required=False, min_value=0),
        'name': forms.CharField(max_length=20),
    })
    def get(self, request, offset=0, limit=10, **kwargs):
        """搜索与用户名或者动态名相关的动态列表

        :param offset: 偏移量
        :param limit: 数量上限
        :param kwargs: 搜索条件
            name: 用户名或动态名包含字段

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

        r = UserAction.objects.filter(Q(entity__name__contains=kwargs['name']) |
                                      Q(action__contains=kwargs['name']))
        c = r.count()
        records = (i for i in r[offset:offset + limit])
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


class ScreenUserActionList(View):
    @validate_args({
        'offset': forms.IntegerField(required=False, min_value=0),
        'limit': forms.IntegerField(required=False, min_value=0),
        'name': forms.CharField(required=False, max_length=20),
        'gender': forms.IntegerField(required=False, min_value=0, max_value=2),
        'province': forms.CharField(required=False, max_length=20),
        'city': forms.CharField(required=False, max_length=20),
        'county': forms.CharField(required=False, max_length=20),
        'role': forms.CharField(required=False, max_length=20),
        'unit1': forms.CharField(required=False, max_length=20),
        'action': forms.CharField(required=False, max_length=20),
    })
    def get(self, request, offset=0, limit=10, **kwargs):
        """筛选与用户名或者动态名相关的动态列表

        :param offset: 偏移量
        :param limit: 数量上限
        :param kwargs: 筛选条件
            name: 用户名或动态名包含字段
            gender: 主体的性别
            province: 主体的省
            city: 主体的市
            county: 主体的区/县
            role: 主体的角色
            unit1: 主体的机构
            action: 动态动作

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

        r = UserAction.objects
        name = kwargs.pop('name', '')
        if name:
            # 按用户昵称或动态名检索
            r = r.filter(Q(entity__name__contains=name) |
                         Q(action__contains=name))
        gender = kwargs.pop('gender', None)
        if gender is not None:
            # 按性别筛选
            r = r.filter(entity__gender=gender)
        province = kwargs.pop('province', '')
        if province:
            # 按省会筛选
            r = r.filter(entity__province=province)
        city = kwargs.pop('city', '')
        if city:
            # 按城市筛选
            r = r.filter(entity__city=city)
        county = kwargs.pop('county', '')
        if county:
            # 按区/县筛选
            r = r.filter(entity__county=county)
        role = kwargs.pop('role', '')
        if role:
            # 按角色筛选
            r = r.filter(entity__role=role)
        unit1 = kwargs.pop('unit1', '')
        if unit1:
            # 按机构筛选
            r = r.filter(entity__unit1=unit1)
        act = kwargs.pop('action', '')
        if act:
            # 按机构筛选
            r = r.filter(action__contains=act)

        r = r.all()
        c = r.count()
        records = (i for i in r[offset:offset + limit])
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


class SearchTeamActionList(View):
    @validate_args({
        'offset': forms.IntegerField(required=False, min_value=0),
        'limit': forms.IntegerField(required=False, min_value=0),
        'name': forms.CharField(max_length=20),
    })
    def get(self, request, offset=0, limit=10, **kwargs):
        """搜索与团队名或者动态名相关的动态列表

        :param offset: 偏移量
        :param limit: 数量上限
        :param kwargs: 搜索条件
            name: 团队或动态名包含字段

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

        r = TeamAction.objects.filter(Q(entity__name__contains=kwargs['name']) |
                                      Q(action__contains=kwargs['name']))
        c = r.count()
        records = (i for i in r[offset:offset + limit])
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


class ScreenTeamActionList(View):
    @validate_args({
        'offset': forms.IntegerField(required=False, min_value=0),
        'limit': forms.IntegerField(required=False, min_value=0),
        'name': forms.CharField(required=False, max_length=20),
        'province': forms.CharField(required=False, max_length=20),
        'city': forms.CharField(required=False, max_length=20),
        'county': forms.CharField(required=False, max_length=20),
        'field': forms.CharField(required=False, max_length=10),
        'action': forms.CharField(required=False, max_length=20),
    })
    def get(self, request, offset=0, limit=10, **kwargs):
        """筛选与团队名或者动态名相关的动态列表

        :param offset: 偏移量
        :param limit: 数量上限
        :param kwargs: 筛选条件
            name: 团队名或动态名包含字段
            province: 主体的省
            city: 主体的市
            county: 主体的区/县
            field: 领域
            action: 动态动作

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

        r = TeamAction.objects
        name = kwargs.pop('name', '')
        if name:
            # 按用户昵称或动态名检索
            r = r.filter(Q(entity__name__contains=name) |
                         Q(action__contains=name))
        province = kwargs.pop('province', '')
        if province:
            # 按省会筛选
            r = r.filter(entity__province=province)
        city = kwargs.pop('city', '')
        if city:
            # 按城市筛选
            r = r.filter(entity__city=city)
        county = kwargs.pop('county', '')
        if county:
            # 按区/县筛选
            r = r.filter(entity__county=county)
        field = kwargs.pop('field', '')
        if field:
            # 按机构筛选
            r = r.filter(entity__field=field)
        act = kwargs.pop('action', '')
        if act:
            # 按机构筛选
            r = r.filter(action__contains=act)

        r = r.all()
        c = r.count()
        records = (i for i in r[offset:offset + limit])
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
class ActionsList(ActionList):
    @require_token
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

        obj.comments.create(author=request.user, content=content)
        request.user.score += 10
        request.user.save()
        abort(200)


# noinspection PyMethodOverriding
class UserCommentList(CommentList):
    @fetch_object(User.enabled, 'user')
    @require_token
    def get(self, request, user=None):
        user = user or request.user
        return super().get(request, user)

    @fetch_object(User.enabled, 'user')
    @require_verification_token
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


# noinspection PyMethodOverriding
class ActivityCommentList(CommentList):
    @fetch_object(Activity.enabled, 'activity')
    @require_token
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


# noinspection PyMethodOverriding
class CompetitionCommentList(CommentList):
    @fetch_object(Competition.enabled, 'competition')
    @require_token
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


# noinspection PyMethodOverriding
class UserActionCommentList(CommentList):
    @fetch_object(UserAction.objects, 'action')
    @require_token
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


# noinspection PyMethodOverriding
class TeamActionCommentList(CommentList):
    @fetch_object(TeamAction.objects, 'action')
    @require_token
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


class UserComment(View):
    @fetch_object(UserCommentModel.objects, 'comment')
    @require_verification_token
    def delete(self, request, comment):
        """删除用户评论"""

        if comment.entity == request.user or comment.author == request.user:
            comment.delete()
            abort(200)
        abort(403)


class TeamComment(View):
    @fetch_object(TeamCommentModel.objects, 'comment')
    @require_verification_token
    def delete(self, request, comment):
        """删除团队评论"""

        if comment.entity.owner == request.user \
                or comment.author == request.user:
            comment.delete()
            abort(200)
        abort(403)


class ActivityComment(View):
    @fetch_object(ActivityCommentModel.objects, 'comment')
    @require_verification_token
    def delete(self, request, comment):
        """删除活动评论"""

        if comment.author == request.user:
            comment.delete()
            abort(200)
        abort(403)


class CompetitionComment(View):
    @fetch_object(CompetitionCommentModel.objects, 'comment')
    @require_verification_token
    def delete(self, request, comment):
        """删除竞赛评论"""

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
                icon_url: 头像
                time_created: 关注时间
        """
        c = obj.followers.count()
        qs = obj.followers.order_by(self.ORDERS[order])[offset:offset + limit]
        l = [{'id': r.follower.id,
              'username': r.follower.username,
              'name': r.follower.name,
              'icon_url': r.follower.icon,
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
        'limit': forms.IntegerField(required=False, min_value=0),
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
              'icon_url': r.liker.icon,
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
