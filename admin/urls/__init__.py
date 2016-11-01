from django.conf.urls import url, include

from . import admin_users, admin_activity, user

from admin.views.main import Login, Register

urlpatterns = [
    url(r'^login', Login.as_view(), name='login'),
    url(r'^register', Register.as_view(), name='register'),
    url(r'^admin_users/', include(admin_users.urls, namespace="admin_user")),
    url(r'^admin_activity/', include(admin_activity.urls, namespace="admin_activity")),
    url(r'^user/', include(user.urls, namespace="user")),
]
