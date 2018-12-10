from django.conf.urls import url

from ..views.lab import *
from ..views.common import LabActionList, LabCommentList, LabComment, \
    LabFollowerList, LabFollower, LabLikerList, LabLiker, \
    LabVisitorList, LabAchievementLikerList, LabAchievementLiker#, LabNeedFollowerList
#from ..views.recommend import LabRecommend, OutsourceNeedLabRecommend, \
#    UndertakeNeedLabRecommend


urls = [
    # 基本
    url(r'^$', List.as_view(), name='list'),
    url(r'^(?P<lab_id>[0-9]+)/profile/$', Profile.as_view(), name='profile'),
    url(r'^(?P<lab_id>[0-9]+)/icon/$', Icon.as_view(), name='icon'),
    # 团队搜索
    url(r'^search/$', Search.as_view(), name='search'),
    # 筛选
    url(r'^screen/$', Screen.as_view(), name='screen'),
    # 成员
    url(r'^(?P<lab_id>[0-9]+)/members/$', MemberList.as_view(),
        name='member_list'),
    url(r'^(?P<lab_id>[0-9]+)/members/(?P<user_id>[0-9]+)/$', Member.as_view(),
        name='members'),
    url(r'^(?P<lab_id>[0-9]+)/member_requests/$',
        MemberRequestList.as_view(), name='member_requests'),
    url(r'^(?P<lab_id>[0-9]+)/member_requests/(?P<user_id>[0-9]+)/$',
        MemberRequest.as_view(), name='member_request'),
    url(r'^(?P<lab_id>[0-9]+)/invitations/(?P<user_id>[0-9]+)/$',
        Invitation.as_view(), name='invitation'),
    # 动态
    url(r'^(?P<lab_id>[0-9]+)/actions/$', LabActionList.as_view(),
        name='actions'),
    # 成果
    url(r'^achievements/$', AllAchievementList.as_view(),
        name='all_achievements'),
    url(r'^achievement/(?P<achievement_id>[0-9]+)/$',
        AllAchievement.as_view(), name='achievement'),
    url(r'^(?P<lab_id>[0-9]+)/achievements/$', AchievementList.as_view(),
        name='achievements'),
    # 点赞
    url(r'^(?P<lab_id>[0-9]+)/likers/$', LabLikerList.as_view(),
        name='likers'),
    url(r'^(?P<lab_id>[0-9]+)/likers/(?P<other_user_id>[0-9]+)/$',
        LabLiker.as_view(), name='liker'),
    # 点赞
    url(r'^(?P<achievement_id>[0-9]+)/likers/$', LabAchievementLikerList.as_view(),
        name='likers'),
    url(r'^(?P<achievement_id>[0-9]+)/likers/(?P<other_user_id>[0-9]+)/$',
        LabAchievementLiker.as_view(), name='liker'),
    # 粉丝
    url(r'^(?P<lab_id>[0-9]+)/followers/$', LabFollowerList.as_view(),
        name='followers'),
    url(r'^(?P<lab_id>[0-9]+)/followers/(?P<other_user_id>[0-9]+)/$',
        LabFollower.as_view(), name='follower'),
    # 评论
    url(r'^(?P<lab_id>[0-9]+)/comments/$', LabCommentList.as_view(),
        name='comments'),
    url(r'^comments/(?P<comment_id>[0-9]+)/$',
        LabComment.as_view(), name='comment'),
    # 访客
    url(r'^(?P<lab_id>[0-9]+)/visitors/$',
        LabVisitorList.as_view(), name='visitors'),

    # 需求
    url(r'^needs/$', AllNeedList.as_view(), name='all_needs'),
    url(r'^needs/(?P<need_id>[0-9]+)/$', Need.as_view(), name='need'),
    url(r'^(?P<need_id>[0-9]+)/need/users/$',
        NeedUserList.as_view(), name='need_users'),
    url(r'^(?P<need_id>[0-9]+)/need/labs/$',
        NeedLabList.as_view(), name='need_labs'),

    url(r'^needs/member/$', AllNeedList.as_view(),
        name='all_member_needs', kwargs={'type': 0}),
    url(r'^needs/outsource/$', AllNeedList.as_view(),
        name='all_outsource_needs', kwargs={'type': 1}),
    url(r'^needs/undertake/$', AllNeedList.as_view(),
        name='all_undertake_needs', kwargs={'type': 2}),
    url(r'^(?P<lab_id>[0-9]+)/needs/$', NeedList.as_view(), name='needs'),
    url(r'^(?P<lab_id>[0-9]+)/needs/member/$', NeedList.as_view(),
        name='member_needs', kwargs={'type': 0}),
    url(r'^(?P<lab_id>[0-9]+)/needs/outsource/$', NeedList.as_view(),
        name='outsource_needs', kwargs={'type': 1}),
    url(r'^(?P<lab_id>[0-9]+)/needs/undertake/$', NeedList.as_view(),
        name='undertake_needs', kwargs={'type': 2}),

    url(r'^(?P<need_id>[0-9]+)/needs/member_requests/$',
        MemberNeedRequestList.as_view(), name='need_member_requests'),
    url(r'^(?P<need_id>[0-9]+)/needs/member_requests/(?P<user_id>[0-9]+)/$',
        MemberNeedRequest.as_view(), name='need_member_request'),
    url(r'^(?P<lab_id>[0-9]+)/needs/requests/(?P<need_id>[0-9]+)/$',
        NeedRequestList.as_view(), name='need_cooperation_requests'),
    url(r'^(?P<lab_id>[0-9]+)/needs/requests/$',
        NeedRequest.as_view(), name='lab_cooperation_requests'),
    url(r'^(?P<lab_id>[0-9]+)/needs/request/(?P<need_id>[0-9]+)/$',
        NeedRequest.as_view(), name='need_cooperation_request'),
    url(r'^(?P<lab_id>[0-9]+)/needs/invitations/(?P<need_id>[0-9]+)/$',
        NeedInvitationList.as_view(), name='need_cooperation_invitations'),
    url(r'^(?P<lab_id>[0-9]+)/needs/invitations/$',
        NeedInvitation.as_view(), name='lab_cooperation_invitations'),
    url(r'^(?P<lab_id>[0-9]+)/needs/invitation/(?P<need_id>[0-9]+)/$',
        NeedInvitation.as_view(), name='need_cooperation_invitation'),
    # 需求搜索
    url(r'^needs/search/$', NeedSearch.as_view(), name='need_search'),
    url(r'^needs/screen/$', NeedScreen.as_view(), name='need_screen'),
    # 需求的粉丝
    #url(r'^needs/(?P<need_id>[0-9]+)/followers/$',
    #    LabNeedFollowerList.as_view(), name='followers'),
    # 任务
    url(r'^(?P<lab_id>[0-9]+)/internal_tasks/$', InternalTaskList.as_view(),
        name='lab_internal_tasks'),
    url(r'^owned_internal_tasks/$', InternalTasks.as_view(),
        name='owned_internal_tasks'),
    url(r'^internal_tasks/(?P<task_id>[0-9]+)/$', InternalTasks.as_view(),
        name='internal_tasks'),
    url(r'^(?P<task_id>[0-9]+)/internal_task/$', LabInternalTask.as_view(),
        name='internal_task'),

    url(r'^(?P<lab_id>[0-9]+)/external_tasks/$', ExternalTaskList.as_view(),
        name='lab_external_tasks'),
    url(r'^external_tasks/(?P<task_id>[0-9]+)/$', ExternalTasks.as_view(),
        name='external_tasks'),
    url(r'^(?P<task_id>[0-9]+)/external_task/$', LabExternalTask.as_view(),
        name='external_task'),
    # 推荐
    #url(r'^(?P<lab_id>[0-9]+)/recommend/', LabRecommend.as_view(),
    #    name='recommend_labs'),
    #url(r'^(?P<need_id>[0-9]+)/outsource/recommend/',
    #    OutsourceNeedLabRecommend.as_view(), name='outsource_recommend'),
    #url(r'^(?P<need_id>[0-9]+)/undertake/recommend/',
    #    UndertakeNeedLabRecommend.as_view(), name='undertake_recommend'),
    # 竞赛
    url(r'^(?P<lab_id>[0-9]+)/competition/$',
        CompetitionList.as_view(), name='competition'),
    # 积分明细
    url(r'^(?P<lab_id>[0-9]+)/score_records/$', LabScoreRecord.as_view(),
        name='score_records'),
    # 团队参加的竞赛评比列表
    url(r'^(?P<lab_id>[0-9]+)/awards/$',LabAwardList.as_view(),
        name='awards'),
]
