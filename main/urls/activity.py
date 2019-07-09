from django.conf.urls import url

from main.views.search import SearchActivity
from ..views.activity import *
from ..views.common import ActivityCommentList, ActivityComment, \
    ActivityFollowerList

urls = [
    # 暂时保留这个接口，后期变更为创建活动
    url(r'^$', SearchActivity.as_view(), name='list'),
    url(r'^(?P<activity_id>[0-9]+)/$', Detail.as_view(), name='detail'),
    url(r'^(?P<activity_id>[0-9]+)/user_participators/$',
        UserParticipatorList.as_view(), name='user_participators'),
    url(r'^(?P<activity_id>[0-9]+)/comments/$',
        ActivityCommentList.as_view(), name='comments'),
    url(r'^comments/(?P<comment_id>[0-9]+)/$',
        ActivityComment.as_view(), name='comment'),
    # 搜索
    url(r'^search/$', SearchActivity.as_view(), name='search'),
    # 筛选
    url(r'^screen/$', Screen.as_view(), name='screen'),
    # 活动的阶段
    url(r'^stage/$', ActivityStage.as_view(), name='stage'),
    # 粉丝
    url(r'^(?P<activity_id>[0-9]+)/followers/$',
        ActivityFollowerList.as_view(), name='followers'),
    url(r'^(?P<activity_id>[0-9]+)/sign/$', ActivitySignList.as_view(), name='sign'),
]
