from util.base.view import BaseView
from util.decorator.auth import client_auth


class Profile(BaseView):

    @client_auth
    def get(self, request, **kwargs):
        user = request.user
        r = {
            'id': user.id,
            'name': user.name,
            'goodat': user.goodat,
        }
        return self.success(r)
