from django import forms

from main.models import Activity
from modellib.models.need import UserNeed
from util.base.view import BaseManyToManyView, BaseView
from util.decorator.auth import client_auth
from util.decorator.param import fetch_object, validate_args


class UserNeedList(BaseView):

    @client_auth
    @validate_args({
        'activity_id': forms.IntegerField(required=False),
    })
    @fetch_object(Activity.objects, 'activity', force=False)
    def get(self, request, activity=None, **kwargs):
        qs = UserNeed.objects.filter(activity=activity)
        return self.success_list(request, qs, need_to_json)

    @client_auth
    @validate_args({
        'tags': forms.CharField(max_length=250),
        'desc': forms.CharField(max_length=250),
        'activity_id': forms.IntegerField(required=False),
    })
    @fetch_object(Activity.objects, 'activity', force=False)
    def post(self, request, tags, desc, activity=None, **kwargs):
        UserNeed.objects.create(field=tags, desc=desc, user=request.user, activity=activity)
        return self.success()


class MyUserNeedList(BaseView):

    @client_auth
    def get(self, request, **kwargs):
        qs = UserNeed.objects.filter(user=request.user)
        return self.success_list(request, qs, need_to_json)


class DeleteMyUserNeed(BaseView):

    @client_auth
    @fetch_object(UserNeed.objects, 'need')
    def delete(self, request, need):
        if need.user != request.user:
            return self.fail(1, '该需求不是您发布的，无权删除')
        UserNeed.objects.filter(id=need.id).delete()


class IDoSomethingOnUserNeed(BaseManyToManyView):

    @fetch_object(UserNeed.objects, 'need')
    def post(self, request, need, field, **kwargs):
        return super().post(request, need, field)

    @fetch_object(UserNeed.objects, 'need')
    def delete(self, request, need, field, **kwargs):
        return super().delete(request, need, field)


def need_to_json(need):
    return {
        'id': need.id,
        'user_id': need.user_id,
        'desc': need.desc,
        'count_likers': need.likers.all().count(),
        'tags': need.field,
    }
