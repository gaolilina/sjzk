from django.conf.urls import url

from main.views.account import Account, AccountCheck
from main.views.account.auth import *

urls = [
    # 检查账户是否存在
    url(r'^account/(?P<phone>\d{11})/exists/$', AccountCheck.as_view()),
    # 注册，登录
    url(r'^account/(?P<method>\w+)/$', Account.as_view()),
    # 实名/身份认证
    url(r'^idcard/$', IdentityVerificationView.as_view()),
    url(r'^idcard/pic/$', IDCardView.as_view()),
    # eid认证
    url(r'^eid/$', EidIdentityVerificationView.as_view()),
    # 资格认证
    url(r'^qualification/$', OtherIdentityVerificationView.as_view()),
    url(r'^qualification/pic/$', OtherCardView.as_view()),
]
