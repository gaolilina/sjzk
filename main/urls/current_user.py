from django.conf.urls import url

from ..views.current_user import *
from ..views.common import UserActionsList, TeamActionsList, UserActionList, \
    UserCommentList, UserFollowerList, UserLikerList, UserLiker, \
    UserVisitorList, FollowedUserActionList, FollowedTeamActionList, \
    UserActionCommentList, TeamActionCommentList
from ..views.forum import BoardList
from ..views.report import Report

urls = [
    # 基本信息
    url(r'^username/$', Username.as_view(), name='username'),
    url(r'^password/$', Password.as_view(), name='password'),
    url(r'^icon/$', Icon.as_view(), name='icon'),
    url(r'^id_card/$', IDCard.as_view(), name='id_card'),
    url(r'^other_card/$', OtherCard.as_view(), name='other_card'),
    url(r'^profile/$', Profile.as_view(), name='profile'),
    url(r'^identity_verification/$',
        IdentityVerification.as_view(), name='identity_verification'),
    # 动态
    url(r'user_actions/$', UserActionsList.as_view(), name='user_actions'),
    url(r'team_actions/$', TeamActionsList.as_view(), name='team_actions'),
    url(r'owned_actions/$', UserActionList.as_view(), name='owned_actions'),
    url(r'^followed_user/actions/$', FollowedUserActionList.as_view(),
        name='followed_actions'),
    url(r'^followed_team/actions/$',
        FollowedTeamActionList.as_view(), name='followers'),
    # 评论
    url(r'^comments/$', UserCommentList.as_view(), name='comments'),
    url(r'^user_action/(?P<action_id>[0-9]+)/comments/$',
        UserActionCommentList.as_view(), name='user_action_comments'),
    url(r'^team_action/(?P<action_id>[0-9]+)/comments/$',
        TeamActionCommentList.as_view(), name='team_action_comments'),
    # 经历
    url(r'^experiences/education/$',
        ExperienceList.as_view(), name='education_experiences',
        kwargs={'type': 'education'}),
    url(r'^experiences/work/$',
        ExperienceList.as_view(), name='work_experiences',
        kwargs={'type': 'work'}),
    url(r'^experiences/fieldwork/$',
        ExperienceList.as_view(), name='fieldwork_experiences',
        kwargs={'type': 'fieldwork'}),
    # 关注
    url(r'^followers/$', UserFollowerList.as_view(), name='follower'),
    url(r'^followed/users/$', FollowedUserList.as_view(),
        name='followed_users'),
    url(r'^followed/users/(?P<user_id>[0-9]+)/$',
        FollowedUser.as_view(), name='followed_user'),
    url(r'^followed/teams/$',
        FollowedTeamList.as_view(), name='followed_teams'),
    url(r'^followed/teams/(?P<team_id>[0-9]+)/$',
        FollowedTeam.as_view(), name='followed_team'),
    # 好友
    url(r'^friends/$', FriendList.as_view(), name='friends'),
    url(r'^friends/(?P<other_user_id>[0-9]+)/$', Friend.as_view(),
        name='friend'),
    url(r'^friend_requests/$', FriendRequestList.as_view(),
        name='friend_requests'),
    url(r'^friend_requests/(?P<req_id>[0-9]+)/$',
        FriendRequest.as_view(), name='friend_request'),
    # 点赞
    url(r'likers/$', UserLikerList.as_view(), name='likers'),
    url(r'likers/(?P<other_user_id>[0-9]+)/$',
        UserLiker.as_view(), name='liker'),
    url(r'liked/users/(?P<user_id>[0-9]+)/$',
        LikedUser.as_view(), name='liked_user'),
    url(r'liked/teams/(?P<team_id>[0-9]+)/$',
        LikedTeam.as_view(), name='liked_team'),
    url(r'liked/activities/(?P<activity_id>[0-9]+)/$',
        LikedActivity.as_view(), name='liked_activity'),
    url(r'liked/competitions/(?P<competition_id>[0-9]+)/$',
        LikedCompetition.as_view(), name='liked_competition'),
    url(r'liked/user_actions/(?P<action_id>[0-9]+)/$',
        LikedUserAction.as_view(), name='liked_user_action'),
    url(r'liked/team_actions/(?P<action_id>[0-9]+)/$',
        LikedTeamAction.as_view(), name='liked_team_action'),
    # 访客
    url(r'^visitors/$', UserVisitorList.as_view(), name='visitors'),
    # 与当前用户相关的团队
    url(r'^teams/$', RelatedTeamList.as_view(), name='teams'),
    url(r'^teams/owned/$', OwnedTeamList.as_view(), name='owned_teams'),
    # 团队邀请
    url(r'^invitations/$', InvitationList.as_view(),
        name='invitations'),
    url(r'^invitations/(?P<invitation_id>[0-9]+)/$', Invitation.as_view(),
        name='invitation'),
    # 论坛版块
    url(r'^forum_boards/$', BoardList.as_view(),
        name='forum_boards', kwargs={'owned_only': True}),
    # 意见反馈
    url(r'^feedback/$', Feedback.as_view(), name='feedback'),
    # 活动
    url(r'^activity/$', ActivityList.as_view(), name='activity'),
    # 竞赛
    url(r'^competition/$', CompetitionList.as_view(), name='owned_competition'),
    # 邀请码
    url(r'^invitation_code/$', InvitationCode.as_view(),
        name='invitation_code'),
    # 绑定手机号
    url(r'^bind_phone_number/$', BindPhoneNumber.as_view(),
        name='bind_phone_number'),
    # 举报
    url(r'^report/$', Report.as_view(), name='report'),
    # 积分明细
    url(r'^score_records/$', UserScoreRecord.as_view(), name='score_records'),
]
