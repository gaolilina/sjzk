from django.http import JsonResponse
from django.views.generic import View

from main.models import Achievement
from main.utils import abort
from util.decorator.auth import app_auth
from util.decorator.param import fetch_object


class AchievementDoWhoView(View):
    """
    成果都有关联的群体，比如点赞者，需求者，他们称之为 who
    需要添加或移除 who 中的成员，请使用该类
    """

    @app_auth
    @fetch_object(Achievement.objects, 'achievement')
    def post(self, request, achievement, who):
        getattr(achievement, who).add(request.user)
        return JsonResponse({})

    @app_auth
    @fetch_object(Achievement.objects, 'achievement')
    def delete(self, request, achievement, who):
        getattr(achievement, who).remove(request.user)
        return JsonResponse({})


class AchievementDetail(View):
    @app_auth
    @fetch_object(Achievement.objects, 'achievement')
    def get(self, request, achievement):
        # 获取当前用户好友id.
        userIds = []
        for item in request.user.friends.all():
            userIds.append(str(item.other_user.id))
        userIds.append(str(request.user.id))
        result = {
            'achievement_id': achievement.id,
            'name': achievement.name,
            'desc': achievement.description,
            'pics': achievement.picture,
            'yes_count': achievement.likers.count(),  # 点赞数
            'is_yes': request.user in achievement.likers.all(),  # 是否点赞
            'require_count': achievement.requirers.count(),  # 需求树
            'is_require': request.user in achievement.requirers.all(),  # 是否需求
        }
        if achievement.team == None:
            result['user_id'] = achievement.user.id
            result['user_name'] = achievement.user.unit1 if achievement.user.is_role_verified else achievement.user.name
            result['real_name'] = achievement.user.real_name if str(achievement.user.id) in userIds else ''
            result['icon_url'] = achievement.user.icon
        else:
            result['team_id'] = achievement.team.id
            result['team_name'] = achievement.team.name
            result['icon_url'] = achievement.team.icon

        return JsonResponse(result)

    @app_auth
    @fetch_object(Achievement.objects, 'achievement')
    def delete(self, request, achievement):
        if achievement.team == None and achievement.user != request.user:
            abort(403, '只有本人可以操作')
        elif achievement.team != None and request.user != achievement.team.owner:
            abort(403, '只有队长可以操作')
        achievement.delete()
        abort(200)
