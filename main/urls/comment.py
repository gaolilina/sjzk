from django.conf.urls import url

from main.views.comment.system import SystemActionCommentList
from main.views.comment.user import UserCommentList, UserActionCommentList
from main.views.comment.team import TeamActionCommentList

urlpatterns = [
    # 评论
    url(r'^comments/$', UserCommentList.as_view()),
    url(r'^user_action/(?P<action_id>[0-9]+)/comments/$', UserActionCommentList.as_view()),
    url(r'^team_action/(?P<action_id>[0-9]+)/comments/$', TeamActionCommentList.as_view()),
    url(r'^system_action/(?P<action_id>[0-9]+)/comments/$', SystemActionCommentList.as_view()),
]
