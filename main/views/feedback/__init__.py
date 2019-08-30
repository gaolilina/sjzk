from django import forms
from django.views.generic import View

from main.utils import get_score_stage, abort
from util.decorator.auth import app_auth
from util.decorator.param import validate_args


class Feedback(View):
    @app_auth
    @validate_args({
        'content': forms.CharField(max_length=200),
    })
    def post(self, request, content):
        """用户意见反馈

        :param content: 反馈内容
        :return: 200
        """
        if request.user.feedback.count() == 0:
            request.user.score += get_score_stage(2)
            request.user.score_records.create(
                score=get_score_stage(2), type="活跃度",
                description="增加一条反馈")
            request.user.save()
        request.user.feedback.create(content=content)
        abort(200)