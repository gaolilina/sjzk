from django.conf.urls import url, include

from . import user, current_user, team, forum, activity

urlpatterns = [
    url(r'^users/', include(user.urls, namespace='user')),
    url(r'^users/current/', include(current_user.urls, namespace='current_user')),
    url(r'^teams/', include(team.urls, namespace='team')),
    url(r'^forum/', include(forum.urls, namespace='forum')),
    url(r'^activity/', include(activity.urls, namespace='activity')),
]
