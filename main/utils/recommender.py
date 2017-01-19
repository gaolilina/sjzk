# 个性化推荐相关函数
import json

from django.core.exceptions import ObjectDoesNotExist
from main.models import UserBehavior


def calculate_ranking_score(object0, object1):
    """计算排序分数"""

    try:
        m0 = json.loads(object0.feature_model.data)
        m1 = json.loads(object1.feature_model.data)
    except ObjectDoesNotExist:
        return 0

    score = 0
    common_tags = set(m0.keys()) & set(m1.keys())
    for t in common_tags:
        score += min(m0[t], m1[t])
    return score


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
