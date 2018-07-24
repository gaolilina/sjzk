from django import forms
from django.db.models import Q
from django.http import JsonResponse
from django.views.generic import View

from ..models import User, Team, Lab, TeamNeed, UserComment as UserCommentModel, \
    TeamComment as TeamCommentModel, LabComment as LabCommentModel, \
    Activity, ActivityComment as ActivityCommentModel, \
    Competition, CompetitionComment as CompetitionCommentModel, \
    UserAction, TeamAction, LabAction, SystemAction, \
    UserActionFavorer, TeamActionFavorer, LabActionFavorer, SystemActionFavorer, \
    ActivityFavorer, CompetitionFavorer

from ..utils import abort, action
from ..utils.decorators import *
from ..utils.dfa import check_bad_words


__all__ = ['UserActionList', 'TeamActionList', 'ActionsList',
           'LabActionList',
           'SearchUserActionList', 'SearchTeamActionList',
           'SearchLabActionList',
           'ScreenUserActionList', 'ScreenTeamActionList',
           'ScreenLabActionList',
           'UserActionsList', 'TeamActionsList', 'UserCommentList',
           'LabActionsList', 'LabCommentList', 'LabComment',
           'TeamCommentList', 'UserComment', 'TeamComment', 'UserFollowerList',
           'TeamFollowerList', 'UserFollower', 'TeamFollower',
           'LabFollowerList', 'LabFollower',
           'UserLikerList', 'TeamLikerList', 'UserLiker', 'TeamLiker',
           'LabLikerList', 'LabLiker',
           'UserVisitorList', 'TeamVisitorList', 'CompetitionFollowerList',
           'LabVisitorList',
           'ActivityCommentList', 'ActivityComment', 'ActivityFollowerList',
           'CompetitionCommentList', 'CompetitionComment',
           'UserActionCommentList', 'TeamActionCommentList',
           'LabActionCommentList',
           'TeamNeedFollowerList', 'SearchSystemActionList', 'SystemActionsList'
           , 'SystemActionCommentList', 'SystemActionComment',
           'FavoredUserActionList', 'FavoredTeamActionList', 'FavoredSystemActionList',
           'FavoredLabActionList',
           'FavoredActivityList', 'FavoredCompetitionList']


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


class LabActionsList(View):
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
        c = LabAction.objects.count()
        records = (i for i in LabAction.objects.all()[offset:offset + limit])
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


class FolloweLabActionList(View):
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

        r = LabAction.objects.filter(
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

# noinspection PyMethodOverriding
class LabActionList(ActionList):
    @fetch_object(Lab.enabled, 'lab')
    @require_token
    def get(self, request, lab):
        return super(LabActionList, self).get(request, lab)


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

        r = UserAction.objects.filter(Q(entity__name__icontains=kwargs['name'])
                                      | Q(action__icontains=kwargs['name']))
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
            r = r.filter(Q(entity__name__icontains=name) |
                         Q(action__icontains=name))
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
            # 按动作筛选
            r = r.filter(action__icontains=act)

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

        r = TeamAction.objects.filter(Q(entity__name__icontains=kwargs['name'])
                                      | Q(action__icontains=kwargs['name']))
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
            r = r.filter(Q(entity__name__icontains=name) |
                         Q(action__icontains=name))
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
            # 按动作筛选
            r = r.filter(action__icontains=act)

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


class SearchLabActionList(View):
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

        r = LabAction.objects.filter(Q(entity__name__icontains=kwargs['name'])
                                      | Q(action__icontains=kwargs['name']))
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


class ScreenLabActionList(View):
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

        r = Labction.objects
        name = kwargs.pop('name', '')
        if name:
            # 按用户昵称或动态名检索
            r = r.filter(Q(entity__name__icontains=name) |
                         Q(action__icontains=name))
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
            # 按动作筛选
            r = r.filter(action__icontains=act)

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

class SearchSystemActionList(View):
    @validate_args({
        'offset': forms.IntegerField(required=False, min_value=0),
        'limit': forms.IntegerField(required=False, min_value=0),
        'name': forms.CharField(max_length=20),
    })
    def get(self, request, offset=0, limit=10, **kwargs):
        """搜索系统动态名相关的动态列表

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

        r = SystemAction.objects.filter(action__icontains=kwargs['name'])
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

        if check_bad_words(content):
            abort(403, '含有非法词汇')
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
class LabCommentList(CommentList):
    @fetch_object(Lab.enabled, 'lab')
    @require_token
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


# noinspection PyMethodOverriding
class LabActionCommentList(CommentList):
    @fetch_object(LabAction.objects, 'action')
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

    @fetch_object(LabAction.objects, 'action')
    @require_verification_token
    def post(self, request, action):
        """当前用户对团队动态进行评论"""

        return super().post(request, action)

# noinspection PyMethodOverriding
class SystemActionCommentList(CommentList):
    @fetch_object(SystemAction.objects, 'action')
    @require_token
    def get(self, request, action):
        """获取系统动态的评论信息列表

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

    @fetch_object(SystemAction.objects, 'action')
    @require_verification_token
    def post(self, request, action):
        """当前用户对系统动态进行评论"""

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


# noinspection PyMethodOverriding
class LabFollowerList(FollowerList):
    @fetch_object(Lab.enabled, 'lab')
    @require_token
    def get(self, request, lab):
        return super().get(request, lab)

# noinspection PyMethodOverriding
class TeamNeedFollowerList(FollowerList):
    @fetch_object(TeamNeed.objects, 'need')
    @require_token
    def get(self, request, need):
        return super().get(request, need)


# noinspection PyMethodOverriding
class ActivityFollowerList(FollowerList):
    @fetch_object(Activity.enabled, 'activity')
    @require_token
    def get(self, request, activity):
        return super().get(request, activity)


# noinspection PyMethodOverriding
class CompetitionFollowerList(FollowerList):
    @fetch_object(Competition, 'competition')
    @require_token
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


# noinspection PyMethodOverriding
class LabFollower(Follower):
    @fetch_object(Lab.enabled, 'lab')
    @require_token
    def get(self, request, lab):
        return super().get(request, lab)

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


# noinspection PyMethodOverriding
class LabLikerList(LikerList):
    @require_token
    @fetch_object(Lab.enabled, 'lab')
    def get(self, request, lab):
        return super().get(request, lab)

class Liker(View):
    def get(self, request, entity, other_user):
        """判断other_user是否对某个实体点过赞"""

        if entity.likers.filter(liker=other_user).exists():
            abort(200)
        abort(404, '未点赞')


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


class LabLiker(Liker):
    @fetch_object(Lab.enabled, 'lab')
    @fetch_object(User.enabled, 'other_user')
    @require_token
    def get(self, request, lab, other_user):
        return super(LabLiker, self).get(request, lab, other_user)

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


# noinspection PyMethodOverriding
class LabVisitorList(VisitorList):
    @require_token
    @fetch_object(Lab.enabled, 'lab')
    def get(self, request, lab):
        return super().get(request, lab)

class FavoredActionList(View):
    get_dict = {
        'offset': forms.IntegerField(required=False, min_value=0),
        'limit': forms.IntegerField(required=False, min_value=0),
        'order': forms.IntegerField(required=False, min_value=0, max_value=1),
    }
    ORDERS = ('time_created', '-time_created')

    @validate_args(get_dict)
    def get(self, request, obj, offset=0, limit=10, order=1):
        """获取动态收藏列表

        :param offset: 偏移量
        :param order: 排序方式
            0: 收藏时间升序
            1: 收藏时间降序（默认值）
        :return:
            count: 收藏总数
            list: 收藏列表
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
        c = obj.count()
        qs = obj.order_by(self.ORDERS[order])[offset:offset + limit]
        
        l = [{'id': i.favored.entity.id,
              'action_id': i.favored.id,
              'name': i.favored.entity.name,
              'icon': i.favored.entity.icon,
              'action': i.favored.action,
              'object_type': i.favored.object_type,
              'object_id': i.favored.object_id,
              'object_name': action.get_object_name(i.favored),
              'icon_url': action.get_object_icon(i.favored),
              'related_object_type': i.favored.related_object_type,
              'related_object_id': i.favored.related_object_id,
              'related_object_name': action.get_related_object_name(i.favored),
              'liker_count': i.favored.likers.count(),
              'comment_count': i.favored.comments.count(),
              'time_created': i.favored.time_created,
              } for i in qs]
        return JsonResponse({'count': c, 'list': l})

# noinspection PyMethodOverriding
class FavoredUserActionList(FavoredActionList):
    @require_token
    def get(self, request):
        return super().get(request, request.user.favored_user_actions)

# noinspection PyMethodOverriding
class FavoredTeamActionList(FavoredActionList):
    @require_token
    def get(self, request):
        return super().get(request, request.user.favored_team_actions)

# noinspection PyMethodOverriding
class FavoredLabActionList(FavoredActionList):
    @require_token
    def get(self, request):
        return super().get(request, request.user.favored_lab_actions)

# noinspection PyMethodOverriding
class FavoredSystemActionList(FavoredActionList):
    @require_token
    def get(self, request):
        return super().get(request, request.user.favored_system_actions)

class FavoredActivityList(View):
    get_dict = {
        'offset': forms.IntegerField(required=False, min_value=0),
        'limit': forms.IntegerField(required=False, min_value=0),
        'order': forms.IntegerField(required=False, min_value=0, max_value=1),
    }
    ORDERS = ('time_created', '-time_created')

    @require_token
    @validate_args(get_dict)
    def get(self, request, offset=0, limit=10, order=1):
        """获取活动收藏列表

        :param offset: 偏移量
        :param order: 排序方式
            0: 收藏时间升序
            1: 收藏时间降序（默认值）
        :return:
            count: 收藏总数
            list: 收藏列表
                id: 活动ID
                name: 活动名
                liker_count: 点赞数
                status: 竞赛当前阶段
                time_started: 开始时间
                time_ended: 结束时间
                deadline: 截止时间
                user_participator_count: 已报名人数
                time_created: 创建时间
                province:
        """
        c = request.user.favored_activities.count()
        qs = request.user.favored_activities.order_by(self.ORDERS[order])[offset:offset + limit]
        
        l = [{'id': a.favored.id,
              'name': a.favored.name,
              'liker_count': a.favored.likers.count(),
              'status': a.favored.status,
              'time_started': a.favored.time_started,
              'time_ended': a.favored.time_ended,
              'deadline': a.favored.deadline,
              'user_participator_count': a.favored.user_participators.count(),
              'time_created': a.favored.time_created,
              'province': a.favored.province} for a in qs]
        return JsonResponse({'count': c, 'list': l})


class FavoredCompetitionList(View):
    get_dict = {
        'offset': forms.IntegerField(required=False, min_value=0),
        'limit': forms.IntegerField(required=False, min_value=0),
        'order': forms.IntegerField(required=False, min_value=0, max_value=1),
    }
    ORDERS = ('time_created', '-time_created')

    @require_token
    @validate_args(get_dict)
    def get(self, request, offset=0, limit=10, order=1):
        """获取竞赛收藏列表

        :param offset: 偏移量
        :param order: 排序方式
            0: 收藏时间升序
            1: 收藏时间降序（默认值）
        :return:
            count: 收藏总数
            list: 收藏列表
                id: 竞赛ID
                name: 竞赛名
                liker_count: 点赞数
                status: 竞赛当前阶段
                time_started: 开始时间
                time_ended: 结束时间
                deadline: 截止时间
                team_participator_count: 已报名人数
                time_created: 创建时间
                province:
        """
        c = request.user.favored_competitions.count()
        qs = request.user.favored_competitions.order_by(self.ORDERS[order])[offset:offset + limit]
        
        l = [{'id': a.favored.id,
              'name': a.favored.name,
              'liker_count': a.favored.likers.count(),
              'status': a.favored.status,
              'time_started': a.favored.time_started,
              'time_ended': a.favored.time_ended,
              'deadline': a.favored.deadline,
              'team_participator_count': a.favored.team_participators.count(),
              'time_created': a.favored.time_created,
              'province': a.favored.province} for a in qs]
        return JsonResponse({'count': c, 'list': l})