from django.conf.urls import url

from main.views.task import InternalTaskList, InternalTasks, ExternalTaskList, ExternalTasks, TeamInternalTask, \
    TeamExternalTask

urls = [
    # 任务
    url(r'^(?P<team_id>[0-9]+)/internal_tasks/$', InternalTaskList.as_view()),
    url(r'^owned_internal_tasks/$', InternalTasks.as_view()),
    url(r'^internal_tasks/(?P<task_id>[0-9]+)/$', InternalTasks.as_view()),
    url(r'^(?P<task_id>[0-9]+)/internal_task/$', TeamInternalTask.as_view()),

    url(r'^(?P<team_id>[0-9]+)/external_tasks/$', ExternalTaskList.as_view()),
    url(r'^external_tasks/(?P<task_id>[0-9]+)/$', ExternalTasks.as_view()),
    url(r'^(?P<task_id>[0-9]+)/external_task/$', TeamExternalTask.as_view()),

    #==================================弃用==================================

]
