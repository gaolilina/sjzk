# ChuangYi URL Configuration
# https://docs.djangoproject.com/en/1.9/topics/http/urls/

from django.conf.urls import url, include

import profiles.views
import user.views

user_urls = [
    url(r'^$', user.views.user_root, name='root'),
    url(r'^total/$', user.views.user_total, name='total'),
    url(r'^token/$', user.views.user_token, name='token'),
    url(r'^username/$', user.views.user_username, name='username'),
    url(r'^password/$', user.views.user_password, name='password'),
    url(r'^profile/$', profiles.views.user_profile, name='profile'),
    url(r'^profile/(?P<user_id>[0-9]+)/$', profiles.views.user_profile,
        name='profile_'),
]

urlpatterns = [
    url(r'^user/', include(user_urls, namespace='user')),
]
