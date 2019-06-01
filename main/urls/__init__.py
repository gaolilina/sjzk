from django.conf.urls import url, include

from main.urls import search, paper
from . import user, current_user, team, forum, activity, competition, system, lab, topic, vote, achievement, auth, \
    friend
from admin.urls import urlpatterns as admin_urls
from web.urls import urlpatterns as web_urls

urlpatterns = [
    # 这两个是导入其他工程
    url(r'^admin/', include(admin_urls, namespace='admin')),
    url(r'^web/', include(web_urls, namespace='web')),

    # 当前工程 url
    url(r'^users/', include(user.urls, namespace='user')),
    url(r'^achievement/', include(achievement.urls, namespace='achievement')),
    url(r'^users/current/', include(current_user.urls, namespace='current_user')),
    url(r'^teams/', include(team.urls, namespace='team')),
    url(r'^forum/', include(forum.urls, namespace='forum')),
    url(r'^activity/', include(activity.urls, namespace='activity')),
    url(r'^competition/', include(competition.urls, namespace='competition')),
    url(r'^system/', include(system.urls, namespace='system')),
    url(r'^labs/', include(lab.urls, namespace='lab')),
    url(r'^topic/', include(topic.urls, namespace='topic')),
    url(r'^vote/', include(vote.urls, namespace='vote')),
    url(r'^auth/', include(auth.urls, namespace='auth')),
    url(r'friend/', include(friend.urls, namespace='friend')),
    url(r'search/', include(search.urls, namespace='search')),
    url(r'paper/', include(paper.urls, namespace='paper')),
]
