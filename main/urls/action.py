from django.conf.urls import url

from main.views.action import UserActionsList, TeamActionsList, LabActionsList

urls = [
    # 用户动态
    url(r'^user/$', UserActionsList.as_view(), name='user'),
    url(r'^team/$', TeamActionsList.as_view(), name='team'),
    url(r'^lab/$', LabActionsList.as_view(), name='lab'),
]
