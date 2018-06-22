from django.conf.urls import url

from ..views.topic import *
#from ..views.common import TopicCommentList, TopicComment, \
#    TopicFollowerList


urls = [
    url(r'^$', List.as_view(), name='list'),
    url(r'^(?P<topic_id>[0-9]+)/$', Detail.as_view(), name='detail'),
    url(r'^(?P<topic_id>[0-9]+)/user_participators/$',
        UserParticipatorList.as_view(), name='user_participators'),
    #url(r'^(?P<topic_id>[0-9]+)/comments/$',
    #    TopicCommentList.as_view(), name='comments'),
    #url(r'^comments/(?P<comment_id>[0-9]+)/$',
    #    TopicComment.as_view(), name='comment'),
    # 搜索
    url(r'^search/$', Search.as_view(), name='search'),
    # 筛选
    url(r'^screen/$', Screen.as_view(), name='screen'),
    # 活动的阶段
    url(r'^stage/$', TopicStage.as_view(), name='stage'),
    # 粉丝
    #url(r'^(?P<topic_id>[0-9]+)/followers/$',
    #    TopicFollowerList.as_view(), name='followers'),
]
