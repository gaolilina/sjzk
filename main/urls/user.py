from django.conf.urls import url

from ..views.user import *
from ..views.action import UserActions

urls = [
    # 基本信息
    url(r'^$', List.as_view(), name='root'),
    url(r'^token/$', Token.as_view(), name='token'),
    url(r'^(?P<user_id>[0-9]+)/icon/$', Icon.as_view(), name='icon'),
    url(r'^(?P<user_id>[0-9]+)/profile/$', Profile.as_view(), name='profile'),
    # 动态
    url(r'^(?P<user_id>[0-9]+)/actions/$',
        UserActions.as_view(), name='actions'),
    # 评论
    url(r'^(?P<user_id>[0-9]+)/comments/$',
        UserComments.as_view(), name='comments'),
    # 经历
    url(r'^(?P<user_id>[0-9]+)/experiences/education/$',
        EducationExperiences.as_view(), name='education_experiences'),
    url(r'^(?P<user_id>[0-9]+)/experiences/work/$',
        WorkExperiences.as_view(), name='work_experiences'),
    url(r'^(?P<user_id>[0-9]+)/experiences/fieldwork/$',
        FieldworkExperiences.as_view(), name='fieldwork_experiences'),
    # 关注
    url(r'^(?P<user_id>[0-9]+)/fans/$', UserFans.as_view(), name='fans'),
    url(r'^(?P<user_id>[0-9]+)/fans/(?P<other_user_id>[0-9]+)/$',
        UserFan.as_view(), name='fan'),
    url(r'^(?P<user_id>[0-9]+)/followed/users/$',
        FollowedUsers.as_view(), name='followed_users'),
    url(r'^(?P<user_id>[0-9]+)/followed/users/(?P<other_user_id>[0-9]+)/$',
        FollowedUser.as_view(), name='followed_user'),
    url(r'^(?P<user_id>[0-9]+)/followed/teams/$',
        FollowedTeams.as_view(), name='followed_teams'),
    url(r'^(?P<user_id>[0-9]+)/followed/teams/(?P<team_id>[0-9]+)/$',
        FollowedTeam.as_view(), name='followed_team'),
    # 好友
    url(r'^(?P<user_id>[0-9]+)/friends/$', Friends.as_view(), name='friends'),
    url(r'^(?P<user_id>[0-9]+)/friends/(?P<other_user_id>[0-9]+)/$',
        Friend.as_view(), name='friend'),
    url(r'^(?P<user_id>[0-9]+)/friends/requests/$',
        FriendRequests.as_view(), name='friend_requests'),
    # 点赞
    url(r'^(?P<user_id>[0-9]+)/likers/$', UserLikers.as_view(), name='likers'),
    url(r'^(?P<user_id>[0-9]+)/likers/(?P<other_user_id>[0-9]+)/$',
        UserLiker.as_view(), name='liker'),
    # 搜索
    url(r'search/$', UserSearch.as_view(), name='search'),
    # 访客
    url(r'^(?P<user_id>[0-9]+)/visitors/$',
        UserVisitors.as_view(), name='visitors'),
]
