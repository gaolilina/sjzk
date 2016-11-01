from django.conf.urls import url

from admin.views.admin_competition import *

urls = [
    url(r'^add$', AdminCompetitionAdd.as_view(), name='add'),
    url(r'^view/(?P<id>\w+)$', AdminCompetitionView.as_view(), name='view'),
    url(r'^list$', AdminCompetitionList.as_view(), name='list'),
]
