# ChuangYi URL Configuration
# https://docs.djangoproject.com/en/1.9/topics/http/urls/

from django.conf.urls import url, include

import user.views

user_urls = [
    url(r'^$', user.views.user_root, name='root'),
    url(r'^total/', user.views.user_total, name='total'),
    url(r'^token/', user.views.user_token, name='token'),
    url(r'^username/', user.views.user_username, name='username'),
    url(r'^password/', user.views.user_password, name='password'),
    url(r'^id/', user.views.user_id, name='id'),
]

urlpatterns = [
    url(r'^user/', include(user_urls, namespace='user')),
]
