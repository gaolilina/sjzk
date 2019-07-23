from django.conf.urls import url, include

from cms.views.control.function import AllFunctionList, FunctionDetail

urlpatterns = [
    url(r'^$', AllFunctionList.as_view()),
    url(r'^(?P<function_id>\w+)/$', FunctionDetail.as_view()),
]
