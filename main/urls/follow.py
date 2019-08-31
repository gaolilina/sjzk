from django.conf.urls import url

from main.views.follow.activity import FollowedActivity, FollowedActivityList
from main.views.follow.competition import FollowedCompetitionList, FollowedCompetition
from main.views.follow.need import FollowedTeamNeedList, FollowedTeamNeed
from main.views.follow.team import FollowedTeamList, FollowedTeam
from main.views.follow.user import FollowedUserList, FollowedUser

urlpatterns = [
    # 我关注的用户
    url(r'^users/$', FollowedUserList.as_view()),
    url(r'^users/(?P<user_id>[0-9]+)/$', FollowedUser.as_view()),
    # 我关注的团队
    url(r'^teams/$', FollowedTeamList.as_view()),
    url(r'^teams/(?P<team_id>[0-9]+)/$', FollowedTeam.as_view()),
    # 我关注的需求
    url(r'^needs/$', FollowedTeamNeedList.as_view()),
    url(r'^needs/(?P<need_id>[0-9]+)/$', FollowedTeamNeed.as_view()),
    # 我关注的活动
    url(r'^activities/$', FollowedActivityList.as_view()),
    url(r'^activities/(?P<activity_id>[0-9]+)/$', FollowedActivity.as_view()),
    # 我关注的竞赛
    url(r'^competitions/$', FollowedCompetitionList.as_view()),
    url(r'^competitions/(?P<competition_id>[0-9]+)/$', FollowedCompetition.as_view()),
]
