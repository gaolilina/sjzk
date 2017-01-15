from django.conf.urls import url

from ..views.forum import *

urls = [
    url(r'^boards/$', BoardList.as_view(), name='boards'),
    url(r'^boards/(?P<board_id>[0-9]+)/$', Board.as_view(), name='board'),
    url(r'^boards/(?P<board_id>[0-9]+)/posts/$', PostList.as_view(),
        name='posts'),
    url(r'^posts/(?P<post_id>[0-9]+)/$', Post.as_view(), name='post'),
    # 搜索
    url(r'^search_board/$', SearchBoard.as_view(), name='search_board'),
    url(r'^(?P<board_id>[0-9]+)/search_post/$',
        SearchPost.as_view(), name='search_post'),
]
