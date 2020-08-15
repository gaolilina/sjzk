from django.conf.urls import url

from main.views.action.user import FollowedUserActionList, UserActionList, FriendActionList
from main.views.search.action import SearchUserAction, SearchTeamAction
from main.views.action.team import FollowedTeamActionList

urlpatterns = [
    # 动态
    url(r'^user_actions/$', SearchUserAction.as_view()),
    url(r'^team_actions/$', SearchTeamAction.as_view()),
    url(r'^owned_actions/$', UserActionList.as_view()),
    url(r'^followed_user/actions/$', FollowedUserActionList.as_view()),
    url(r'^friend/actions/$', FriendActionList.as_view()),
    url(r'^followed_team/actions/$', FollowedTeamActionList.as_view()),
]
