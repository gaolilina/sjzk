from django.conf.urls import url

from main.views.search import SearchTeam
from main.views.team.competition import CompetitionList, TeamAwardList
from main.views.team.info import Profile, Icon, TeamScoreRecord
from main.views.team.member import MemberList, Member, MemberRequestList, MemberRequest, Invitation
from main.views.team.social import TeamActionList, TeamCommentList, TeamComment, TeamFollower, \
    TeamVisitorList
from main.views.follow.team import TeamFollowerList
from main.views.like.team import TeamLiker, TeamLikerList
from ..views.recommend import TeamRecommend, OutsourceNeedTeamRecommend, UndertakeNeedTeamRecommend
from ..views.team import *

urls = [
    # 团队搜索
    url(r'^search/$', SearchTeam.as_view()),
    # 筛选
    url(r'^screen/$', Screen.as_view()),

    url(r'^$', TeamCreate.as_view()),
    ##########################信息
    # 基本
    url(r'^(?P<team_id>[0-9]+)/profile/$', Profile.as_view()),
    url(r'^(?P<team_id>[0-9]+)/icon/$', Icon.as_view()),
    # 积分明细
    url(r'^(?P<team_id>[0-9]+)/score_records/$', TeamScoreRecord.as_view()),
    # 成员
    url(r'^(?P<team_id>[0-9]+)/members/$', MemberList.as_view()),
    url(r'^(?P<team_id>[0-9]+)/members/(?P<user_id>[0-9]+)/$', Member.as_view()),
    url(r'^(?P<team_id>[0-9]+)/member_requests/$', MemberRequestList.as_view()),
    url(r'^(?P<team_id>[0-9]+)/member_requests/(?P<user_id>[0-9]+)/$', MemberRequest.as_view()),
    url(r'^(?P<team_id>[0-9]+)/invitations/(?P<user_id>[0-9]+)/$', Invitation.as_view()),

    ########################社交
    # 动态
    url(r'^(?P<team_id>[0-9]+)/actions/$', TeamActionList.as_view()),
    # 点赞
    url(r'^(?P<team_id>[0-9]+)/likers/$', TeamLikerList.as_view()),
    url(r'^(?P<team_id>[0-9]+)/likers/(?P<other_user_id>[0-9]+)/$', TeamLiker.as_view()),
    # 粉丝
    url(r'^(?P<team_id>[0-9]+)/followers/$', TeamFollowerList.as_view()),
    url(r'^(?P<team_id>[0-9]+)/followers/(?P<other_user_id>[0-9]+)/$', TeamFollower.as_view()),
    # 评论
    url(r'^(?P<team_id>[0-9]+)/comments/$', TeamCommentList.as_view()),
    url(r'^comments/(?P<comment_id>[0-9]+)/$', TeamComment.as_view()),
    # 访客
    url(r'^(?P<team_id>[0-9]+)/visitors/$', TeamVisitorList.as_view()),

    #######################竞赛
    # 竞赛
    url(r'^(?P<team_id>[0-9]+)/competition/$', CompetitionList.as_view()),
    # 团队参加的竞赛评比列表
    url(r'^(?P<team_id>[0-9]+)/awards/$', TeamAwardList.as_view()),

    # ==================================弃用==================================
    # 推荐
    url(r'^(?P<team_id>[0-9]+)/recommend/', TeamRecommend.as_view()),
    url(r'^(?P<need_id>[0-9]+)/outsource/recommend/', OutsourceNeedTeamRecommend.as_view()),
    url(r'^(?P<need_id>[0-9]+)/undertake/recommend/', UndertakeNeedTeamRecommend.as_view()),
]
