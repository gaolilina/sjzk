from django.conf.urls import url, include

from admin.urls import security, paper
from . import admin_users, admin_activity, admin_competition, feedback, user, team, activity, competition, forum, admin_user

from admin.views.main import Login, Register, Main
from admin.views.system import Setting, Notification
from admin.views.op_log import OpLog

urlpatterns = [
    url(r'^$', Main.as_view(), name='root'),
    url(r'^login', Login.as_view(), name='login'),
    url(r'^register', Register.as_view(), name='register'),
    url(r'^admin_users/', include(admin_users.urls, namespace="admin_users")),
    url(r'^admin_activity/', include(admin_activity.urls, namespace="admin_activity")),
    url(r'^admin_competition/', include(admin_competition.urls, namespace="admin_competition")),
    url(r'^feedback/', include(feedback.urls, namespace="feedback")),
    url(r'^user_admin/', include(user.urls, namespace="user")),
    url(r'^team_admin/', include(team.urls, namespace="team")),
    url(r'^activity_admin/', include(activity.urls, namespace="activity")),
    url(r'^competition_admin/', include(competition.urls, namespace="competition")),
    url(r'^forum_admin/', include(forum.urls, namespace="forum")),
    url(r'^system_admin/', Setting.as_view(), name='system'),
    url(r'^system_notification/', Notification.as_view(), name='notification'),
    url(r'^admin_user/', include(admin_user.urls, namespace='admin_user')),
    url(r'^op_log/', OpLog.as_view(), name='op_log'),
    url(r'^paper/', include(paper.urls), name='paper'),
    url(r'^security_log/', include(security.urls, namespace='security_log')),
]
