# todo 完善事件记录辅助函数与其他相关说明
from django.db import transaction
from django.core.exceptions import ObjectDoesNotExist

import json
from main.utils.http import notify_user

from main.models import User, Team, SystemAction, Activity, \
    Competition, ForumBoard
from main.models.task import InternalTask, ExternalTask
from main.models.need import TeamNeed


@transaction.atomic
def get_object_name(action):
    """ 获取对象的名称（或者标题）"""

    try:
        if action.object_type == "user":
            name = User.enabled.get(id=action.object_id).name
        elif action.object_type == "team":
            name = Team.enabled.get(id=action.object_id).name
        elif action.object_type == "member_need":
            name = TeamNeed.objects.get(id=action.object_id).title
        elif action.object_type == "outsource_need":
            name = TeamNeed.objects.get(id=action.object_id).title
        elif action.object_type == "undertake_need":
            name = TeamNeed.objects.get(id=action.object_id).title
        elif action.object_type == "internal_task":
            name = InternalTask.objects.get(id=action.object_id).title
        elif action.object_type == "external_task":
            name = ExternalTask.objects.get(id=action.object_id).title
        elif action.related_object_type == "activity":
            name = Activity.enabled.get(id=action.related_object_id).name
        elif action.related_object_type == "competition":
            name = Competition.enabled.get(id=action.related_object_id).name
        elif action.related_object_type == "forum":
            name = ForumBoard.enabled.get(id=action.related_object_id).name
        else:
            name = ""
        return name
    except ObjectDoesNotExist:
        return ""


@transaction.atomic
def get_related_object_name(action):
    """ 获取相关对象的名称（或者标题）"""

    try:
        if action.related_object_type == "user":
            name = User.enabled.get(id=action.related_object_id).name
        elif action.related_object_type == "team":
            name = Team.enabled.get(id=action.related_object_id).name
        elif action.related_object_type == "member_need":
            name = TeamNeed.objects.get(id=action.related_object_id).title
        elif action.related_object_type == "outsource_need":
            name = TeamNeed.objects.get(id=action.related_object_id).title
        elif action.related_object_type == "undertake_need":
            name = TeamNeed.objects.get(id=action.related_object_id).title
        elif action.object_type == "internal_task":
            name = InternalTask.objects.get(id=action.object_id).title
        elif action.object_type == "external_task":
            name = ExternalTask.objects.get(id=action.object_id).title
        elif action.related_object_type == "activity":
            name = Activity.enabled.get(id=action.related_object_id).name
        elif action.related_object_type == "competition":
            name = Competition.enabled.get(id=action.related_object_id).name
        elif action.related_object_type == "forum":
            name = ForumBoard.enabled.get(id=action.related_object_id).name
        else:
            name = ""
        return name
    except ObjectDoesNotExist:
        return ""


@transaction.atomic
def get_object_icon(action):
    """ 获取对象的头像"""

    if action.object_type == "user":
        icon = User.enabled.get(id=action.object_id).icon
    elif action.object_type == "team":
        icon = Team.enabled.get(id=action.object_id).icon
    else:
        icon = ""
    return icon


@transaction.atomic
def create_team(user, team):
    """记录创建团队事件"""

    user.actions.create(action='create',
                        object_type='team', object_id=team.id)
    team.actions.create(action='create_team',
                        object_type='user', object_id=user.id)
    for u in user.followers.all():
        notify_user(u.follower, json.dumps({
            'type': 'user_action',
            'content': user.name + '创建了团队' + team.name
        }))
    for t in team.followers.all():
        notify_user(t.follower, json.dumps({
            'type': 'team_action',
            'content': user.name + '创建了团队' + team.name
        }))


@transaction.atomic
def send_forum(user, forum):
    """记录创建论坛事件"""

    user.actions.create(action='create',
                        object_type='forum', object_id=forum.id)
    for u in user.followers.all():
        notify_user(u.follower, json.dumps({
            'type': 'user_action',
            'content': user.name + '创建了论坛' + forum.name
        }))


@transaction.atomic
def join_team(user, team):
    """记录参加团队事件"""

    user.actions.create(action='join',
                        object_type='team', object_id=team.id)
    team.actions.create(action='join',
                        object_type='user', object_id=user.id)
    for u in user.followers.all():
        notify_user(u.follower, json.dumps({
            'type': 'user_action',
            'content': user.name + '加入了团队' + team.name
        }))
    for t in team.followers.all():
        notify_user(t.follower, json.dumps({
            'type': 'team_action',
            'content': user.name + '加入了团队' + team.name
        }))


@transaction.atomic
def leave_team(user, team):
    """记录退出团队事件"""

    user.actions.create(action='leave',
                        object_type='team', object_id=team.id)
    team.actions.create(action='leave',
                        object_type='user', object_id=user.id)
    for u in user.followers.all():
        notify_user(u.follower, json.dumps({
            'type': 'user_action',
            'content': user.name + '退出了团队' + team.name
        }))
    for t in team.followers.all():
        notify_user(t.follower, json.dumps({
            'type': 'team_action',
            'content': user.name + '退出了团队' + team.name
        }))


@transaction.atomic
def finish_external_task(team, task):
    """记录团队完成外包及外包团队完成支付事件"""

    team.actions.create(action='finish',
                        object_type='external_task', object_id=task.id,
                        related_object_type='team',
                        related_object_id=task.team.id)
    task.team.actions.create(action='pay',
                             object_type='team', object_id=team.id,
                             related_object_type='external_task',
                             related_object_id=task.id)
    for t in team.followers.all():
        notify_user(t.follower, json.dumps({
            'type': 'team_action',
            'content': team.name + '完成了任务' + task.title
        }))


@transaction.atomic
def send_member_need(team, need):
    """记录团队发布人员需求事件"""

    team.actions.create(action='send',
                        object_type='member_need', object_id=need.id)
    for t in team.followers.all():
        notify_user(t.follower, json.dumps({
            'type': 'team_action',
            'content': team.name + '发布了需求' + need.title
        }))


@transaction.atomic
def send_outsource_need(team, need):
    """记录团队发布外包需求事件"""

    team.actions.create(action='send',
                        object_type='outsource_need', object_id=need.id)
    for t in team.followers.all():
        notify_user(t.follower, json.dumps({
            'type': 'team_action',
            'content': team.name + '发布了需求' + need.title
        }))


@transaction.atomic
def send_undertake_need(team, need):
    """记录团队发布承接需求事件"""

    team.actions.create(action='send',
                        object_type='undertake_need', object_id=need.id)
    for t in team.followers.all():
        notify_user(t.follower, json.dumps({
            'type': 'team_action',
            'content': team.name + '发布了需求' + need.title
        }))


@transaction.atomic
def send_activity(activity):
    """记录系统发布活动事件"""

    SystemAction.objects.create(action='send', object_type='activity',
                                object_id=activity.id)


@transaction.atomic
def send_competition(competition):
    """记录系统发布竞赛事件"""

    SystemAction.objects.create(action='send', object_type='competition',
                                object_id=competition.id)
