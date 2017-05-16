from django.conf.urls import url

from ..views.system import *
from ..views.common import SystemActionCommentList, SystemActionsList

urls = [
    # 版本号
    url(r'^version_number/$', VersionNumber.as_view(), name='version_number'),
    # 系统动态
    url(r'actions/$', SystemActionsList.as_view(), name='actions'),
]