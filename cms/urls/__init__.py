from django.conf.urls import url, include

from cms.urls import role, function, permission, adminuser, account, word

urlpatterns = [
    url(r'^role/', include(role)),
    url(r'^function/', include(function)),
    url(r'^permission/', include(permission)),
    url(r'^manager/', include(adminuser)),
    url(r'^account/', include(account)),
    url(r'^word/', include(word)),

    # 弃用
    url(r'^adminuser/', include(adminuser)),
]
