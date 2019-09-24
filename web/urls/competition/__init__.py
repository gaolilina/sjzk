from django.conf.urls import url

from web.views.competition.file import TeamFile, ExpertRateFile
from web.views.competition.list import MyJoinedCompetition
from web.views.competition.score import FileScore

urlpatterns = [
    url(r'^joined/$', MyJoinedCompetition.as_view()),
    url(r'^(?P<competition_id>\d+)/ratefile/$', ExpertRateFile.as_view()),
    url(r'^(?P<competition_id>\d+)/file/team/(?P<team_id>\d+)/$', TeamFile.as_view()),

    url(r'^score/file/(?P<file_id>\d+)/$', FileScore.as_view()),
]
