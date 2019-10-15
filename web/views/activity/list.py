from django import forms

from main.models import Activity
from main.views.activity.user_activity import activity_to_json
from util.base.view import BaseView
from util.constant.param import CONSTANT_DEFAULT_LIMIT
from util.decorator.auth import client_auth
from util.decorator.param import validate_args


class MyCreatedActivityList(BaseView):

    @client_auth
    @validate_args({
        'page': forms.IntegerField(required=False, min_value=0),
        'limit': forms.IntegerField(required=False, min_value=0),
        'state': forms.IntegerField(required=False),
    })
    def get(self, request, state=None, page=0, limit=CONSTANT_DEFAULT_LIMIT, **kwargs):
        filter_param = {
            'owner_user': request.user,
        }
        if state is not None:
            filter_param['state'] = state
        qs = Activity.objects.filter(**filter_param)
        c = qs.count()
        l = [activity_to_json(a) for a in qs[page * limit:(page + 1) * limit]]
        return self.success({'count': c, 'list': l})
