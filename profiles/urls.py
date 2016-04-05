from django.conf.urls import url, include

from profiles import views

user_urlpatterns = [  # namespace: user:profile
    url(r'^$', views.user_profile, name='root'),
    url(r'^(?P<user_id>[0-9]+)/$', views.user_profile, name='id'),
    url(r'^identification/$', views.user_profile_identification,
        name='identification'),
    url(r'^identification/verification/$',
        views.user_profile_identification_verification,
        name='identification_verification'),
    url(r'^student_identification/$', views.user_profile_student_identification,
        name='student_identification'),
]

user_urls = [url(r'^profile/', include(user_urlpatterns, namespace='profile'))]
