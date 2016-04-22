from django.conf.urls import url

from main.views.user import Username, Password, Profile, EducationExperience, \
    WorkExperience

urls = [
    url(r'^username/$', Username.as_view(), name='username'),
    url(r'^password/$', Password.as_view(), name='password'),
    url(r'^profile/$', Profile.as_view(), name='profile'),
    url(r'^experience/education/$',
        EducationExperience.as_view(), name='education_experiences'),
    url(r'^experience/education/(?P<sn>[0-9]+)/$',
        EducationExperience.as_view(), name='education_experience'),
    url(r'^experience/work/$',
        WorkExperience.as_view(), name='work_experiences'),
    url(r'^experience/work/(?P<sn>[0-9]+)/$',
        WorkExperience.as_view(), name='work_experience'),
    url(r'^experience/fieldwork/$',
        WorkExperience.as_view(), kwargs={'is_fieldwork': True},
        name='fieldwork_experiences'),
    url(r'^experience/fieldwork/(?P<sn>[0-9]+)/$',
        WorkExperience.as_view(), kwargs={'is_fieldwork': True},
        name='fieldwork_experience'),
]
