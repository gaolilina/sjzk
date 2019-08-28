from django.http import JsonResponse
from django.views.generic import View

from main.models import Achievement
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
        achievement[who].add(request.user)
        return JsonResponse({})

    @app_auth
    @fetch_object(Achievement.objects, 'achievement')
    def delete(self, request, achievement, who):
        achievement[who].remove(request.user)
        return JsonResponse({})