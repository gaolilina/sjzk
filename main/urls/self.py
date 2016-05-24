from django.conf.urls import url

from main.views.like import UserLikers, UserLiker, LikedUser, LikedTeam
from main.views.user import Username, Password, IconSelf, ProfileSelf, \
    IdentificationSelf, IDCard, OtherCard
from main.views.user.experience import EducationExperiencesSelf, \
    WorkExperiencesSelf, FieldworkExperiencesSelf, EducationExperience, \
    WorkExperience, FieldworkExperience
from main.views.user.follow import UserFans, UserFan, FollowedUsers, \
    FollowedUserSelf, FollowedTeams, FollowedTeamSelf
from main.views.user.friend import Friends, FriendSelf, FriendRequests, \
    FriendRequest
from main.views.user.message import Contacts, Messages
from main.views.visitor import UserVisitors

urls = [
    # 基本信息
    url(r'^username/$', Username.as_view(), name='username'),
    url(r'^password/$', Password.as_view(), name='password'),
    url(r'^icon/$', IconSelf.as_view(), name='icon'),
    url(r'^profile/$', ProfileSelf.as_view(), name='profile'),
    url(r'^identification/$',
        IdentificationSelf.as_view(), name='identification'),
    url(r'^identification/id_card/$', IDCard.as_view(), name='id_card'),
    url(r'^identification/other_card/$',
        OtherCard.as_view(), name='other_card'),
    # 经历
    url(r'^experiences/education/$',
        EducationExperiencesSelf.as_view(), name='education_experiences'),
    url(r'^experiences/education/(?P<exp_id>[0-9]+)/$',
        EducationExperience.as_view(), name='education_experience'),
    url(r'^experiences/work/$',
        WorkExperiencesSelf.as_view(), name='work_experiences'),
    url(r'^experiences/work/(?P<exp_id>[0-9]+)/$',
        WorkExperience.as_view(), name='work_experience'),
    url(r'^experiences/fieldwork/$',
        FieldworkExperiencesSelf.as_view(), name='fieldwork_experiences'),
    url(r'^experiences/fieldwork/(?P<exp_id>[0-9]+)/$',
        FieldworkExperience.as_view(), name='fieldwork_experience'),
    # 关注
    url(r'^fans/$', UserFans.as_view(), name='fans'),
    url(r'^fans/(?P<other_user_id>[0-9]+)/$', UserFan.as_view(), name='fan'),
    url(r'^followed/users/$', FollowedUsers.as_view(), name='followed_users'),
    url(r'^followed/users/(?P<other_user_id>[0-9]+)/$',
        FollowedUserSelf.as_view(), name='followed_user'),
    url(r'^followed/teams/$',
        FollowedTeams.as_view(), name='followed_teams'),
    url(r'^followed/users/(?P<team_id>[0-9]+)/$',
        FollowedTeamSelf.as_view(), name='followed_team'),
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
    url(r'messages/', Contacts.as_view(), name='contacts'),
    url(r'messages/(?P<user_id>[0-9]+)/$', Messages.as_view(), name='messages'),
    # 访客
    url(r'^visitors/$', UserVisitors.as_view(), name='visitors'),
]
