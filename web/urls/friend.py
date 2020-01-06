from django.conf.urls import url

from web.views.friend import FriendRequestList

urlpatterns = [
    url(r'^request/$', FriendRequestList.as_view()),
]
