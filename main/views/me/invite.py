from django.db import IntegrityError
from django.http import JsonResponse
from django.views.generic import View

from main.models import User
from main.utils import abort
from util.decorator.auth import app_auth


class InvitationCode(View):
    @app_auth
    def get(self, request):
        """获取用户自己的邀请码

        :return: invitation_code: 邀请码
        """
        invitation_code = request.user.invitation_code
        return JsonResponse({'invitation_code': invitation_code})


class Inviter(View):
    @app_auth
    def get(self, request):
        """获取用户自己的邀请者信息

        """
        used_invitation_code = request.user.used_invitation_code
        if not used_invitation_code:
            abort(403, '你没有邀请人')
        try:
            user = User.enabled.get(invitation_code=used_invitation_code)
        except IntegrityError:
            abort(404, '该用户已不存在')
        else:
            r = {'id': user.id,
                 'time_created': user.time_created,
                 'name': user.name,
                 'icon_url': user.icon,
                 'description': user.description,
                 'gender': user.gender,
                 'birthday': user.birthday,
                 'province': user.province,
                 'city': user.city,
                 'county': user.county,
                 'tags': [tag.name for tag in user.tags.all()],
                 'follower_count': user.followers.count(),
                 'followed_count': user.followed_users.count() +
                                   user.followed_teams.count(),
                 'friend_count': user.friends.count(),
                 'liker_count': user.likers.count(),
                 'visitor_count': user.visitors.count(),
                 'is_verified': user.is_verified,
                 'is_role_verified': user.is_role_verified,
                 'role': user.role,
                 'adept_field': user.adept_field,
                 'adept_skill': user.adept_skill,
                 'expect_role': user.expect_role,
                 'follow_field': user.follow_field,
                 'follow_skill': user.follow_skill,
                 'unit1': user.unit1,
                 'unit2': user.unit2,
                 'profession': user.profession,
                 'score': user.score}
            return JsonResponse(r)