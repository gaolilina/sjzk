from django.conf.urls import url

from main.views.activity.user_activity import FollowedActivityList, FollowedActivity, LikedActivity, FavoredActivity, \
    ActivityList
from main.views.search.action import SearchUserAction, SearchTeamAction, SearchLabAction
from main.views.account.auth import IdentityVerificationView
from main.views.friend import FriendAction, MyFriendList
from main.views.friend.request import FriendRequestList, FriendRequestAction
from ..views.current_user import *
from ..views.common import *
from ..views.forum import BoardList
from ..views.report import Report

urls = [
    # 基本信息
    url(r'^username/$', Username.as_view()),
    url(r'^password/$', Password.as_view()),
    url(r'^icon/$', Icon.as_view()),
    url(r'^profile/$', Profile.as_view()),
    url(r'^getui/$', Getui.as_view()),
    # 实名认证
    url(r'^identity_verification/$', IdentityVerificationView.as_view()),
    # 动态
    url(r'^user_actions/$', SearchUserAction.as_view()),
    url(r'^team_actions/$', SearchTeamAction.as_view()),
    url(r'^lab_actions/$', SearchLabAction.as_view()),
    url(r'^owned_actions/$', UserActionList.as_view()),
    url(r'^followed_user/actions/$', FollowedUserActionList.as_view()),
    url(r'^followed_team/actions/$', FollowedTeamActionList.as_view()),
    url(r'^followed_lab/actions/$', FollowedLabActionList.as_view()),
    # 评论
    url(r'^comments/$', UserCommentList.as_view()),
    url(r'^user_action/(?P<action_id>[0-9]+)/comments/$', UserActionCommentList.as_view()),
    url(r'^team_action/(?P<action_id>[0-9]+)/comments/$', TeamActionCommentList.as_view()),
    url(r'^lab_action/(?P<action_id>[0-9]+)/comments/$', LabActionCommentList.as_view()),
    url(r'^system_action/(?P<action_id>[0-9]+)/comments/$', SystemActionCommentList.as_view()),
    # 经历
    url(r'^experiences/education/$', ExperienceList.as_view(), kwargs={'type': 'education'}),
    url(r'^experiences/work/$', ExperienceList.as_view(), kwargs={'type': 'work'}),
    url(r'^experiences/fieldwork/$', ExperienceList.as_view(), kwargs={'type': 'fieldwork'}),
    # 关注
    url(r'^followers/$', UserFollowerList.as_view()),
    url(r'^followed/users/$', FollowedUserList.as_view()),
    url(r'^followed/users/(?P<user_id>[0-9]+)/$', FollowedUser.as_view()),
    url(r'^followed/teams/$', FollowedTeamList.as_view()),
    url(r'^followed/teams/(?P<team_id>[0-9]+)/$', FollowedTeam.as_view()),
    url(r'^followed/labs/$', FollowedLabList.as_view()),
    url(r'^followed/labs/(?P<lab_id>[0-9]+)/$', FollowedLab.as_view()),
    url(r'^followed/needs/$', FollowedTeamNeedList.as_view()),
    url(r'^followed/needs/(?P<need_id>[0-9]+)/$', FollowedTeamNeed.as_view()),
    url(r'^followed/activities/$', FollowedActivityList.as_view()),
    url(r'^followed/activities/(?P<activity_id>[0-9]+)/$', FollowedActivity.as_view()),
    url(r'^followed/competitions/$', FollowedCompetitionList.as_view()),
    url(r'^followed/competitions/(?P<competition_id>[0-9]+)/$', FollowedCompetition.as_view()),
    # 好友
    url(r'^friends/$', MyFriendList.as_view()),
    url(r'^friends/(?P<other_user_id>[0-9]+)/$', FriendAction.as_view()),
    url(r'^friend_requests/$', FriendRequestList.as_view()),
    url(r'^friend_requests/(?P<req_id>[0-9]+)/$', FriendRequestAction.as_view()),
    # 点赞
    url(r'likers/$', UserLikerList.as_view()),
    url(r'likers/(?P<other_user_id>[0-9]+)/$', UserLiker.as_view()),
    url(r'liked/users/(?P<user_id>[0-9]+)/$', LikedUser.as_view()),
    url(r'liked/teams/(?P<team_id>[0-9]+)/$', LikedTeam.as_view()),
    url(r'liked/labs/(?P<lab_id>[0-9]+)/$', LikedLab.as_view()),
    url(r'liked/activities/(?P<activity_id>[0-9]+)/$', LikedActivity.as_view()),
    url(r'liked/competitions/(?P<competition_id>[0-9]+)/$', LikedCompetition.as_view()),
    url(r'liked/user_actions/(?P<action_id>[0-9]+)/$', LikedUserAction.as_view()),
    url(r'liked/team_actions/(?P<action_id>[0-9]+)/$', LikedTeamAction.as_view()),
    url(r'liked/lab_actions/(?P<action_id>[0-9]+)/$', LikedLabAction.as_view()),
    url(r'liked/system_actions/(?P<action_id>[0-9]+)/$', LikedSystemAction.as_view()),
    url(r'liked/user_tags/(?P<tag_id>.+?)/$', LikedUserTag.as_view()),
    url(r'liked/team_tags/(?P<tag_id>.+?)/$', LikedTeamTag.as_view()),
    # 访客
    url(r'^visitors/$', UserVisitorList.as_view()),
    # 与当前用户相关的团队
    url(r'^teams/$', RelatedTeamList.as_view()),
    url(r'^teams/owned/$', OwnedTeamList.as_view()),
    # 与当前用户相关的团队
    url(r'^labs/$', RelatedLabList.as_view()),
    url(r'^labs/owned/$', OwnedLabList.as_view()),
    # 团队邀请
    url(r'^invitations/$', InvitationList.as_view()),
    url(r'^invitations/(?P<invitation_id>[0-9]+)/$', Invitation.as_view()),
    # 论坛版块
    url(r'^forum_boards/$', BoardList.as_view(), kwargs={'owned_only': True}),
    # 意见反馈
    url(r'^feedback/$', Feedback.as_view()),
    # 活动
    url(r'^activity/$', ActivityList.as_view()),
    # 竞赛
    url(r'^competition/$', CompetitionList.as_view()),
    # 邀请码
    url(r'^invitation_code/$', InvitationCode.as_view()),
    url(r'^inviter/$', Inviter.as_view()),
    # 绑定手机号
    url(r'^bind_phone_number/$', BindPhoneNumber.as_view()),
    # 举报
    url(r'^report/$', Report.as_view()),
    # 积分明细
    url(r'^score_records/$', UserScoreRecord.as_view()),
    # 收藏
    url(r'^favored/activities/$', FavoredActivityList.as_view()),
    url(r'^favored/competitions/$', FavoredCompetitionList.as_view()),
    url(r'^favored/user_actions/$', FavoredUserActionList.as_view()),
    url(r'^favored/team_actions/$', FavoredTeamActionList.as_view()),
    url(r'^favored/lab_actions/$', FavoredLabActionList.as_view()),
    url(r'^favored/system_actions/$', FavoredSystemActionList.as_view()),
    url(r'^favored/activities/(?P<activity_id>[0-9]+)/$', FavoredActivity.as_view()),
    url(r'^favored/competitions/(?P<competition_id>[0-9]+)/$', FavoredCompetition.as_view()),
    url(r'^favored/user_actions/(?P<action_id>[0-9]+)/$', FavoredUserAction.as_view()),
    url(r'^favored/team_actions/(?P<action_id>[0-9]+)/$', FavoredTeamAction.as_view()),
    url(r'^favored/lab_actions/(?P<action_id>[0-9]+)/$', FavoredLabAction.as_view()),
    url(r'^favored/system_actions/(?P<action_id>[0-9]+)/$', FavoredSystemAction.as_view()),
    url(r'^achievements/$', AchievementList.as_view()),
]
