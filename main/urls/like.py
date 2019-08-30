from django.conf.urls import url

from main.views.activity.user_activity import LikedActivity
from main.views.like.action import LikedUserAction, LikedTeamAction, LikedSystemAction
from main.views.like.competition import LikedCompetition
from main.views.like.tag import LikedUserTag, LikedTeamTag
from main.views.like.team import LikedTeam
from main.views.like.user import LikedUser, UserLikerList, UserLiker

urls = [
    # 点赞
    url(r'likers/$', UserLikerList.as_view()),
    url(r'likers/(?P<other_user_id>[0-9]+)/$', UserLiker.as_view()),
    url(r'liked/users/(?P<user_id>[0-9]+)/$', LikedUser.as_view()),
    url(r'liked/teams/(?P<team_id>[0-9]+)/$', LikedTeam.as_view()),
    url(r'liked/activities/(?P<activity_id>[0-9]+)/$', LikedActivity.as_view()),
    url(r'liked/competitions/(?P<competition_id>[0-9]+)/$', LikedCompetition.as_view()),
    url(r'liked/user_actions/(?P<action_id>[0-9]+)/$', LikedUserAction.as_view()),
    url(r'liked/team_actions/(?P<action_id>[0-9]+)/$', LikedTeamAction.as_view()),
    url(r'liked/system_actions/(?P<action_id>[0-9]+)/$', LikedSystemAction.as_view()),
    url(r'liked/user_tags/(?P<tag_id>.+?)/$', LikedUserTag.as_view()),
    url(r'liked/team_tags/(?P<tag_id>.+?)/$', LikedTeamTag.as_view()),

]
