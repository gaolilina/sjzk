from django.conf.urls import url, include

from admin.urls import security, paper
from admin.urls.activity import client
from . import admin_users, admin_competition, feedback, user, team, activity, competition, forum, admin_user

from admin.views.main import Login, Register, Main
from admin.views.system import Setting, Notification
from admin.views.op_log import OpLog

urlpatterns = [
    url(r'^$', Main.as_view(), name='root'),
    url(r'^login', Login.as_view(), name='login'),
    url(r'^register', Register.as_view(), name='register'),
    url(r'^admin_users/', include(admin_users.urls, namespace="admin_users")),
    url(r'^feedback/', include(feedback.urls, namespace="feedback")),
    url(r'^user_admin/', include(user.urls, namespace="user")),
    url(r'^team_admin/', include(team.urls, namespace="team")),
    url(r'^forum_admin/', include(forum.urls, namespace="forum")),
    url(r'^system_admin/', Setting.as_view(), name='system'),
    url(r'^system_notification/', Notification.as_view(), name='notification'),
    url(r'^admin_user/', include(admin_user.urls, namespace='admin_user')),
    url(r'^op_log/', OpLog.as_view(), name='op_log'),
    url(r'^paper/', include(paper.urls, namespace='paper')),
    url(r'^security_log/', include(security.urls, namespace='security_log')),

    url(r'^competition_admin/', include(competition, namespace="competition")),
    url(r'^admin_competition/', include(admin_competition.urls, namespace="admin_competition")),

    # 活动，以后仅在 activity 这个 url，另外两个不在维护
    url(r'^admin_activity/', include(client.urls, namespace="admin_activity")),
    url(r'^activity/', include(activity.urls, namespace="activity")),
]
