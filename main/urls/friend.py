#!usr/bin/env python3
# -*- coding:utf-8 _*-
from django.conf.urls import url

from main.views.friend import MyFriendList, FriendAction
from main.views.friend.request import FriendRequestList, FriendRequestAction

urls = [
    # 好友列表
    url(r'^$', MyFriendList.as_view()),
    # 添加，删除好友
    url(r'^(?P<other_user_id>[0-9]+)/$', FriendAction.as_view()),
    # 好友请求列表，发送好友请求
    url(r'^request/$', FriendRequestList.as_view()),
    # 拒绝好友请求
    url(r'^request/(?P<req_id>[0-9]+)/$', FriendRequestAction.as_view()),
]
