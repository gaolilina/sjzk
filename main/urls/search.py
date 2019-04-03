#!usr/bin/env python3
# -*- coding:utf-8 _*-
from django.conf.urls import url

from main.views.search import SearchUser, SearchUserActionList, SearchTeamActionList, SearchLabActionList

urls = [
    # 搜索
    url(r'^search/user/$', SearchUser.as_view(), name='search'),
    url(r'^search/user_action/$', SearchUserActionList.as_view(), name='search_user_action'),
    url(r'^search/team_action/$', SearchTeamActionList.as_view(), name='search_team_action'),
    url(r'^search/lab_action/$', SearchLabActionList.as_view(), name='search_lab_action'),
]
