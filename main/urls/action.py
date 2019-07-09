from django.conf.urls import url

from main.views.search.action import SearchUserAction, SearchTeamAction, SearchLabAction

urls = [
    # 用户动态
    url(r'^user/$', SearchUserAction.as_view(), name='user'),
    url(r'^team/$', SearchTeamAction.as_view(), name='team'),
    url(r'^lab/$', SearchLabAction.as_view(), name='lab'),
]
