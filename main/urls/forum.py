from django.conf.urls import url

from main.views.forum import Boards, BoardSelf, Posts, PostSelf

urls = [
    # 获取所有的版块(get)
    url(r'^boards/$', Boards.as_view(), name='boards'),
    # 获取自己创建的所有版块(get)/创建版块(post)/删除版块(delete)
    url(r'^board/$', BoardSelf.as_view(), name='board'),
    # 获取当前版块下所有的帖子(get)
    url(r'^(?P<board_id>[0-9]+)/posts/$', Posts.as_view(), name='posts'),
    # 获取自己发布的所有帖子(get)
    url(r'^posts/$', PostSelf.as_view(), name='posts_self'),
    # 创建帖子(post)
    url(r'^(?P<board_id>[0-9]+)/post/$', BoardSelf.as_view(), name='post'),
    # 删除帖子(delete)
    url(r'^(?P<board_id>[0-9]+)/post/(?P<post_id>[0-9]+)/$',
        BoardSelf.as_view(), name='post_delete'),
]
