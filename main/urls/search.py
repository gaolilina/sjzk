#!usr/bin/env python3
# -*- coding:utf-8 _*-
from django.conf.urls import url

from main.views.search import SearchUser, SearchActivity, SearchCompetition, SearchTeam
from main.views.search.achievement import SearchUserAchievement, SearchTeamAchievement, SearchAllTeamAchievement, SearchAllUserAchievement
from main.views.search.action import SearchUserAction, SearchTeamAction, SearchLabAction
from main.views.search.need import NeedSearch

urlpatterns = [
    # 搜索
    url(r'^user/$', SearchUser.as_view()),
    url(r'^team/$', SearchTeam.as_view()),
    url(r'^activity/$', SearchActivity.as_view()),
    url(r'^competition/$', SearchCompetition.as_view()),
    url(r'^achievement/$', SearchAllUserAchievement.as_view()),
    url(r'^achievement/team/$', SearchAllTeamAchievement.as_view()),
    url(r'^(?P<user_id>[0-9]+)/achievement/$', SearchUserAchievement.as_view()),
    url(r'^(?P<team_id>[0-9]+)/achievement/team/$', SearchTeamAchievement.as_view()),

    url(r'^action/user/$', SearchUserAction.as_view(), name='user'),
    url(r'^action/team/$', SearchTeamAction.as_view(), name='team'),
    url(r'^user_action/$', SearchUserAction.as_view()),
    url(r'^team_action/$', SearchTeamAction.as_view()),
    url(r'^need/$', NeedSearch.as_view()),

    ##########################弃用
    url(r'^lab_action/$', SearchLabAction.as_view()),
    url(r'^action/lab/$', SearchLabAction.as_view(), name='lab'),
]
