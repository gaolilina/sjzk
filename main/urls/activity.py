from django.conf.urls import url

from ..views.activity import *
from ..views.common import ActivityCommentList, ActivityComment


urls = [
    url(r'^$', List.as_view(), name='list'),
    url(r'^(?P<activity_id>[0-9]+)/$', Detail.as_view(), name='detail'),
    url(r'^(?P<activity_id>[0-9]+)/user_participators/$',
        UserParticipatorList.as_view(), name='user_participators'),
    url(r'^(?P<activity_id>[0-9]+)/comments/$',
        ActivityCommentList.as_view(), name='comments'),
    url(r'^comments/(?P<comment_id>[0-9]+)/$',
        ActivityComment.as_view(), name='comment'),
]