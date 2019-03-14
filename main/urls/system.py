from django.conf.urls import url

from main.views.system_role import RoleList
from ..views.system import *
from ..views.common import SystemActionsList

urls = [
    # 版本号
    url(r'^version_number/$', VersionNumber.as_view(), name='version_number'),
    # 系统动态
    url(r'actions/$', SystemActionsList.as_view(), name='actions'),
    # 系统通知
    url(r'notifications/$', SystemNotificationList.as_view(), name='actions'),
    # 资格认证角色列表
    url(r'qualification/$', RoleList.as_view(), name='qualification'),
    # 当前系统参数
    url(r'system_param/$', SystemParam.as_view(), name='system_param'),
]
