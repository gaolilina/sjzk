# ChuangYi URL Configuration
# https://docs.djangoproject.com/en/1.9/topics/http/urls/

from django.conf.urls import url, include

import user.urls
import profiles.urls

user_urls = user.urls.urls + profiles.urls.user_urls

urlpatterns = [
    url(r'^user/', include(user_urls, namespace='user')),
]
