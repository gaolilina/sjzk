from django.conf.urls import url

from user import views

urlpatterns = [
    url(r'^token/', views.token, name='token'),
    url(r'^username/', views.username, name='username'),
]
