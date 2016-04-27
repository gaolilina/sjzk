from django.conf.urls import url

from main.views.user import Users, Token, Profile, EducationExperience, \
    WorkExperience

urls = [
    url(r'^$', Users.as_view(), name='root'),
    url(r'^token/$', Token.as_view(), name='token'),
    url(r'^(?P<user_id>[0-9]+)/profile/$', Profile.as_view(), name='profile'),
    url(r'^(?P<user_id>[0-9]+)/experiences/education/$',
        EducationExperience.as_view(), name='education_experiences'),
    url(r'^(?P<user_id>[0-9]+)/experiences/education/(?P<sn>[0-9]+)/$',
        EducationExperience.as_view(), name='education_experience'),
    url(r'^(?P<user_id>[0-9]+)/experiences/work/$',
        WorkExperience.as_view(), name='work_experiences'),
    url(r'^(?P<user_id>[0-9]+)/experiences/work/(?P<sn>[0-9]+)/$',
        WorkExperience.as_view(), name='work_experience'),
    url(r'^(?P<user_id>[0-9]+)/experiences/fieldwork/$',
        WorkExperience.as_view(), kwargs={'is_fieldwork': True},
        name='fieldwork_experiences'),
    url(r'^(?P<user_id>[0-9]+)/experiences/fieldwork/(?P<sn>[0-9]+)/$',
        WorkExperience.as_view(), kwargs={'is_fieldwork': True},
        name='fieldwork_experience'),
]
