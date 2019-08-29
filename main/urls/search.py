#!usr/bin/env python3
# -*- coding:utf-8 _*-
from django.conf.urls import url, include

from main.urls import action
from main.views.search import SearchUser, SearchActivity, SearchCompetition, SearchTeam
from main.views.search.achievement import SearchUserAchievement, SearchTeamAchievement
from main.views.search.action import SearchUserAction, SearchTeamAction, SearchLabAction
from main.views.search.need import NeedSearch

urlpatterns = [
    # 搜索
    url(r'^user/$', SearchUser.as_view()),
    url(r'^team/$', SearchTeam.as_view()),
    url(r'^activity/$', SearchActivity.as_view()),
    url(r'^competition/$', SearchCompetition.as_view()),
    url(r'^achievement/$', SearchUserAchievement.as_view()),
    url(r'^achievement/team/$', SearchTeamAchievement.as_view()),

    url(r'^action/', include(action.urlpatterns)),
    url(r'^user_action/$', SearchUserAction.as_view()),
    url(r'^team_action/$', SearchTeamAction.as_view()),
    url(r'^lab_action/$', SearchLabAction.as_view()),
    url(r'^need/$', NeedSearch.as_view()),
]
