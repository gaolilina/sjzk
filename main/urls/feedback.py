from django.conf.urls import url

from main.views.feedback import Feedback

urlpatterns = [
    # 意见反馈
    url(r'^feedback/$', Feedback.as_view()),
]
