# todo 完善事件记录辅助函数与其他相关说明
from django.db import transaction


@transaction.atomic
def create_team(user, team):
    """记录创建团队事件"""

    user.actions.create(action='create',
                        object_type='team', object_id=team.id)
    team.actions.create(action='create_team',
                        object_type='user', object_id=user.id)


@transaction.atomic
def join_team(user, team):
    """记录参加团队事件"""

    user.actions.create(action='join',
                        object_type='team', object_id=team.id)
    team.actions.create(action='join',
                        object_type='user', object_id=user.id)


@transaction.atomic
def leave_team(user, team):
    """记录退出团队事件"""

    user.actions.create(action='leave',
                        object_type='team', object_id=team.id)
    team.actions.create(action='leave',
                        object_type='user', object_id=user.id)
