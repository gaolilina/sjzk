from django.conf.urls import url

from main.views.team import Teams, TeamsSelf, Profile, Icon
from main.views.team.member import Members, Member, MemberSelf, MemberRequest,\
    MemberRequests, Invitation, InvitationSelf, Invitations

urls = [
    # 获取自己创建(或者参加)的团队列表(get)/创建团队(post)
    url(r'^$', TeamsSelf.as_view(), name='root_self'),
    # 获取团队列表(get)
    url(r'^list$', Teams.as_view(), name='root'),
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
]