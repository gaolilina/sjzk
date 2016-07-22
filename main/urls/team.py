from django.conf.urls import url

from main.views.team import Teams, TeamsSelf, Profile, Icon
from main.views.team.member import Members, Member, MemberSelf, MemberRequest,\
    MemberRequests, Invitation, InvitationSelf, Invitations
from main.views.team.need import Needs, NeedSelf, NeedDetail, MemberNeed, \
    OutsourceNeed, UndertakeNeed
from main.views.team.achievement import Achievement, Achievements
from main.views.team.task import Tasks, TaskSelf, TaskMarker, Task
from main.views.like import TeamLiker, TeamLikers
from main.views.follow import TeamFan, TeamFans
from main.views.comment import TeamComment, TeamComments
from main.views.visitor import TeamVisitors
from main.views.team.message import UserContacts, UserMessages, TeamContacts,\
    TeamMessages
from main.views.team.notification import Notification, Notifications

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
        MemberSelf.as_view(), name='member_self'),
    # 用户退出团队(delete)
    url(r'^member/leave/(?P<team_id>[0-9]+)/$', MemberSelf.as_view(),
        name='member_leave'),
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

    # 获取团队的评论信息列表(get)/对团队进行评论(post)
    url(r'^(?P<team_id>[0-9]+)/comments/$',
        TeamComments.as_view(), name='comments'),
    # 删除团队的某条评论
    url(r'^(?P<team_id>[0-9]+)/comments/(?P<comment_id>[0-9]+)/$',
        TeamComment.as_view(), name='comment'),

    # 获取团队的访客信息(get)
    url(r'^(?P<team_id>[0-9]+)/visitors/$',
        TeamVisitors.as_view(), name='visitors'),

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

    # 获取所有的成果列表(get)
    url(r'^achievements/$', Achievements.as_view(), name='achievements'),
    # 获取某一团队发布的成果列表(get)/发布成果(post)
    url(r'^(?P<team_id>[0-9]+)/achievements/$', Achievement.as_view(),
        name='team_achievements'),
    # 删除成果(delete)
    url(r'^(?P<team_id>[0-9]+)/achievement/(?P<achievement_id>[0-9]+)$',
        Achievement.as_view(), name='achievement_delete'),

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

    # 获取用户的团队联系列表(get)
    url(r'^contacts/$', UserContacts.as_view(), name='user_contacts'),
    # 获取用户的与某团队相关的消息(get)/用户向某团队发送消息(post)
    url(r'^(?P<team_id>[0-9]+)/messages/$', UserMessages.as_view(),
        name='user_messages'),
    # 获取团队的用户联系列表(get)
    url(r'^(?P<team_id>[0-9]+)/contacts/$', TeamContacts.as_view(),
        name='team_contacts'),
    # 获取团队的与某用户相关的消息(get)/团队向某用户发送消息(post)
    url(r'^(?P<team_id>[0-9]+)/messages/(?P<user_id>[0-9]+)/$',
        TeamMessages.as_view(), name='team_messages'),

    # 获取系统通知列表(get)/将所有通知标记为删除状态(delete)
    url(r'^(?P<team_id>[0-9]+)/notifications/$', Notifications.as_view(),
        name='notifications'),
    # 将某凭据对应的通知标记为删除状态
    url(r'^(?P<team_id>[0-9]+)/notification/(?P<receipt_id>[0-9]+)/$',
        Notification.as_view(), name='notification_delete'),
]
