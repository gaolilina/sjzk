from django.conf.urls import url

from main.views.search import SearchTeam
from ..views.team import *
from ..views.common import TeamActionList, TeamCommentList, TeamComment, \
    TeamFollowerList, TeamFollower, TeamLikerList, TeamLiker, \
    TeamVisitorList, TeamNeedFollowerList
from ..views.recommend import TeamRecommend, OutsourceNeedTeamRecommend, \
    UndertakeNeedTeamRecommend

urls = [
    # 需求搜索，迁移到 /search/ 上
    url(r'^needs/search/$', NeedSearch.as_view()),
    url(r'^needs/screen/$', NeedScreen.as_view()),
    # 团队搜索
    url(r'^search/$', SearchTeam.as_view()),
    # 筛选
    url(r'^screen/$', Screen.as_view()),

    url(r'^$', TeamCreate.as_view()),
    # 基本
    url(r'^(?P<team_id>[0-9]+)/profile/$', Profile.as_view()),
    url(r'^(?P<team_id>[0-9]+)/icon/$', Icon.as_view()),
    # 成员
    url(r'^(?P<team_id>[0-9]+)/members/$', MemberList.as_view()),
    url(r'^(?P<team_id>[0-9]+)/members/(?P<user_id>[0-9]+)/$', Member.as_view()),
    url(r'^(?P<team_id>[0-9]+)/member_requests/$',
        MemberRequestList.as_view()),
    url(r'^(?P<team_id>[0-9]+)/member_requests/(?P<user_id>[0-9]+)/$', MemberRequest.as_view()),
    url(r'^(?P<team_id>[0-9]+)/invitations/(?P<user_id>[0-9]+)/$', Invitation.as_view()),
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

    # 需求
    url(r'^needs/$', AllNeedList.as_view()),
    url(r'^needs/(?P<need_id>[0-9]+)/$', Need.as_view()),
    url(r'^(?P<need_id>[0-9]+)/need/users/$', NeedUserList.as_view()),
    url(r'^(?P<need_id>[0-9]+)/need/teams/$', NeedTeamList.as_view()),

    url(r'^needs/member/$', AllNeedList.as_view(), kwargs={'type': 0}),
    url(r'^needs/outsource/$', AllNeedList.as_view(), kwargs={'type': 1}),
    url(r'^needs/undertake/$', AllNeedList.as_view(), kwargs={'type': 2}),
    url(r'^(?P<team_id>[0-9]+)/needs/$', NeedList.as_view()),
    url(r'^(?P<team_id>[0-9]+)/needs/member/$', NeedList.as_view(), kwargs={'type': 0}),
    url(r'^(?P<team_id>[0-9]+)/needs/outsource/$', NeedList.as_view(), kwargs={'type': 1}),
    url(r'^(?P<team_id>[0-9]+)/needs/undertake/$', NeedList.as_view(), kwargs={'type': 2}),

    url(r'^(?P<need_id>[0-9]+)/needs/member_requests/$', MemberNeedRequestList.as_view()),
    url(r'^(?P<need_id>[0-9]+)/needs/member_requests/(?P<user_id>[0-9]+)/$', MemberNeedRequest.as_view()),
    url(r'^(?P<team_id>[0-9]+)/needs/requests/(?P<need_id>[0-9]+)/$', NeedRequestList.as_view()),
    url(r'^(?P<team_id>[0-9]+)/needs/requests/$', NeedRequest.as_view()),
    url(r'^(?P<team_id>[0-9]+)/needs/request/(?P<need_id>[0-9]+)/$', NeedRequest.as_view()),
    url(r'^(?P<team_id>[0-9]+)/needs/invitations/(?P<need_id>[0-9]+)/$', NeedInvitationList.as_view()),
    url(r'^(?P<team_id>[0-9]+)/needs/invitations/$', NeedInvitation.as_view()),
    url(r'^(?P<team_id>[0-9]+)/needs/invitation/(?P<need_id>[0-9]+)/$', NeedInvitation.as_view()),
    # 需求的粉丝
    url(r'^needs/(?P<need_id>[0-9]+)/followers/$', TeamNeedFollowerList.as_view()),
    # 任务
    url(r'^(?P<team_id>[0-9]+)/internal_tasks/$', InternalTaskList.as_view()),
    url(r'^owned_internal_tasks/$', InternalTasks.as_view()),
    url(r'^internal_tasks/(?P<task_id>[0-9]+)/$', InternalTasks.as_view()),
    url(r'^(?P<task_id>[0-9]+)/internal_task/$', TeamInternalTask.as_view()),

    url(r'^(?P<team_id>[0-9]+)/external_tasks/$', ExternalTaskList.as_view()),
    url(r'^external_tasks/(?P<task_id>[0-9]+)/$', ExternalTasks.as_view()),
    url(r'^(?P<task_id>[0-9]+)/external_task/$', TeamExternalTask.as_view()),
    # 推荐
    url(r'^(?P<team_id>[0-9]+)/recommend/', TeamRecommend.as_view()),
    url(r'^(?P<need_id>[0-9]+)/outsource/recommend/', OutsourceNeedTeamRecommend.as_view()),
    url(r'^(?P<need_id>[0-9]+)/undertake/recommend/', UndertakeNeedTeamRecommend.as_view()),
    # 竞赛
    url(r'^(?P<team_id>[0-9]+)/competition/$', CompetitionList.as_view()),
    # 积分明细
    url(r'^(?P<team_id>[0-9]+)/score_records/$', TeamScoreRecord.as_view()),
    # 团队参加的竞赛评比列表
    url(r'^(?P<team_id>[0-9]+)/awards/$', TeamAwardList.as_view()),
]
