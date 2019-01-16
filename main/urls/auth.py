from django.conf.urls import url

from ..views.auth import *

urls = [
    # 实名/身份认证
    url(r'^idcard/$',
        IdentityVerificationView.as_view(), name='identity_verification'),
    # eid认证
    url(r'^eid/$',
        EidIdentityVerificationView.as_view(), name='eid_identity_verification'),
    # 资格认证
    url(r'^qualification/$', OtherIdentityVerificationView.as_view(),
        name='other_identity_verification'),
]
