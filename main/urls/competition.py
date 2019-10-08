from django.conf.urls import url

from main.views.competition.award import CompetitionAwardList
from main.views.search.competition import SearchCompetition
from ..views.competition import *
from ..views.common import CompetitionComment, CompetitionFollowerList
from main.views.competition.comment import CompetitionCommentList

urls = [
    # 暂时保留这个接口，后期变更为创建竞赛
    url(r'^$', SearchCompetition.as_view(), name='list'),
    # 搜索，筛选，后期要删掉，已经迁移到 /search/ 接口中
    url(r'^search/$', SearchCompetition.as_view(), name='search'),
    url(r'^screen/$', Screen.as_view(), name='screen'),

    url(r'^(?P<competition_id>[0-9]+)/$', Detail.as_view(), name='detail'),
    url(r'^(?P<competition_id>[0-9]+)/team_participators/$', TeamParticipatorList.as_view()),
    url(r'^(?P<competition_id>[0-9]+)/comments/$', CompetitionCommentList.as_view()),
    url(r'^comments/(?P<comment_id>[0-9]+)/$', CompetitionComment.as_view()),
    # 竞赛的阶段
    url(r'^(?P<competition_id>[0-9]+)/stage/$', CompetitionStageList.as_view()),
    # 竞赛的评比列表，获奖名单
    url(r'^(?P<competition_id>[0-9]+)/awards/$', CompetitionAwardList.as_view()),
    # 竞赛的通知
    url(r'^(?P<competition_id>[0-9]+)/notifications/$', CompetitionNotification.as_view()),
    # 竞赛的文件
    url(r'^(?P<competition_id>[0-9]+)/files/$', CompetitionFileList.as_view()),
    # 竞赛文件上传
    url(r'(?P<team_id>[0-9]+)/files/$', CompetitionFile.as_view(), name='files'),
    url(r'(?P<team_id>[0-9]+)/file/(?P<competition_id>[0-9]+)/$', CompetitionFile.as_view()),
    url(r'(?P<team_id>[0-9]+)/file/(?P<competition_id>[0-9]+)/expert/$', CompetitionFileExpert.as_view()),
    # 评委打分
    url(r'file/(?P<file_id>[0-9]+)/score/$', CompetitionFileScore.as_view()),
    url(r'team/(?P<team_participator_id>[0-9]+)/score/$', CompetitionTeamScore.as_view()),
    # 粉丝
    url(r'^(?P<competition_id>[0-9]+)/followers/$', CompetitionFollowerList.as_view()),
    url(r'^(?P<competition_id>[0-9]+)/experts/$', CompetitionExpertList.as_view()),
    url(r'^(?P<competition_id>[0-9]+)/sign/$', CompetitionSignList.as_view()),
]
