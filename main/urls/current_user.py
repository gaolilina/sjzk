from django.conf.urls import url

from main.views.account.auth import IdentityVerificationView
from main.views.account.phone import BindPhoneNumber
from main.views.achievement import AchievementList
from main.views.activity.user_activity import MyJoinedActivityList
from main.views.competition import CompetitionList
from main.views.follow.user import UserFollowerList
from main.views.friend import FriendAction, MyFriendList
from main.views.friend.request import FriendRequestList, FriendRequestAction
from main.views.lab import LabActionCommentList, FollowedLabActionList, FollowedLabList, FollowedLab, LikedLab, \
    LikedLabAction, RelatedLabList, OwnedLabList
from main.views.like.user import UserLikerList
from main.views.experience import ExperienceList
from main.views.me.info import Username, Password, Icon, Getui, Profile
from main.views.me.score import UserScoreRecord
from main.views.me.visit import UserVisitorList
from main.views.search.action import SearchLabAction
from main.views.team.user import RelatedTeamList, OwnedTeamList
from ..views.forum import BoardList

urls = [
    url(r'^icon/$', Icon.as_view()),
    url(r'^profile/$', Profile.as_view()),
    url(r'^getui/$', Getui.as_view()),
    url(r'^password/$', Password.as_view()),
    # 访客
    url(r'^visitors/$', UserVisitorList.as_view()),
    # 对我点赞的用户
    url(r'^liker/$', UserLikerList.as_view()),
    # 关注我的用户，我的粉丝
    url(r'^followers/$', UserFollowerList.as_view()),
    # 积分明细
    url(r'^score_records/$', UserScoreRecord.as_view()),

    # 绑定手机号
    url(r'^bind_phone_number/$', BindPhoneNumber.as_view()),

    # 需要迁移走
    # 与当前用户相关的团队
    url(r'^teams/$', RelatedTeamList.as_view()),
    url(r'^teams/owned/$', OwnedTeamList.as_view()),
    # 活动
    url(r'^activity/$', MyJoinedActivityList.as_view()),
    # 竞赛
    url(r'^competition/$', CompetitionList.as_view()),
    url(r'^achievements/$', AchievementList.as_view()),

    #####################################弃用
    # 实名认证
    url(r'^identity_verification/$', IdentityVerificationView.as_view()),
    url(r'^lab_actions/$', SearchLabAction.as_view()),
    url(r'^followed_lab/actions/$', FollowedLabActionList.as_view()),
    url(r'^lab_action/(?P<action_id>[0-9]+)/comments/$', LabActionCommentList.as_view()),
    url(r'^followed/labs/$', FollowedLabList.as_view()),
    url(r'^followed/labs/(?P<lab_id>[0-9]+)/$', FollowedLab.as_view()),
    url(r'liked/labs/(?P<lab_id>[0-9]+)/$', LikedLab.as_view()),
    url(r'liked/lab_actions/(?P<action_id>[0-9]+)/$', LikedLabAction.as_view()),
    # 与当前用户相关的团队
    url(r'^labs/$', RelatedLabList.as_view()),
    url(r'^labs/owned/$', OwnedLabList.as_view()),
    # 论坛版块
    url(r'^forum_boards/$', BoardList.as_view(), kwargs={'owned_only': True}),
    # 好友
    url(r'^friends/$', MyFriendList.as_view()),
    url(r'^friends/(?P<other_user_id>[0-9]+)/$', FriendAction.as_view()),
    url(r'^friend_requests/$', FriendRequestList.as_view()),
    url(r'^friend_requests/(?P<req_id>[0-9]+)/$', FriendRequestAction.as_view()),
    # 经历
    url(r'^experiences/education/$', ExperienceList.as_view(), kwargs={'type': 'education'}),
    url(r'^experiences/work/$', ExperienceList.as_view(), kwargs={'type': 'work'}),
    url(r'^experiences/fieldwork/$', ExperienceList.as_view(), kwargs={'type': 'fieldwork'}),
    # 基本信息
    url(r'^username/$', Username.as_view()),
]
