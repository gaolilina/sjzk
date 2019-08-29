from django.conf.urls import url

from main.views.need import NeedScreen, Need
from main.views.need.invitation import NeedInvitationList, NeedInvitation, TeamInvitationList
from main.views.need.user import MemberNeedRequestList, MemberNeedRequest, NeedUserList
from main.views.need.team import NeedTeamList, NeedRequestList, NeedRequest, TeamApplyNeedList
from main.views.need.create import CreateNeed
from main.views.search.need import NeedSearch
from ..views.common import TeamNeedFollowerList

urls = [
    # 详情
    url(r'^needs/(?P<need_id>[0-9]+)/$', Need.as_view()),
    # 需求的粉丝
    url(r'^needs/(?P<need_id>[0-9]+)/followers/$', TeamNeedFollowerList.as_view()),

    # 列表
    url(r'^needs/member/$', NeedSearch.as_view(), kwargs={'type': 0}),
    url(r'^needs/outsource/$', NeedSearch.as_view(), kwargs={'type': 1}),
    url(r'^needs/undertake/$', NeedSearch.as_view(), kwargs={'type': 2}),

    # 创建
    url(r'^(?P<team_id>[0-9]+)/needs/member/$', CreateNeed.as_view(), kwargs={'type': 0}),
    url(r'^(?P<team_id>[0-9]+)/needs/outsource/$', CreateNeed.as_view(), kwargs={'type': 1}),
    url(r'^(?P<team_id>[0-9]+)/needs/undertake/$', CreateNeed.as_view(), kwargs={'type': 2}),

    # 相关人员
    url(r'^(?P<need_id>[0-9]+)/need/users/$', NeedUserList.as_view()),
    url(r'^(?P<need_id>[0-9]+)/needs/member_requests/$', MemberNeedRequestList.as_view()),
    url(r'^(?P<need_id>[0-9]+)/needs/member_requests/(?P<user_id>[0-9]+)/$', MemberNeedRequest.as_view()),

    # 相关团队
    url(r'^(?P<need_id>[0-9]+)/need/teams/$', NeedTeamList.as_view()),
    url(r'^(?P<team_id>[0-9]+)/needs/requests/(?P<need_id>[0-9]+)/$', NeedRequestList.as_view()),
    url(r'^(?P<team_id>[0-9]+)/needs/request/(?P<need_id>[0-9]+)/$', NeedRequest.as_view()),
    url(r'^(?P<team_id>[0-9]+)/needs/requests/$', TeamApplyNeedList.as_view()),

    # 邀请
    url(r'^(?P<team_id>[0-9]+)/needs/invitations/(?P<need_id>[0-9]+)/$', NeedInvitationList.as_view()),
    url(r'^(?P<team_id>[0-9]+)/needs/invitation/(?P<need_id>[0-9]+)/$', NeedInvitation.as_view()),
    url(r'^(?P<team_id>[0-9]+)/needs/invitations/$', TeamInvitationList.as_view()),

    # ==================================弃用==================================
    url(r'^needs/screen/$', NeedScreen.as_view()),
    # 需求搜索，迁移到 /search/ 上
    url(r'^needs/search/$', NeedSearch.as_view()),
    url(r'^needs/$', NeedSearch.as_view()),
]
