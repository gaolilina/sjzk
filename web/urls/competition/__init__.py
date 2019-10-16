from django.conf.urls import url

from web.views.competition.for_expert import RatingFileListInCompetition, MyRatingCompetition
from web.views.competition.for_user import MyJoinedCompetition, UploadFileForTeamInCompetition
from web.views.competition.score import RatingFile

urlpatterns = [
    # 竞赛参与者
    # 我参加的竞赛
    url(r'^joined/$', MyJoinedCompetition.as_view()),
    # 上传文件
    url(r'^(?P<competition_id>\d+)/file/team/(?P<team_id>\d+)/$', UploadFileForTeamInCompetition.as_view()),

    # 竞赛专家
    # 我评分的竞赛
    url(r'^rating/$', MyRatingCompetition.as_view()),
    # 我评分的文件
    url(r'^(?P<competition_id>\d+)/ratefile/$', RatingFileListInCompetition.as_view()),
    # 评分文件
    url(r'^score/file/(?P<file_id>\d+)/$', RatingFile.as_view()),
]
