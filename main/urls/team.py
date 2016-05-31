from django.conf.urls import url

from main.views.team import Teams, TeamsSelf, Profile, Icon
from main.views.team.member import Members, Member, MemberSelf, MemberRequest,\
    MemberRequests, Invitation, InvitationSelf, Invitations
from main.views.team.need import Needs, NeedSelf
from main.views.team.task import Tasks, TaskSelf, TaskMarker, Task
from main.views.like import TeamLiker, TeamLikers
from main.views.follow import TeamFan, TeamFans
from main.views.visitor import TeamVisitors

urls = [
    # 获取所有的团队列表(get)
    url(r'^$', Teams.as_view(), name='teams'),
    # 创建团队(post)
    url(r'^create/$', TeamsSelf.as_view(), name='team_create'),
    # 获取自己创建的团队列表(get)
    url(r'^owned/$', TeamsSelf.as_view(), name='teams_owned'),
    # 获取自己参加的团队列表(get)
    url(r'^joined/$', TeamsSelf.as_view(), name='teams_joined'),
    # 获取团队的基本信息(get)/修改团队的基本信息(post)
    url(r'^(?P<team_id>[0-9]+)/profile/$',
        Profile.as_view(), name='profile'),
    # 获取(get)/设置团队头像(post)
    url(r'^(?P<team_id>[0-9]+)/icon/$', Icon.as_view(), name='icon'),

    # 获取团队成员列表(get)
    url(r'^members/(?P<team_id>[0-9]+)/$', Members.as_view(), name='members'),
    # 检查当前用户是否为团队成员(get)
    url(r'^member/(?P<team_id>[0-9]+)/$', Member.as_view(), name='member'),
    # 添加用户为团队成员(post)/删除团队成员(delete)
    url(r'^member/(?P<team_id>[0-9]+)/(?P<user_id>[0-9]+)/$',
        MemberSelf.as_view(), name='memberSelf'),
    # 获取团队的加入申请列表(get)/用户向团队发出加入申请(post)
    url(r'^member/requests/(?P<team_id>[0-9]+)/$',
        MemberRequests.as_view(), name='member_requests'),
    # 忽略用户的加入团队申请(delete)
    url(r'^member/request/(?P<team_id>[0-9]+)/(?P<user_id>[0-9]+)/$',
        MemberRequest.as_view(), name='member_request'),
    # 获取用户的加入团队邀请列表(get)
    url(r'^invitations/$',
        Invitations.as_view(), name='invitations'),
    # 同意团队的加入邀请并成为团队成员（post）/忽略团队的加入团队邀请(delete)
    url(r'^invitation/(?P<team_id>[0-9]+)/$',
        InvitationSelf.as_view(), name='invitation_self'),
    # 团队向用户发出加入邀请(post)
    url(r'^invitation/(?P<team_id>[0-9]+)/(?P<user_id>[0-9]+)/$',
        Invitation.as_view(), name='invitation'),

    # 获取团队的点赞者信息列表(get)
    url(r'^(?P<team_id>[0-9]+)/likers/$', TeamLikers.as_view(), name='likers'),
    # 判断用户是否给团队点过赞(get)
    url(r'^(?P<team_id>[0-9]+)/likers/(?P<other_user_id>[0-9]+)/$',
        TeamLiker.as_view(), name='liker'),

    # 获取团队的粉丝信息列表(get)
    url(r'^(?P<team_id>[0-9]+)/fans/$', TeamFans.as_view(), name='fans'),
    # 判断用户是否关注过团队(get)
    url(r'^(?P<team_id>[0-9]+)/fans/(?P<other_user_id>[0-9]+)/$',
        TeamFan.as_view(), name='fan'),

    # 获取团队的访客信息(get)
    url(r'^(?P<team_id>[0-9]+)/visitors/$',
        TeamVisitors.as_view(), name='visitors'),

    # 获取所有的需求列表(get)/发布需求(post)
    url(r'^needs/$', Needs.as_view(), name='needs'),
    # 获取某一团队发布的需求列表(get)/发布需求(post)
    url(r'^(?P<team_id>[0-9]+)/needs/$', NeedSelf.as_view(),
        name='team_needs'),
    # 删除需求(delete)
    url(r'^(?P<team_id>[0-9]+)/need/(?P<need_id>[0-9]+)$', NeedSelf.as_view(),
        name='need_delete'),

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