from django.conf.urls import url, include

from cms.urls import role, function, permission, adminuser, account

urlpatterns = [
    url(r'^role/', include(role)),
    url(r'^function/', include(function)),
    url(r'^permission/', include(permission)),
    url(r'^adminuser/', include(adminuser)),
    url(r'^account/', include(account)),
]
