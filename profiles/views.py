from datetime import datetime

from django.db import transaction
from django.http import \
    JsonResponse, HttpResponse, HttpResponseForbidden, HttpResponseBadRequest

from web_service.decorators import web_service
from user.models import User
from profiles.models import UserProfile
from location.tools import set_location, get_location
from tag.tools import get_tags, set_tags


def user_profile(request, user_id=None):
    @web_service(method='GET')
    def get(request, user_id):
        """
        获取用户个人资料

        :return:
            name - 昵称
            description - 个人描述
            email - 邮箱地址
            gender - 性别（0-保密，1-男，2-女）
            birthday - 生日（格式：YYYY-MM-DD）
            location - 位置信息（列表类型，格式：[x, y]，x：省索引，y：市索引）

            tags - 标签列表
            create_time - 注册时间
        """
        if not user_id:
            user = request.user
        else:
            try:
                user_id = int(user_id)
                user = User.enabled.get(id=user_id)
            except (User.DoesNotExist, KeyError):
                return HttpResponseBadRequest()

        r = {  # from User
            'name': user.name,
            'email': user.email,
            'create_time': user.create_time,
        }

        try:  # from UserProfile
            profile = user.profile
        except UserProfile.DoesNotExist:
            profile = UserProfile(user=user)
            profile.save()
        r['description'] = profile.description
        r['gender'] = profile.gender
        r['birthday'] = profile.birthday.strftime('%Y-%m-%d') \
            if profile.birthday else None

        # from UserLocation
        r['location'] = get_location(user)

        # from UserTag
        r['tags'] = get_tags(user)

        return JsonResponse(r)

    @web_service()
    @transaction.atomic
    def post(request, data):
        """
        修改用户个人资料

        :param data: 接受以下数据项
            name - 昵称
            description - 个人描述
            email - 邮箱地址
            gender - 性别（0-保密，1-男，2-女）
            birthday - 生日（格式：YYYY-MM-DD）
            location - 位置信息（列表类型）
                [x, y] | [x, None] | [None, None]
            tags - 标签列表
        :return: 200 | 400
        """
        user = request.user

        # to User
        if 'name' in data:
            user.name = data['name']
        if 'email' in data:
            user.email = data['email']
        user.save()

        try:  # to UserProfile
            profile = user.profile
        except UserProfile.DoesNotExist:
            profile = UserProfile(user=user)
        if 'description' in data:
            profile.description = data['description']
        if 'gender' in data:
            if data['gender'] not in [0, 1, 2]:
                raise ValueError('invalid gender value %s' % data['gender'])
            profile.gender = data['gender']
        if 'birthday' in data:
            profile.birthday = \
                datetime.strptime(data['birthday'], '%Y-%m-%d').date() \
                if data['birthday'] else None
        profile.save()

        # to UserLocation
        if 'location' in data:
            set_location(user, data['location'])

        # to UserTag
        if 'tags' in data:
            set_tags(user, data['tags'])

        return HttpResponse()

    if request.method == 'GET':
        return get(request, user_id)
    elif request.method == 'POST' and not user_id:
        return post(request)
    else:
        return HttpResponseForbidden()
