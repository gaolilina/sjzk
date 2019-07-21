from django.conf.urls import url, include

from cms.views.control.function import AllFunctionList

urlpatterns = [
    url(r'^$', AllFunctionList.as_view()),
]
