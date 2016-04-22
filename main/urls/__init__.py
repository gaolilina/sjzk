# ChuangYi URL Configuration
# https://docs.djangoproject.com/en/1.9/topics/http/urls/
from django.conf.urls import url, include

from . import self, users

urlpatterns = [
    url(r'^self/', include(self.urls, namespace='self')),
    url(r'^users/', include(users.urls, namespace='user')),
]
