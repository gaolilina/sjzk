from django.conf.urls import url

from main.views.user import Users, Token, Icon, Profile, Identification
from main.views.user.experience import EducationExperiences, WorkExperiences, \
    FieldworkExperiences
from main.views.user.friend import Friends, Friend, FriendRequests

urls = [
    url(r'^$', Users.as_view(), name='root'),
    url(r'^token/$', Token.as_view(), name='token'),
    url(r'^(?P<user_id>[0-9]+)/icon/$', Icon.as_view(), name='icon'),
    url(r'^(?P<user_id>[0-9]+)/profile/$',
        Profile.as_view(), name='profile'),
    url(r'^(?P<user_id>[0-9]+)/identification/$',
        Identification.as_view(), name='identification'),

    url(r'^(?P<user_id>[0-9]+)/experiences/education/$',
        EducationExperiences.as_view(), name='education_experiences'),
    url(r'^(?P<user_id>[0-9]+)/experiences/work/$',
        WorkExperiences.as_view(), name='work_experiences'),
    url(r'^(?P<user_id>[0-9]+)/experiences/fieldwork/$',
        FieldworkExperiences.as_view(), name='fieldwork_experiences'),

    url(r'^(?P<user_id>[0-9]+)/friends/$', Friends.as_view(), name='friends'),
    url(r'^(?P<user_id>[0-9]+)/friends/(?P<other_user_id>[0-9]+)/$',
        Friend.as_view(), name='friend'),
    url(r'^(?P<user_id>[0-9]+)/friends/requests/$',
        FriendRequests.as_view(), name='friend_requests'),
]
