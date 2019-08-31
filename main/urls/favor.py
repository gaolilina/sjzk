from django.conf.urls import url

from main.views.favor.action_system import FavoredSystemActionList, FavoredSystemAction
from main.views.favor.action_team import FavoredTeamActionList, FavoredTeamAction
from main.views.favor.action_user import FavoredUserActionList, FavoredUserAction
from main.views.favor.activity import FavoredActivityList, FavoredActivity
from main.views.favor.competition import FavoredCompetitionList, FavoredCompetition
from main.views.lab import FavoredLabAction, FavoredLabActionList

urlpatterns = [
    # 我收藏的活动
    url(r'^activities/$', FavoredActivityList.as_view()),
    url(r'^activities/(?P<activity_id>[0-9]+)/$', FavoredActivity.as_view()),
    # 我收藏的竞赛
    url(r'^competitions/$', FavoredCompetitionList.as_view()),
    url(r'^competitions/(?P<competition_id>[0-9]+)/$', FavoredCompetition.as_view()),
    # 我收藏的用户动态
    url(r'^user_actions/$', FavoredUserActionList.as_view()),
    url(r'^user_actions/(?P<action_id>[0-9]+)/$', FavoredUserAction.as_view()),
    # 我收藏的团队动态
    url(r'^team_actions/$', FavoredTeamActionList.as_view()),
    url(r'^team_actions/(?P<action_id>[0-9]+)/$', FavoredTeamAction.as_view()),
    # 我收藏的系统动态
    url(r'^system_actions/$', FavoredSystemActionList.as_view()),
    url(r'^system_actions/(?P<action_id>[0-9]+)/$', FavoredSystemAction.as_view()),

    ####################################弃用
    url(r'^lab_actions/(?P<action_id>[0-9]+)/$', FavoredLabAction.as_view()),
    url(r'^lab_actions/$', FavoredLabActionList.as_view()),
]
