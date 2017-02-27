from django.conf.urls import url

from ..views.competition import *
from ..views.common import CompetitionCommentList, CompetitionComment


urls = [
    url(r'^$', List.as_view(), name='list'),
    url(r'^(?P<competition_id>[0-9]+)/$', Detail.as_view(), name='detail'),
    url(r'^(?P<competition_id>[0-9]+)/team_participators/$',
        TeamParticipatorList.as_view(), name='team_participators'),
    url(r'^(?P<competition_id>[0-9]+)/comments/$',
        CompetitionCommentList.as_view(), name='comments'),
    url(r'^comments/(?P<comment_id>[0-9]+)/$',
        CompetitionComment.as_view(), name='comment'),
    # 搜索
    url(r'^search/$', Search.as_view(), name='search'),
    # 筛选
    url(r'^screen/$', Screen.as_view(), name='screen'),
    # 竞赛的阶段
    url(r'^(?P<competition_id>[0-9]+)/stage/$',
        CompetitionStage.as_view(), name='stage'),
    # 竞赛的通知
    url(r'^(?P<competition_id>[0-9]+)/notifications/$',
        CompetitionNotification.as_view(), name='notifications'),
    # 竞赛文件上传
    url(r'(?P<team_id>[0-9]+)/files/$', CompetitionFile.as_view(), name='files'),
    url(r'(?P<team_id>[0-9]+)/file/(?P<competition_id>[0-9]+)/$',
        CompetitionFile.as_view(), name='file'),
]
