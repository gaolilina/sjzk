# ChuangYi URL Configuration
# https://docs.djangoproject.com/en/1.9/topics/http/urls/

from django.conf.urls import url, include

urlpatterns = [
    url(r'^user/', include('user.urls', namespace='user')),
]
