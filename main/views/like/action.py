from main.models import UserAction, TeamAction, SystemAction
from main.views.like import ILikeSomething
from util.decorator.param import fetch_object


class LikedUserAction(ILikeSomething):
    @fetch_object(UserAction.objects, 'action')
    def get(self, request, action):
        return super().get(request, action)

    @fetch_object(UserAction.objects, 'action')
    def post(self, request, action):
        return super().post(request, action)

    @fetch_object(UserAction.objects, 'action')
    def delete(self, request, action):
        return super().delete(request, action)


class LikedTeamAction(ILikeSomething):
    @fetch_object(TeamAction.objects, 'action')
    def get(self, request, action):
        return super().get(request, action)

    @fetch_object(TeamAction.objects, 'action')
    def post(self, request, action):
        return super().post(request, action)

    @fetch_object(TeamAction.objects, 'action')
    def delete(self, request, action):
        return super().delete(request, action)


class LikedSystemAction(ILikeSomething):
    @fetch_object(SystemAction.objects, 'action')
    def get(self, request, action):
        return super().get(request, action)

    @fetch_object(SystemAction.objects, 'action')
    def post(self, request, action):
        return super().post(request, action)

    @fetch_object(SystemAction.objects, 'action')
    def delete(self, request, action):
        return super().delete(request, action)
