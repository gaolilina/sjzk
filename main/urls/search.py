#!usr/bin/env python3
# -*- coding:utf-8 _*-
from django.conf.urls import url

from main.views.search import SearchUser, SearchUserActionList, SearchTeamActionList, SearchLabActionList, \
    SearchActivity, SearchCompetition, SearchTeam

urls = [
    # 搜索
    url(r'^user/$', SearchUser.as_view(), name='search_user'),
    url(r'^team/$', SearchTeam.as_view(), name='search_team'),
    url(r'^user_action/$', SearchUserActionList.as_view(), name='search_user_action'),
    url(r'^team_action/$', SearchTeamActionList.as_view(), name='search_team_action'),
    url(r'^lab_action/$', SearchLabActionList.as_view(), name='search_lab_action'),
    url(r'^activity/$', SearchActivity.as_view(), name='search_activity'),
    url(r'^competition/$', SearchCompetition.as_view(), name='search_competition'),
]
