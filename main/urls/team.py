from django.conf.urls import url

from ..views.team import *
from ..views.common import TeamActionList, TeamCommentList, TeamComment, \
    TeamFollowerList, TeamFollower, TeamLikerList, TeamLiker, \
    TeamVisitorList


urls = [
    # 基本
    url(r'^$', List.as_view(), name='list'),
    url(r'^(?P<team_id>[0-9]+)/profile/$', Profile.as_view(), name='profile'),
    url(r'^(?P<team_id>[0-9]+)/icon/$', Icon.as_view(), name='icon'),
    # 成员
    url(r'^(?P<team_id>[0-9]+)/members/$', MemberList.as_view(),
        name='member_list'),
    url(r'^(?P<team_id>[0-9]+)/members/(?P<user_id>[0-9]+)/$', Member.as_view(),
        name='member'),
    url(r'^(?P<team_id>[0-9]+)/member_requests/$',
        MemberRequestList.as_view(), name='member_requests'),
    url(r'^(?P<team_id>[0-9]+)/member_requests/(?P<user_id>[0-9]+)/$',
        MemberRequest.as_view(), name='member_request'),
    url(r'^(?P<team_id>[0-9]+)/invitations/(?P<user_id>[0-9]+)/$',
        Invitation.as_view(), name='invitation'),
    # 动态
    url(r'^(?P<team_id>[0-9]+)/actions/$', TeamActionList.as_view(),
        name='actions'),
    # 成果
    url(r'^achievements/$', AllAchievementList.as_view(),
        name='all_achievements'),
    url(r'^achievement/(?P<achievement_id>[0-9]+)$',
        AllAchievement.as_view(), name='achievement'),
    url(r'^(?P<team_id>[0-9]+)/achievements/$', AchievementList.as_view(),
        name='achievements'),
    # 点赞
    url(r'^(?P<team_id>[0-9]+)/likers/$', TeamLikerList.as_view(),
        name='likers'),
    url(r'^(?P<team_id>[0-9]+)/likers/(?P<other_user_id>[0-9]+)/$',
        TeamLiker.as_view(), name='liker'),
    # 粉丝
    url(r'^(?P<team_id>[0-9]+)/followers/$', TeamFollowerList.as_view(),
        name='followers'),
    url(r'^(?P<team_id>[0-9]+)/followers/(?P<other_user_id>[0-9]+)/$',
        TeamFollower.as_view(), name='follower'),
    # 评论
    url(r'^(?P<team_id>[0-9]+)/comments/$', TeamCommentList.as_view(),
        name='comments'),
    url(r'^(?P<team_id>[0-9]+)/comments/(?P<comment_id>[0-9]+)/$',
        TeamComment.as_view(), name='comment'),
    # 访客
    url(r'^(?P<team_id>[0-9]+)/visitors/$',
        TeamVisitorList.as_view(), name='visitors'),

    # 获取发布中的需求(全部,人员,外包或承接)列表(get)
    url(r'^needs/$', Needs.as_view(), name='needs'),
    # 获取某一团队发布的需求(全部,人员,外包或承接)列表(get)
    url(r'^(?P<team_id>[0-9]+)/needs/$', NeedSelf.as_view(),
        name='team_needs'),
    # 发布人员需求(post)
    url(r'^(?P<team_id>[0-9]+)/member_need/$', MemberNeed.as_view(),
        name='member_need'),
    # 发布外包需求(post)
    url(r'^(?P<team_id>[0-9]+)/outsource_need/$', OutsourceNeed.as_view(),
        name='outsource_need'),
    # 发布承接需求(post)
    url(r'^(?P<team_id>[0-9]+)/undertake_need/$', UndertakeNeed.as_view(),
        name='undertake_need'),
    # 获取需求详情(get)
    url(r'^(?P<team_id>[0-9]+)/need_detail/(?P<need_id>[0-9]+)$',
        NeedDetail.as_view(), name='need_detail'),
    # 设置需求为已满足(post)/设置需求为已删除(delete)
    url(r'^(?P<team_id>[0-9]+)/need/(?P<need_id>[0-9]+)$', NeedSelf.as_view(),
        name='need_self'),

    # 获取团队发布的所有任务(get)/发布任务(post)
    url(r'^(?P<team_id>[0-9]+)/tasks/$', Tasks.as_view(), name='tasks'),
    # 获取用户收到的所有任务(get)
    url(r'^tasks/$', TaskSelf.as_view(), name='tasks_self'),
    # 用户标记任务为已完成(post)
    url(r'^(?P<team_id>[0-9]+)/task/marker/(?P<task_id>[0-9]+)$',
        TaskMarker.as_view(), name='task_marker'),
    # 创始人确认用户的标记(post)/取消任务(delete)
    url(r'^(?P<team_id>[0-9]+)/task/(?P<task_id>[0-9]+)$', Task.as_view(),
        name='task'),
]
