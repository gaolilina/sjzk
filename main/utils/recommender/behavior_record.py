# 用户行为记录相关函数

from ...models import UserBehavior


def record_view_user(current_user, user):
    """记录浏览用户行为"""

    r = UserBehavior(user=current_user, behavior='view',
                     object_type='user', object_id=user.id)
    r.save()


def record_like_user(current_user, user):
    """记录对用户的点赞行为"""

    r = UserBehavior(user=current_user, behavior='like',
                     object_type='user', object_id=user.id)
    r.save()


def record_view_team(current_user, team):
    """记录浏览团队team行为"""

    r = UserBehavior(user=current_user, behavior='view',
                     object_type='team', object_id=team.id)
    r.save()


def record_like_team(current_user, team):
    """记录对团队的点赞行为"""

    r = UserBehavior(user=current_user, behavior='like',
                     object_type='team', object_id=team.id)
    r.save()
