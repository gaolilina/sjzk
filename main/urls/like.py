from django.conf.urls import url

from main.views.like.action import LikedUserAction, LikedTeamAction, LikedSystemAction
from main.views.like.activity import LikedActivity
from main.views.like.competition import LikedCompetition
from main.views.like.tag import LikedUserTag, LikedTeamTag
from main.views.like.team import LikedTeam
from main.views.like.user import LikedUser

urlpatterns = [
    # 我点赞的用户
    url(r'user/(?P<user_id>[0-9]+)/$', LikedUser.as_view()),
    # 我点赞的团队
    url(r'team/(?P<team_id>[0-9]+)/$', LikedTeam.as_view()),
    # 我点赞的活动
    url(r'activity/(?P<activity_id>[0-9]+)/$', LikedActivity.as_view()),
    # 我点赞的竞赛
    url(r'competition/(?P<competition_id>[0-9]+)/$', LikedCompetition.as_view()),
    # 我点赞的用户动态
    url(r'action/user/(?P<action_id>[0-9]+)/$', LikedUserAction.as_view()),
    # 我点赞团队动态
    url(r'action/team/(?P<action_id>[0-9]+)/$', LikedTeamAction.as_view()),
    # 我点赞系统动态
    url(r'action/system/(?P<action_id>[0-9]+)/$', LikedSystemAction.as_view()),
    # 我点赞用户标签
    url(r'tag/user/(?P<tag_id>.+?)/$', LikedUserTag.as_view()),
    # 我点赞团队标签
    url(r'tag/team/(?P<tag_id>.+?)/$', LikedTeamTag.as_view()),
]
