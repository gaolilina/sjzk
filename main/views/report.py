from django import forms
from django.views.generic import View

from main.models import Report as ReportModel
from main.utils import abort
from main.utils.decorators import *
from util.decorator.param import validate_args

__all__ = ['Report']


class Report(View):
    type_list = ['user', 'team', 'need', 'activity', 'competition',
                 'forum', 'internal_task', 'external_task',
                 'user_action', 'team_action']

    @require_verification_token
    @validate_args({
        'type': forms.CharField(max_length=20),
        'object_id': forms.IntegerField(min_value=1),
        'content': forms.CharField(max_length=100),
    })
    def post(self, request, type, object_id, content):
        """举报
        :param type: 举报对象的类型
        :param object_id: 举报对象的ID
        :param content: 举报原因

        :return 400/200
        """

        if type not in self.type_list:
            abort(400, '举报对象类型错误')

        report = ReportModel(
            user=request.user, type=type, object_id=object_id, content=content)
        report.save()
        abort(200)
