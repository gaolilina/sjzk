from django.conf.urls import url

from ..views.team import *

urls = [
    url(r'^$', List.as_view(), name='list'),
    url(r'^(?P<team_id>[0-9]+)/profile/$', Profile.as_view(), name='profile'),
    url(r'^(?P<team_id>[0-9]+)/icon/$', Icon.as_view(), name='icon'),

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
