from main.models import Activity
from main.views.like import ILikeSomething
from util.decorator.param import fetch_object


class LikedActivity(ILikeSomething):
    @fetch_object(Activity.enabled, 'activity')
    def get(self, request, activity):
        return super().get(request, activity)

    @fetch_object(Activity.enabled, 'activity')
    def post(self, request, activity):
        return super().post(request, activity)

    @fetch_object(Activity.enabled, 'activity')
    def delete(self, request, activity):
        return super().delete(request, activity)
