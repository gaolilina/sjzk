from main.models import UserTag, TeamTag
from main.views.like import LikedEntity
from util.decorator.param import fetch_object


class LikedUserTag(LikedEntity):
    @fetch_object(UserTag.objects, 'tag')
    def get(self, request, tag):
        return super().get(request, tag)

    @fetch_object(UserTag.objects, 'tag')
    def post(self, request, tag):
        return super().post(request, tag)

    @fetch_object(UserTag.objects, 'tag')
    def delete(self, request, tag):
        return super().delete(request, tag)


class LikedTeamTag(LikedEntity):
    @fetch_object(TeamTag.objects, 'tag')
    def get(self, request, tag):
        return super().get(request, tag)

    @fetch_object(TeamTag.objects, 'tag')
    def post(self, request, tag):
        return super().post(request, tag)

    @fetch_object(TeamTag.objects, 'tag')
    def delete(self, request, tag):
        return super().delete(request, tag)