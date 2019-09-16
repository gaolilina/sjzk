from django.conf.urls import url

from main.views.me.invite import InvitationCode, Inviter
from main.views.me.invite_team import InvitationList, Invitation

urlpatterns = [
    # 团队邀请
    url(r'^invitations/$', InvitationList.as_view()),
    url(r'^invitations/(?P<invitation_id>[0-9]+)/$', Invitation.as_view()),
    # 邀请码
    url(r'^invitation_code/$', InvitationCode.as_view()),
    url(r'^inviter/$', Inviter.as_view()),
]
