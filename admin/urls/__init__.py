from django.conf.urls import url, include

from . import admin_users, user

from admin.views.main import Login, Register

urlpatterns = [
    url(r'^login', Login.as_view(), name='login'),
    url(r'^register', Register.as_view(), name='register'),
    url(r'^admin_users/', include(admin_users.urls, namespace="admin_user")),
    url(r'^user/', include(user.urls, namespace="user")),
]
