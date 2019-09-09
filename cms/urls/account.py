from django.conf.urls import url

from cms.views.account.auth import LoginByUsername
from cms.views.account.info import UserInfo
from cms.views.account.password import ChangePassword
from cms.views.account.phone import ChangePhone

urlpatterns = [
    # 登录
    url(r'^auth/username/$', LoginByUsername.as_view()),
    # 用户详情
    url(r'^info/$', UserInfo.as_view()),
    url(r'^phone/$', ChangePhone.as_view()),
    url(r'^password/$', ChangePassword.as_view()),
]
