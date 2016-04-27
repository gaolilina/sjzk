from django.conf.urls import url

from main.views.experiences import EducationExperiencesReadOnly, \
    WorkExperiencesReadOnly, FieldworkExperiencesReadOnly
from main.views.user import Users, Token, ProfileReadOnly

urls = [
    url(r'^$', Users.as_view(), name='root'),
    url(r'^token/$', Token.as_view(), name='token'),
    url(r'^(?P<user_id>[0-9]+)/profile/$',
        ProfileReadOnly.as_view(), name='profile'),
    url(r'^(?P<user_id>[0-9]+)/experiences/education/$',
        EducationExperiencesReadOnly.as_view(), name='education_experiences'),
    url(r'^(?P<user_id>[0-9]+)/experiences/work/$',
        WorkExperiencesReadOnly.as_view(), name='work_experiences'),
    url(r'^(?P<user_id>[0-9]+)/experiences/fieldwork/$',
        FieldworkExperiencesReadOnly.as_view(), name='fieldwork_experiences'),
]
