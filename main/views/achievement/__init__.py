from django import forms
from django.http import JsonResponse
from django.views.generic import View

from main.models import Achievement
from main.utils import abort, save_uploaded_image
from main.utils.decorators import require_verification_token
from main.utils.dfa import check_bad_words
from util.decorator.auth import app_auth
from util.decorator.param import fetch_object, validate_args


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


class AchievementList(View):
    ORDERS = ('time_created', '-time_created')

    @app_auth
    @validate_args({
        'offset': forms.IntegerField(required=False, min_value=0),
        'limit': forms.IntegerField(required=False, min_value=0),
        'order': forms.IntegerField(required=False, min_value=0, max_value=3),
    })
    def get(self, request, offset=0, limit=10, order=1):
        user = request.user
        i, j, k = offset, offset + limit, self.ORDERS[order]
        c = user.achievements.count()
        achievements = user.achievements.order_by(k)[i:j]
        l = [{'id': a.id,
              'description': a.description,
              'picture': a.picture,
              'time_created': a.time_created} for a in achievements]
        return JsonResponse({'count': c, 'list': l})

    @require_verification_token
    @validate_args({
        'description': forms.CharField(min_length=1, max_length=100),
    })
    def post(self, request, description):
        user = request.user
        if check_bad_words(description):
            abort(403, '含有非法词汇')

        achievement = Achievement(user=user, description=description)
        picture = request.FILES.get('image')
        if picture:
            filename = save_uploaded_image(picture)
            if filename:
                achievement.picture = filename
        else:
            abort(400, '图片上传失败')
        achievement.save()

        return JsonResponse({'achievement_id': achievement.id})