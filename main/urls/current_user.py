from django.conf.urls import url

from ..views.current_user import *
from ..views.common import UserActionList, UserCommentList, UserFollowerList, \
    UserLikerList, UserLiker

urls = [
    # 基本信息
    url(r'^username/$', Username.as_view(), name='username'),
    url(r'^password/$', Password.as_view(), name='password'),
    url(r'^icon/$', Icon.as_view(), name='icon'),
    url(r'^id_card/$', IDCard.as_view(), name='id_card'),
    url(r'^other_card/$', OtherCard.as_view(), name='other_card'),
    url(r'^profile/$', Profile.as_view(), name='profile'),
    # 动态
    url(r'actions/$', UserActionList.as_view(), name='actions'),
    # 评论
    url(r'comments/$', UserCommentList.as_view(), name='comments'),
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
    # 访客
    url(r'^visitors/$', UserVisitors.as_view(), name='visitors'),
]
