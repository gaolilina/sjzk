from django.conf.urls import url

from cms.views.recommend import CalculateUserSim

urlpatterns = [
    url(r'^sim/user/$', CalculateUserSim.as_view()),
]
