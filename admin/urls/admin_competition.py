from django.conf.urls import url

from admin.views.admin_competition import *

urls = [
    url(r'^add$', AdminCompetitionAdd.as_view(), name='add'),
    url(r'^view/(?P<id>\w+)$', AdminCompetitionView.as_view(), name='view'),
    url(r'^view/(?P<id>\w+)/files/(?P<status>\w+)$', AdminCompetitionFilesView.as_view(), name='file'),
    url(r'^edit/(?P<id>\w+)$', AdminCompetitionEdit.as_view(), name='edit'),
    url(r'^award/(?P<id>\w+)$', AdminCompetitionAwardEdit.as_view(), name='award'),
    url(r'^list$', AdminCompetitionList.as_view(), name='list'),
    url(r'^view/(?P<id>\w+)/excel.csv$', AdminCompetitionExcelView.as_view(), name='excel'),
]
