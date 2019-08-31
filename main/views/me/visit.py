from main.models import User
from main.views.common import VisitorList
from util.decorator.auth import app_auth
from util.decorator.param import fetch_object


class UserVisitorList(VisitorList):
    @app_auth
    @fetch_object(User.enabled, 'user')
    def get(self, request, user=None):
        user = user or request.user
        return super().get(request, user)