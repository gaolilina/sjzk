from django.conf.urls import url

from main.views.friend import FriendCheck, MyFriendList
from main.views.friend.request import FriendRequestList
from main.views.action import ScreenUserActionList
from main.views.action.user import UserActionList
from main.views.action.team import ScreenTeamActionList
from main.views.lab import ScreenLabActionList
from main.views.comment.user import UserCommentList, UserComment
from main.views.follow.user import UserFollowerList
from main.views.like.user import UserLikerList, UserLiker
from main.views.me.visit import UserVisitorList
from main.views.search import SearchUser
from main.views.search.action import SearchUserAction, SearchTeamAction, SearchLabAction
from ..views.user import *
from ..views.common import *
from ..views.recommend import UserRecommend

urls = [
    # 暂时保留这个接口，后期删除
    url(r'^$', SearchUser.as_view()),
    url(r'^search/$', SearchUser.as_view()),
    url(r'^search/user_action/$', SearchUserAction.as_view()),
    url(r'^search/team_action/$', SearchTeamAction.as_view()),
    url(r'^search/lab_action/$', SearchLabAction.as_view()),
    url(r'^screen/$', Screen.as_view()),
    url(r'^screen/user_action/$', ScreenUserActionList.as_view()),
    url(r'^screen/team_action/$', ScreenTeamActionList.as_view()),
    url(r'^screen/lab_action/$', ScreenLabActionList.as_view()),

    # 基本信息
    url(r'^(?P<user_id>[0-9]+)/icon/$', Icon.as_view()),
    url(r'^(?P<user_id>[0-9]+)/profile/$', Profile.as_view()),
    # 获取某用户的团队
    url(r'^(?P<user_id>[0-9]+)/owned_teams/$', TeamOwnedList.as_view()),
    url(r'^(?P<user_id>[0-9]+)/joined_teams/$', TeamJoinedList.as_view()),
    # 活动
    url(r'^(?P<user_id>[0-9]+)/activity/$', ActivityList.as_view()),
    # 竞赛
    url(r'^(?P<user_id>[0-9]+)/competition/$', CompetitionList.as_view()),
    url(r'^(?P<user_id>[0-9]+)/joined_competition/$', CompetitionJoinedList.as_view()),
    # 动态
    url(r'^(?P<user_id>[0-9]+)/actions/$', UserActionList.as_view()),
    # 评论
    url(r'^(?P<user_id>[0-9]+)/comments/$', UserCommentList.as_view()),
    url(r'comments/(?P<comment_id>[0-9]+)/$', UserComment.as_view()),
    # 经历
    url(r'^(?P<user_id>[0-9]+)/experiences/education/$', ExperienceList.as_view(), kwargs={'type': 'education'}),
    url(r'^(?P<user_id>[0-9]+)/experiences/work/$', ExperienceList.as_view(), kwargs={'type': 'work'}),
    url(r'^(?P<user_id>[0-9]+)/experiences/fieldwork/$', ExperienceList.as_view(), kwargs={'type': 'fieldwork'}),
    url(r'experiences/(?P<exp_id>[0-9]+)/$', Experience.as_view()),
    # 关注者
    url(r'^(?P<user_id>[0-9]+)/followers/$', UserFollowerList.as_view()),
    url(r'^(?P<user_id>[0-9]+)/followers/(?P<other_user_id>[0-9]+)/$', UserFollower.as_view()),
    # 好友
    url(r'^(?P<user_id>[0-9]+)/friends/$', MyFriendList.as_view()),
    url(r'^(?P<user_id>[0-9]+)/friends/(?P<other_user_id>[0-9]+)/$', FriendCheck.as_view()),
    url(r'^(?P<user_id>[0-9]+)/friend_requests/$', FriendRequestList.as_view()),
    # 点赞
    url(r'^(?P<user_id>[0-9]+)/likers/$', UserLikerList.as_view()),
    url(r'^(?P<user_id>[0-9]+)/likers/(?P<other_user_id>[0-9]+)/$', UserLiker.as_view()),
    # 验证码
    url(r'^validation_code/$', ValidationCode.as_view()),
    # 忘记密码
    url(r'^password_forgotten/$', PasswordForgotten.as_view()),
    # 访客
    url(r'^(?P<user_id>[0-9]+)/visitors/$', UserVisitorList.as_view()),
    # 推荐
    url(r'^recommend/', UserRecommend.as_view()),
]
