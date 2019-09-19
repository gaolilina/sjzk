from django import forms

from main.models import Activity, User
from util.base.view import BaseView
from util.decorator.auth import client_auth
from util.decorator.param import validate_args, fetch_object
from web.views.activity import activity_owner


class ActivityExpert(BaseView):

    @client_auth
    @validate_args({
        'activity_id': forms.IntegerField()
    })
    @fetch_object(Activity.objects, 'activity')
    def get(self, request, activity, **kwargs):
        return self.success({
            'experts': [{
                'name': ex.name,
                'phone': ex.phone_number,
                'id': ex.id
            } for ex in activity.experts.all()],
        })

    @client_auth
    @validate_args({
        'activity_id': forms.IntegerField(),
        'expert_id': forms.IntegerField(),
    })
    @fetch_object(Activity.objects, 'activity')
    @fetch_object(User.enabled, 'expert')
    @activity_owner()
    def post(self, request, activity, expert, **kwargs):
        if expert.role != '专家':
            return self.fail(2, '添加的用户不是专家')
        activity.experts.add(expert)
        return self.success()

    @client_auth
    @validate_args({
        'activity_id': forms.IntegerField(),
        'expert_id': forms.IntegerField(),
    })
    @fetch_object(Activity.objects, 'activity')
    @fetch_object(User.enabled, 'expert')
    @activity_owner()
    def delete(self, request, activity, expert, **kwargs):
        if expert.role != '专家':
            return self.fail(2, '添加的用户不是专家')
        activity.experts.remove(expert)
        return self.success()
