# todo: following related methods
from django.views.generic import View


class Fans(View):
    def get(self, request, user=None):
        """
        获取粉丝列表
        :param request:
        :param user:
        :return:
        """
        pass


class Fan(View):
    def get(self, request, other_user, user=None):
        """
        判断other_user是否为user的粉丝
        :param request:
        :param other_user:
        :param user:
        :return:
        """
        pass


class FollowedUsers(View):
    def get(self, request, user=None):
        """
        获取用户的关注用户列表
        :param request:
        :param user:
        :return:
        """
        pass


class FollowedUser(View):
    def get(self, request, other_user, user=None):
        """
        判断user是否关注了other_user
        :param request:
        :param other_user:
        :param user:
        :return:
        """
        pass


class FollowedUserSelf(FollowedUser):
    def post(self, request, other_user):
        """
        令当前用户关注other_user
        :param request:
        :param other_user:
        :return:
        """
        pass

    def delete(self, request, other_user):
        """
        令当前用户取消关注other_user
        :param request:
        :param other_user:
        :return:
        """
        pass


class FollowedTeams(View):
    def get(self, request, user=None):
        """
        获取用户的关注团队列表
        :param request:
        :param user:
        :return:
        """
        pass


class FollowedTeam(View):
    def get(self, request, team, user=None):
        """
        判断user是否关注了team
        :param request:
        :param team:
        :param user:
        :return:
        """
        pass


class FollowedTeamSelf(FollowedTeam):
    def post(self, request, team):
        """
        令当前用户关注team
        :param request:
        :param team:
        :return:
        """
        pass

    def delete(self, request, team):
        """
        令当前用户取消关注team
        :param request:
        :param team:
        :return:
        """
        pass

