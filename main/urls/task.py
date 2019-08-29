from django.conf.urls import url

from main.views.task.outer import ExternalTaskList, ExternalTasks, TeamExternalTask
from main.views.task.inner import InternalTaskList, InternalTasks, TeamInternalTask, MyInnerTasks

urls = [
    # 内部任务
    url(r'^(?P<team_id>[0-9]+)/internal_tasks/$', InternalTaskList.as_view()),
    url(r'^owned_internal_tasks/$', MyInnerTasks.as_view()),
    url(r'^internal_tasks/(?P<task_id>[0-9]+)/$', InternalTasks.as_view()),
    url(r'^(?P<task_id>[0-9]+)/internal_task/$', TeamInternalTask.as_view()),

    # 外部任务
    url(r'^(?P<team_id>[0-9]+)/external_tasks/$', ExternalTaskList.as_view()),
    url(r'^external_tasks/(?P<task_id>[0-9]+)/$', ExternalTasks.as_view()),
    url(r'^(?P<task_id>[0-9]+)/external_task/$', TeamExternalTask.as_view()),

    #==================================弃用==================================

]
