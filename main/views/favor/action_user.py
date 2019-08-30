from main.models import UserAction
from main.views.favor import FavoredActionList, FavoredEntity
from util.decorator.auth import app_auth
from util.decorator.param import fetch_object


class FavoredUserActionList(FavoredActionList):
    @app_auth
    def get(self, request):
        return super().get(request, request.user.favored_user_actions)


class FavoredUserAction(FavoredEntity):
    @fetch_object(UserAction.objects, 'action')
    def get(self, request, action):
        return super().get(request, action)

    @fetch_object(UserAction.objects, 'action')
    def post(self, request, action):
        return super().post(request, action)

    @fetch_object(UserAction.objects, 'action')
    def delete(self, request, action):
        return super().delete(request, action)