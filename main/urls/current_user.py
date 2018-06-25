from django.conf.urls import url

from ..views.current_user import *
from ..views.common import UserActionsList, TeamActionsList, UserActionList, \
    UserCommentList, UserFollowerList, UserLikerList, UserLiker, \
    UserVisitorList, FollowedUserActionList, FollowedTeamActionList, \
    UserActionCommentList, TeamActionCommentList, SystemActionCommentList, \
    FavoredUserActionList, FavoredTeamActionList, FavoredSystemActionList, \
    FavoredActivityList, FavoredCompetitionList
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
    url(r'^getui/$', Getui.as_view(), name='getui'),
    # 实名认证
    url(r'^identity_verification/$',
        IdentityVerification.as_view(), name='identity_verification'),
    # eid认证
    url(r'^eid_identity_verification/$',
        EidIdentityVerification.as_view(), name='eid_identity_verification'),
    # 身份认证
    url(r'^other_identity_verification/$', OtherIdentityVerification.as_view(),
        name='other_identity_verification'),
    # 动态
    url(r'^user_actions/$', UserActionsList.as_view(), name='user_actions'),
    url(r'^team_actions/$', TeamActionsList.as_view(), name='team_actions'),
    url(r'^owned_actions/$', UserActionList.as_view(), name='owned_actions'),
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
    url(r'^system_action/(?P<action_id>[0-9]+)/comments/$',
        SystemActionCommentList.as_view(), name='system_action_comments'),
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
    url(r'^followed/needs/$',
        FollowedTeamNeedList.as_view(), name='followed_needs'),
    url(r'^followed/needs/(?P<need_id>[0-9]+)/$',
        FollowedTeamNeed.as_view(), name='followed_need'),
    url(r'^followed/activities/$',
        FollowedActivityList.as_view(), name='followed_activities'),
    url(r'^followed/activities/(?P<activity_id>[0-9]+)/$',
        FollowedActivity.as_view(), name='followed_activity'),
    url(r'^followed/competitions/$',
        FollowedCompetitionList.as_view(), name='followed_competitions'),
    url(r'^followed/competitions/(?P<competition_id>[0-9]+)/$',
        FollowedCompetition.as_view(), name='followed_competition'),
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
    url(r'liked/system_actions/(?P<action_id>[0-9]+)/$',
        LikedSystemAction.as_view(), name='liked_system_action'),
    url(r'liked/user_tags/(?P<tag_id>.+?)/$',
        LikedUserTag.as_view(), name='liked_user_tag'),
    url(r'liked/team_tags/(?P<tag_id>.+?)/$',
        LikedTeamTag.as_view(), name='liked_team_tag'),
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
    url(r'^activity/$', ActivityList.as_view(), name='owned_activity'),
    # 竞赛
    url(r'^competition/$', CompetitionList.as_view(), name='owned_competition'),
    # 邀请码
    url(r'^invitation_code/$', InvitationCode.as_view(),
        name='invitation_code'),
    url(r'^inviter/$', Inviter.as_view(),
        name='inviter'),
    # 绑定手机号
    url(r'^bind_phone_number/$', BindPhoneNumber.as_view(),
        name='bind_phone_number'),
    # 举报
    url(r'^report/$', Report.as_view(), name='report'),
    # 积分明细
    url(r'^score_records/$', UserScoreRecord.as_view(), name='score_records'),
    # 收藏
    url(r'^favored/activities/$', FavoredActivityList.as_view(),
        name='favored_activities'),
    url(r'^favored/competitions/$', FavoredCompetitionList.as_view(),
        name='favored_competitions'),
    url(r'^favored/user_actions/$', FavoredUserActionList.as_view(),
        name='favored_user_actions'),
    url(r'^favored/team_actions/$', FavoredTeamActionList.as_view(),
        name='favored_team_actions'),
    url(r'^favored/system_actions/$', FavoredSystemActionList.as_view(),
        name='favored_system_actions'),
    url(r'^favored/activities/(?P<activity_id>[0-9]+)/$',
        FavoredActivity.as_view(), name='favored_activity'),
    url(r'^favored/competitions/(?P<competition_id>[0-9]+)/$',
        FavoredCompetition.as_view(), name='favored_competition'),
    url(r'^favored/user_actions/(?P<action_id>[0-9]+)/$',
        FavoredUserAction.as_view(), name='favored_user_action'),
    url(r'^favored/team_actions/(?P<action_id>[0-9]+)/$',
        FavoredTeamAction.as_view(), name='favored_team_action'),
    url(r'^favored/system_actions/(?P<action_id>[0-9]+)/$',
        FavoredSystemAction.as_view(), name='favored_system_action'),
    url(r'^achievements/$', AchievementList.as_view(),
        name='achievements'),
]
