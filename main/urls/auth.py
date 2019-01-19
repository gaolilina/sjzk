from django.conf.urls import url

from ..views.auth import *

urls = [
    # 实名/身份认证
    url(r'^idcard/$', IdentityVerificationView.as_view(), name='identity_verification'),
    url(r'^idcard/pic/$', IDCardView.as_view(), name='id_card'),
    # eid认证
    url(r'^eid/$', EidIdentityVerificationView.as_view(), name='eid_identity_verification'),
    # 资格认证
    url(r'^qualification/$', OtherIdentityVerificationView.as_view(), name='other_identity_verification'),
    url(r'^qualification/pic/$', OtherCardView.as_view(), name='other_card'),
]
