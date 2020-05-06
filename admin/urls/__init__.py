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

    # 系统配置
    url(r'^system_admin/', Setting.as_view(), name='system'),

    # 系统通知
    url(r'^system_notification/', Notification.as_view(), name='notification'),

    # 调查问卷
    url(r'^paper/', include(paper.urls, namespace='paper')),

    # 日志
    url(r'^op_log/', OpLog.as_view(), name='op_log'), # 管理端操作日志
    url(r'^security_log/', include(security.urls, namespace='security_log')), # 客户端安全日志

    # 竞赛的业务流程
    url(r'^admin_competition/', include(admin_competition.urls, namespace="admin_competition")),

    # 活动的业务流程
    url(r'^activity/', include(activity.urls, namespace="activity")),

    # 纯粹的客户端数据管理
    url(r'^competition_admin/', include(competition, namespace="competition")), # 竞赛对象的数据管理
    url(r'^admin_activity/', include(client.urls, namespace="admin_activity")), # 活动对象的数据管理
    url(r'^feedback/', include(feedback.urls, namespace="feedback")),
    url(r'^user_admin/', include(user.urls, namespace="user")),
    url(r'^team_admin/', include(team.urls, namespace="team")),
    url(r'^forum_admin/', include(forum.urls, namespace="forum")),

    # 以下的弃用，已迁移至 cms
    # 管理员
    url(r'^admin_users/', include(admin_users.urls, namespace="admin_users")), # 管理自己的信息
    url(r'^admin_user/', include(admin_user.urls, namespace='admin_user')), # 作为管理员管理其他管理员

    # 注册管理员
    url(r'^register', Register.as_view(), name='register'),
]
