#!usr/bin/env python3
# -*- coding:utf-8 _*-
from django.conf.urls import url, include

from main.urls import action
from main.views.search import SearchUser, SearchActivity, SearchCompetition, SearchTeam
from main.views.search.action import SearchUserAction, SearchTeamAction, SearchLabAction

urlpatterns = [
    # 搜索
    url(r'^user/$', SearchUser.as_view()),
    url(r'^team/$', SearchTeam.as_view()),
    url(r'^activity/$', SearchActivity.as_view()),
    url(r'^competition/$', SearchCompetition.as_view()),

    url(r'^action/', include(action.urlpatterns)),
    url(r'^user_action/$', SearchUserAction.as_view()),
    url(r'^team_action/$', SearchTeamAction.as_view()),
    url(r'^lab_action/$', SearchLabAction.as_view()),
]
