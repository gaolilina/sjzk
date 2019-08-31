from main.models import SystemAction
from main.views.favor import FavoredActionList, IFavorSomething
from util.decorator.auth import app_auth
from util.decorator.param import fetch_object


class FavoredSystemActionList(FavoredActionList):
    @app_auth
    def get(self, request):
        return super().get(request, request.user.favored_system_actions)


class FavoredSystemAction(IFavorSomething):
    @fetch_object(SystemAction.objects, 'action')
    def get(self, request, action):
        return super().get(request, action)

    @fetch_object(SystemAction.objects, 'action')
    def post(self, request, action):
        return super().post(request, action)

    @fetch_object(SystemAction.objects, 'action')
    def delete(self, request, action):
        return super().delete(request, action)