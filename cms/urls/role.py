from django.conf.urls import url

from cms.views.control.role import RoleList

urlpatterns = [
    url(r'^$', RoleList.as_view())
]
