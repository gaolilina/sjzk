from main.models import TeamAction
from main.views.favor import FavoredActionList, IFavorSomething
from util.decorator.auth import app_auth
from util.decorator.param import fetch_object


class FavoredTeamActionList(FavoredActionList):
    @app_auth
    def get(self, request):
        return super().get(request, request.user.favored_team_actions)


class FavoredTeamAction(IFavorSomething):
    @fetch_object(TeamAction.objects, 'action')
    def get(self, request, action):
        return super().get(request, action)

    @fetch_object(TeamAction.objects, 'action')
    def post(self, request, action):
        return super().post(request, action)

    @fetch_object(TeamAction.objects, 'action')
    def delete(self, request, action):
        return super().delete(request, action)