from django.conf.urls import url, include

from cms.views.control.function import AllFunctionList, FunctionDetail

urlpatterns = [
    # 所有功能列表
    url(r'^$', AllFunctionList.as_view()),
    # 我的功能列表
    url(r'^my/$', AllFunctionList.as_view()),
    # 功能详情
    url(r'^(?P<function_id>\w+)/$', FunctionDetail.as_view()),
]
