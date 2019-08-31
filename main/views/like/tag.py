from main.models import UserTag, TeamTag
from main.views.like import ILikeSomething
from util.decorator.param import fetch_object


class LikedUserTag(ILikeSomething):
    @fetch_object(UserTag.objects, 'tag')
    def get(self, request, tag):
        return super().get(request, tag)

    @fetch_object(UserTag.objects, 'tag')
    def post(self, request, tag):
        return super().post(request, tag)

    @fetch_object(UserTag.objects, 'tag')
    def delete(self, request, tag):
        return super().delete(request, tag)


class LikedTeamTag(ILikeSomething):
    @fetch_object(TeamTag.objects, 'tag')
    def get(self, request, tag):
        return super().get(request, tag)

    @fetch_object(TeamTag.objects, 'tag')
    def post(self, request, tag):
        return super().post(request, tag)

    @fetch_object(TeamTag.objects, 'tag')
    def delete(self, request, tag):
        return super().delete(request, tag)
