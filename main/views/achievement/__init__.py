from django.http import JsonResponse
from django.views.generic import View

from main.models import Achievement
from main.utils import abort
from main.utils.decorators import *
from util.decorator.param import fetch_object


# noinspection PyUnusedLocal
class AllUserAchievementView(View):
    @require_verification_token
    @fetch_object(Achievement.objects, 'achievement')
    def get(self, request, achievement):
        """获取成果详情"""
        user = request.user
        return JsonResponse({
            'achievement_id': achievement.id,
            'user_id': achievement.user.id,
            'user_name': achievement.user.unit1 if achievement.user.is_role_verified else achievement.user.name,
            'icon_url': achievement.user.icon,
            'desc': achievement.description,
            'pics': achievement.picture,
            'yes_count': achievement.likers.count(),  # 点赞数
            'is_yes': request.user in achievement.likers.all(),  # 是否点赞
            'require_count': achievement.requirers.count(),  # 需求树
            'is_require': request.user in achievement.requirers.all(),  # 是否需求
        })

    @require_verification_token
    @fetch_object(Achievement.objects, 'achievement')
    def delete(self, request, achievement):
        """删除成果
        TODO 如果是团队成果，需要验证当前用户是否有操作团队成果的权限
        """
        user = request.user
        achievement.delete()
        abort(200)


class AllTeamAchievementView(View):
    """
    弃用，功能迁移到上面的类中
    """
    @require_verification_token
    @fetch_object(Achievement.objects, 'achievement')
    def get(self, request, user, achievement):
        """获取成果详情"""
        return JsonResponse({
            'achievement_id': achievement.id,
            'team_id': achievement.team.id,
            'team_name': achievement.team.name,
            'icon_url': achievement.team.icon,
            'desc': achievement.description,
            'pics': achievement.picture,
        })

    @fetch_object(Achievement.objects, 'achievement')
    @require_verification_token
    def delete(self, request, team, achievement):
        """删除成果"""

        if request.user != achievement.team.owner:
            abort(403, '只有队长可以操作')
        achievement.delete()
        abort(200)