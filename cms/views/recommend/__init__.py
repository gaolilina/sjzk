from recommend.user_sim import user_sim
from util.base.view import BaseView
from util.decorator.auth import cms_auth
from util.decorator.permission import cms_permission


class CalculateUserSim(BaseView):

    @cms_auth
    @cms_permission('calculate_user_sim')
    def get(self, request, **kwargs):
        user_sim()
        return self.success()
