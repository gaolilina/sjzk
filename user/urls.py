from django.conf.urls import url

from user import views

urlpatterns = [
    url(r'^$', views.user_root, name='root'),
    url(r'^total/', views.user_total, name='total'),
    url(r'^token/', views.user_token, name='token'),
    url(r'^username/', views.user_username, name='username'),
    url(r'^password/', views.user_password, name='password'),
]
