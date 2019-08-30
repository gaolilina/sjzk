from django.conf.urls import url

from main.views.favor.action_system import FavoredSystemActionList, FavoredSystemAction
from main.views.favor.action_team import FavoredTeamActionList, FavoredTeamAction
from main.views.favor.action_user import FavoredUserActionList, FavoredUserAction
from main.views.favor.activity import FavoredActivityList, FavoredActivity
from main.views.favor.competition import FavoredCompetitionList, FavoredCompetition
from main.views.lab import FavoredLabAction, FavoredLabActionList

urls = [
    # 收藏
    url(r'^favored/activities/$', FavoredActivityList.as_view()),
    url(r'^favored/competitions/$', FavoredCompetitionList.as_view()),
    url(r'^favored/user_actions/$', FavoredUserActionList.as_view()),
    url(r'^favored/team_actions/$', FavoredTeamActionList.as_view()),
    url(r'^favored/system_actions/$', FavoredSystemActionList.as_view()),
    url(r'^favored/activities/(?P<activity_id>[0-9]+)/$', FavoredActivity.as_view()),
    url(r'^favored/competitions/(?P<competition_id>[0-9]+)/$', FavoredCompetition.as_view()),
    url(r'^favored/user_actions/(?P<action_id>[0-9]+)/$', FavoredUserAction.as_view()),
    url(r'^favored/team_actions/(?P<action_id>[0-9]+)/$', FavoredTeamAction.as_view()),
    url(r'^favored/system_actions/(?P<action_id>[0-9]+)/$', FavoredSystemAction.as_view()),

    ####################################弃用
    url(r'^favored/lab_actions/(?P<action_id>[0-9]+)/$', FavoredLabAction.as_view()),
    url(r'^favored/lab_actions/$', FavoredLabActionList.as_view()),
]
