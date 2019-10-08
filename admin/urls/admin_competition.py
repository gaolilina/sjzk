from django.conf.urls import url

from admin.views.competition import CompetitionTeamList
from admin.views.competition.award import AdminCompetitionAwardEdit
from admin.views.competition.create_edit import AdminCompetitionAdd, AdminCompetitionEdit
from admin.views.competition.expert import CompetitionExpertList, CompetitionAddExpert
from admin.views.competition.file import AdminCompetitionFilesView, AdminCompetitionExcelView, CompetitionFileExpert
from admin.views.competition.list_detail import AdminCompetitionList, AdminCompetitionView
from admin.views.competition.promote import CompetitionTeamFinal

urls = [
    # 列表和详情
    url(r'^list$', AdminCompetitionList.as_view(), name='list'),
    url(r'^view/(?P<id>\w+)$', AdminCompetitionView.as_view(), name='view'),
    # 创建和编辑
    url(r'^add$', AdminCompetitionAdd.as_view(), name='add'),
    url(r'^edit/(?P<id>\w+)$', AdminCompetitionEdit.as_view(), name='edit'),
    # 查看竞赛某阶段的文件列表
    url(r'^view/(?P<id>\w+)/files/(?P<status>\w+)$', AdminCompetitionFilesView.as_view(), name='file'),
    # 导出 excel
    url(r'^view/(?P<id>\w+)/excel.csv$', AdminCompetitionExcelView.as_view(), name='excel'),
    # 竞赛专家
    url(r'^(?P<competition_id>[0-9]+)/experts/$', CompetitionExpertList.as_view()),
    url(r'^(?P<competition_id>[0-9]+)/addexperts/$', CompetitionAddExpert.as_view()),
    # 参赛团队
    url(r'^(?P<competition_id>[0-9]+)/team/$', CompetitionTeamList.as_view()),
    # 淘汰团队
    url(r'^(?P<competition_id>[0-9]+)/final/$', CompetitionTeamFinal.as_view()),
    # 设置中奖名单
    url(r'^award/(?P<id>\w+)$', AdminCompetitionAwardEdit.as_view(), name='award'),

    # 弃用
    url(r'(?P<team_id>[0-9]+)/file/(?P<competition_id>[0-9]+)/expert/$', CompetitionFileExpert.as_view()),
]
