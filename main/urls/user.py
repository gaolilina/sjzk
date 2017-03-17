from django.conf.urls import url

from ..views.user import *
from ..views.common import UserActionList, SearchUserActionList, \
    SearchTeamActionList, UserCommentList, UserComment,UserFollowerList, \
    UserFollower, UserLikerList, UserLiker, UserVisitorList, \
    ScreenUserActionList, ScreenTeamActionList
from ..views.recommend import UserRecommend

urls = [
    # 基本信息
    url(r'^$', List.as_view(), name='list'),
    url(r'^token/$', Token.as_view(), name='token'),
    url(r'^(?P<user_id>[0-9]+)/icon/$', Icon.as_view(), name='icon'),
    url(r'^(?P<user_id>[0-9]+)/profile/$', Profile.as_view(), name='profile'),
    # 获取某用户的团队
    url(r'^(?P<user_id>[0-9]+)/owned_teams/$',
        TeamOwnedList.as_view(), name='owned_teams'),
    url(r'^(?P<user_id>[0-9]+)/joined_teams/$',
        TeamJoinedList.as_view(), name='joined_teams'),
    # 活动
    url(r'^activity/$', ActivityList.as_view(), name='activity'),
    # 竞赛
    url(r'^competition/$', CompetitionList.as_view(), name='competition'),
    # 动态
    url(r'^(?P<user_id>[0-9]+)/actions/$', UserActionList.as_view(),
        name='actions'),
    # 评论
    url(r'^(?P<user_id>[0-9]+)/comments/$', UserCommentList.as_view(),
        name='comments'),
    url(r'comments/(?P<comment_id>[0-9]+)/$', UserComment.as_view(),
        name='comment'),
    # 经历
    url(r'^(?P<user_id>[0-9]+)/experiences/education/$',
        ExperienceList.as_view(), name='education_experiences',
        kwargs={'type': 'education'}),
    url(r'^(?P<user_id>[0-9]+)/experiences/work/$',
        ExperienceList.as_view(), name='work_experiences',
        kwargs={'type': 'work'}),
    url(r'^(?P<user_id>[0-9]+)/experiences/fieldwork/$',
        ExperienceList.as_view(), name='fieldwork_experiences',
        kwargs={'type': 'fieldwork'}),
    url(r'experiences/(?P<exp_id>[0-9]+)/$', Experience.as_view(),
        name='comment'),
    # 关注者
    url(r'^(?P<user_id>[0-9]+)/followers/$', UserFollowerList.as_view(),
        name='followers'),
    url(r'^(?P<user_id>[0-9]+)/followers/(?P<other_user_id>[0-9]+)/$',
        UserFollower.as_view(), name='followers'),
    # 好友
    url(r'^(?P<user_id>[0-9]+)/friends/$', FriendList.as_view(),
        name='friends'),
    url(r'^(?P<user_id>[0-9]+)/friends/(?P<other_user_id>[0-9]+)/$',
        Friend.as_view(), name='friend'),
    url(r'^(?P<user_id>[0-9]+)/friend_requests/$',
        FriendRequestList.as_view(), name='friend_requests'),
    # 点赞
    url(r'^(?P<user_id>[0-9]+)/likers/$', UserLikerList.as_view(),
        name='likers'),
    url(r'^(?P<user_id>[0-9]+)/likers/(?P<other_user_id>[0-9]+)/$',
        UserLiker.as_view(), name='liker'),
    # 搜索
    url(r'^search/$', Search.as_view(), name='search'),
    url(r'^search/user_action/$', SearchUserActionList.as_view(),
        name='search_user_action'),
    url(r'^search/team_action/$', SearchTeamActionList.as_view(),
        name='search_team_action'),
    # 筛选
    url(r'^screen/$', Screen.as_view(), name='screen'),
    url(r'^screen/user_action/$', ScreenUserActionList.as_view(),
        name='screen_user_action'),
    url(r'^screen/team_action/$', ScreenTeamActionList.as_view(),
        name='search_team_action'),
    # 验证码
    url(r'^validation_code/$', ValidationCode.as_view(), name='validation_code'),
    # 忘记密码
    url(r'^password_forgotten/$', PasswordForgotten.as_view(), name='password_forgotten'),
    # 访客
    url(r'^(?P<user_id>[0-9]+)/visitors/$',
        UserVisitorList.as_view(), name='visitors'),
    # 推荐
    url(r'^recommend/', UserRecommend.as_view(), name='recommend_users'),
]
