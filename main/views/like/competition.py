from main.models import Competition
from main.views.like import LikedEntity
from util.decorator.param import fetch_object


class LikedCompetition(LikedEntity):
    @fetch_object(Competition.enabled, 'competition')
    def get(self, request, competition):
        return super().get(request, competition)

    @fetch_object(Competition.enabled, 'competition')
    def post(self, request, competition):
        return super().post(request, competition)

    @fetch_object(Competition.enabled, 'competition')
    def delete(self, request, competition):
        return super().delete(request, competition)