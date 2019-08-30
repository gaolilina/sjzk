from django.conf.urls import url

from main.views.activity.user_activity import FollowedActivityList, FollowedActivity
from main.views.follow.competition import FollowedCompetitionList, FollowedCompetition
from main.views.follow.user import UserFollowerList, FollowedUserList, FollowedUser
from main.views.follow.need import FollowedTeamNeedList, FollowedTeamNeed
from main.views.follow.team import FollowedTeamList, FollowedTeam

urls = [
    # 关注
    url(r'^followers/$', UserFollowerList.as_view()),
    url(r'^followed/users/$', FollowedUserList.as_view()),
    url(r'^followed/users/(?P<user_id>[0-9]+)/$', FollowedUser.as_view()),
    url(r'^followed/teams/$', FollowedTeamList.as_view()),
    url(r'^followed/teams/(?P<team_id>[0-9]+)/$', FollowedTeam.as_view()),
    url(r'^followed/needs/$', FollowedTeamNeedList.as_view()),
    url(r'^followed/needs/(?P<need_id>[0-9]+)/$', FollowedTeamNeed.as_view()),
    url(r'^followed/activities/$', FollowedActivityList.as_view()),
    url(r'^followed/activities/(?P<activity_id>[0-9]+)/$', FollowedActivity.as_view()),
    url(r'^followed/competitions/$', FollowedCompetitionList.as_view()),
    url(r'^followed/competitions/(?P<competition_id>[0-9]+)/$', FollowedCompetition.as_view()),
]
