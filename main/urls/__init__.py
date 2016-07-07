# ChuangYi URL Configuration
# https://docs.djangoproject.com/en/1.9/topics/http/urls/
from django.conf.urls import url, include
from django.conf.urls.static import static

from ChuangYi import settings
from . import self, users, team, forum

urlpatterns = [
    url(r'^self/', include(self.urls, namespace='self')),
    url(r'^users/', include(users.urls, namespace='user')),
    url(r'^team/', include(team.urls, namespace='team')),
    url(r'^forum/', include(forum.urls, namespace='forum')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
