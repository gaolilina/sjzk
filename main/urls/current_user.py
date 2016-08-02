from django.conf.urls import url

from ..views.current_user import *
from ..views.common import UserActionList, UserCommentList, UserFollowerList

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
    url(r'^friends/$', Friends.as_view(), name='friends'),
    url(r'^friends/(?P<other_user_id>[0-9]+)/$',
        FriendSelf.as_view(), name='friend'),
    url(r'^friends/requests/$',
        FriendRequests.as_view(), name='friend_requests'),
    url(r'^friends/requests/(?P<req_id>[0-9]+)/$',
        FriendRequest.as_view(), name='friend_request'),
    # 点赞
    url(r'likers/$', UserLikers.as_view(), name='likers'),
    url(r'likers/(?P<other_user_id>[0-9]+)/$',
        UserLiker.as_view(), name='liker'),
    url(r'liked/users/(?P<user_id>[0-9]+)/$',
        LikedUser.as_view(), name='liked_user'),
    url(r'liked/teams/(?P<team_id>[0-9]+)/$',
        LikedTeam.as_view(), name='liked_team'),
    # 消息
    url(r'messages/$', Contacts.as_view(), name='contacts'),
    url(r'messages/(?P<user_id>[0-9]+)/$', Messages.as_view(), name='messages'),
    url(r'messages/(?P<user_id>[0-9]+)/share_user/(?P<other_user_id>[0-9]+)$',
        ShareUser.as_view(), name='share_user'),
    url(r'messages/(?P<user_id>[0-9]+)/share_team/(?P<team_id>[0-9]+)$',
        ShareTeam.as_view(), name='share_team'),
    # 通知
    url(r'notifications/$',
        Notifications.as_view(), name='notifications'),
    url(r'notifications/(?P<receipt_id>[0-9]+)/$',
        Notification.as_view(), name='notification'),
    # 访客
    url(r'^visitors/$', UserVisitors.as_view(), name='visitors'),
]
