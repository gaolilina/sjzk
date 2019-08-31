from django.conf.urls import url

from main.views.me.experience import ExperienceList

urlpatterns = [
    # 经历
    url(r'^education/$', ExperienceList.as_view(), kwargs={'type': 'education'}),
    url(r'^work/$', ExperienceList.as_view(), kwargs={'type': 'work'}),
    url(r'^fieldwork/$', ExperienceList.as_view(), kwargs={'type': 'fieldwork'}),
]
