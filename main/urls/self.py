from django.conf.urls import url

from main.views.self import Username, Password, Profile, EducationExperiences, \
    EducationExperiencesWriteOnly, WorkExperiences, WorkExperiencesWriteOnly, \
    FieldworkExperiences, FieldworkExperiencesWriteOnly

urls = [
    url(r'^username/$', Username.as_view(), name='username'),
    url(r'^password/$', Password.as_view(), name='password'),
    url(r'^profile/$', Profile.as_view(), name='profile'),
    url(r'^experiences/education/$',
        EducationExperiences.as_view(), name='education_experiences'),
    url(r'^experiences/education/(?P<exp_id>[0-9]+)/$',
        EducationExperiencesWriteOnly.as_view(), name='education_experience'),
    url(r'^experiences/work/$',
        WorkExperiences.as_view(), name='work_experiences'),
    url(r'^experiences/work/(?P<exp_id>[0-9]+)/$',
        WorkExperiencesWriteOnly.as_view(), name='work_experience'),
    url(r'^experiences/fieldwork/$',
        FieldworkExperiences.as_view(), name='fieldwork_experiences'),
    url(r'^experiences/fieldwork/(?P<exp_id>[0-9]+)/$',
        FieldworkExperiencesWriteOnly.as_view(), name='fieldwork_experience'),
]
