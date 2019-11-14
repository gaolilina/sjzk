from django.conf.urls import url

from main.views.like.action import LikedUserAction, LikedTeamAction, LikedSystemAction
from main.views.like.activity import LikedActivity
from main.views.like.comment import ILikeTeamComment, ILikeUserComment, ILikeActivityComment, ILikeCompetitionComment, \
    ILikeUserActionComment, ILikeTeamActionComment
from main.views.like.competition import LikedCompetition
from main.views.like.tag import LikedUserTag, LikedTeamTag
from main.views.like.team import LikedTeam
from main.views.like.user import LikedUser, ILikeUserExperience

urlpatterns = [
    # 我点赞用户
    url(r'^user/(?P<user_id>[0-9]+)/$', LikedUser.as_view()),
    # 我点赞团队
    url(r'^team/(?P<team_id>[0-9]+)/$', LikedTeam.as_view()),
    # 我点赞活动
    url(r'^activity/(?P<activity_id>[0-9]+)/$', LikedActivity.as_view()),
    # 我点赞竞赛
    url(r'^competition/(?P<competition_id>[0-9]+)/$', LikedCompetition.as_view()),
    # 我点赞用户动态
    url(r'^action/user/(?P<action_id>[0-9]+)/$', LikedUserAction.as_view()),
    # 我点赞团队动态
    url(r'^action/team/(?P<action_id>[0-9]+)/$', LikedTeamAction.as_view()),
    # 我点赞系统动态
    url(r'^action/system/(?P<action_id>[0-9]+)/$', LikedSystemAction.as_view()),
    # 我点赞用户标签
    url(r'^tag/user/(?P<tag_id>.+?)/$', LikedUserTag.as_view()),
    # 我点赞团队标签
    url(r'^tag/team/(?P<tag_id>.+?)/$', LikedTeamTag.as_view()),
    # 我点赞团队评论
    url(r'^comment_team/(?P<comment_id>.+?)/$', ILikeTeamComment.as_view()),
    # 我点赞用户评论
    url(r'^comment_user/(?P<comment_id>.+?)/$', ILikeUserComment.as_view()),
    # 我点赞活动评论
    url(r'^comment_activity/(?P<comment_id>.+?)/$', ILikeActivityComment.as_view()),
    # 我点赞竞赛评论
    url(r'^comment_competition/(?P<comment_id>.+?)/$', ILikeCompetitionComment.as_view()),
    # 我点赞用户动态评论
    url(r'^comment_user_action/(?P<comment_id>.+?)/$', ILikeUserActionComment.as_view()),
    # 我点赞团队评论
    url(r'^comment_team_action/(?P<comment_id>.+?)/$', ILikeTeamActionComment.as_view()),
    # 我点赞用户经历
    url(r'^experience/(?P<experience_id>.+?)/$', ILikeUserExperience.as_view()),
]
