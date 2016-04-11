from django.conf.urls import url

from . import views

urls = [  # /user/
    url(r'^$', views.user, name='root'),
    url(r'^total/$', views.user_total, name='total'),
    url(r'^token/$', views.user_token, name='token'),
    url(r'^username/$', views.user_username, name='username'),
    url(r'^password/$', views.user_password, name='password'),
    url(r'^profile/$', views.user_profile, name='profile'),
    url(r'^profile/(?P<user_id>[0-9]+)/$',
        views.user_profile, name='profile_id'),
    url(r'^identification/$', views.user_identification,
        name='identification'),
    url(r'^identification/verification/$',
        views.user_identification_verification,
        name='identification_verification'),
    url(r'^student_identification/$', views.user_student_identification,
        name='student_identification'),
    url(r'^student_identification/(?P<user_id>[0-9]+)/$',
        views.user_student_identification,
        name='student_identification_id'),
]
