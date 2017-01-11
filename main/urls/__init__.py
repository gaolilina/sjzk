from django.conf.urls import url, include

from . import user, current_user, team, forum, activity, competition, system
from admin.urls import urlpatterns as admin_urls

urlpatterns = [
    url(r'^admin/', include(admin_urls, namespace='admin')),
    url(r'^users/', include(user.urls, namespace='user')),
    url(r'^users/current/', include(current_user.urls, namespace='current_user')),
    url(r'^teams/', include(team.urls, namespace='team')),
    url(r'^forum/', include(forum.urls, namespace='forum')),
    url(r'^activity/', include(activity.urls, namespace='activity')),
    url(r'^competition/', include(competition.urls, namespace='competition')),
    url(r'^system/', include(system.urls, namespace='system')),
]
