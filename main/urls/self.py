from django.conf.urls import url

from main.views.user import Username, Password, ProfileSelf, IdentificationSelf
from main.views.user.experience import EducationExperiencesSelf, \
    WorkExperiencesSelf, FieldworkExperiencesSelf, EducationExperience, \
    WorkExperience, FieldworkExperience

urls = [
    url(r'^username/$', Username.as_view(), name='username'),
    url(r'^password/$', Password.as_view(), name='password'),
    url(r'^profile/$', ProfileSelf.as_view(), name='profile'),
    url(r'^identification/$',
        IdentificationSelf.as_view(), name='identification'),
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
]
