from django.conf.urls import url

from main.views.user import Username, Password, IconSelf, ProfileSelf, \
    IdentificationSelf, IDCardPhoto, StudentCardPhoto
from main.views.user.experience import EducationExperiencesSelf, \
    WorkExperiencesSelf, FieldworkExperiencesSelf, EducationExperience, \
    WorkExperience, FieldworkExperience
from main.views.user.friend import Friends, FriendSelf, FriendRequests, \
    FriendRequest

urls = [
    url(r'^username/$', Username.as_view(), name='username'),
    url(r'^password/$', Password.as_view(), name='password'),
    url(r'^icon/$', IconSelf.as_view(), name='icon'),
    url(r'^profile/$', ProfileSelf.as_view(), name='profile'),
    url(r'^identification/$',
        IdentificationSelf.as_view(), name='identification'),
    url(r'^id_card_photo/$', IDCardPhoto.as_view(), name='id_card_photo'),
    url(r'^student_card_photo/$',
        StudentCardPhoto.as_view(), name='student_card_photo'),

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

    url(r'^friends/$', Friends.as_view(), name='friends'),
    url(r'^friends/(?P<other_user_id>[0-9]+)/$',
        FriendSelf.as_view(), name='friend'),
    url(r'^friends/requests/$',
        FriendRequests.as_view(), name='friend_requests'),
    url(r'^friends/requests/(?P<req_id>[0-9]+)/$',
        FriendRequest.as_view(), name='friend_request'),
]
