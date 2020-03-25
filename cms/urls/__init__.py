from django.conf.urls import url, include

from cms.urls import role, function, permission, adminuser, account, word, user, recommend, manageComboBox


urlpatterns = [
    url(r'^role/', include(role)),
    url(r'^function/', include(function)),
    url(r'^permission/', include(permission)),
    url(r'^manager/', include(adminuser)),
    url(r'^account/', include(account)),
    url(r'^word/', include(word)),
    url(r'^user/', include(user)),
    url(r'^recommend/', include(recommend)),
    url(r'^manageword/', include(manageComboBox)),

    # 弃用
    url(r'^adminuser/', include(adminuser)),
]
