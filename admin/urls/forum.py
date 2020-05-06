# Auto generated by forum.py
from django.conf.urls import url

from admin.views.forum import *

urls = [
    url(r'^forum_board/list/(?P<id>\w+)?$', ForumBoardList.as_view(), name='forum_board_list'),
    url(r'^forum_board/(?P<id>\w+)$', ForumBoardView.as_view(), name='forum_board'),
    url(r'^forum_post/list/(?P<id>\w+)?$', ForumPostList.as_view(), name='forum_post_list'),
    url(r'^forum_post/(?P<id>\w+)$', ForumPostView.as_view(), name='forum_post'),
]
