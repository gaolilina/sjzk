from datetime import datetime

from django.db import transaction
from django.http import \
    JsonResponse, HttpResponse, HttpResponseForbidden, HttpResponseBadRequest

from location.tools import set_location, get_location
from profiles.models import \
    UserProfile, UserIdentification, UserStudentIdentification
from tag.tools import get_tags, set_tags
from user.models import User
from visit.tools import update_visitor
from web_service.decorators import web_service


def user_profile(request, user_id=None):
    @web_service(method='GET')
    def get(request, user_id):
        """
        获取用户个人资料

        :return:
            name: 昵称
            description: 个人描述
            email: 邮箱地址
            gender: 性别（0-保密，1-男，2-女）
            birthday: 生日（格式：YYYY-MM-DD）
            location: 位置信息（列表类型，格式：[x, y]，x：省索引，y：市索引）
            tags: 标签列表
            create_time: 注册时间
        """
        if not user_id:
            user = request.user
        else:
            try:
                user_id = int(user_id)
                user = User.enabled.get(id=user_id)
            except (User.DoesNotExist, KeyError):
                return HttpResponseBadRequest()

        if user is not request.user:  # 更新来访信息
            update_visitor(user, request.user)

        r = {  # from User
            'name': user.name,
            'email': user.email,
            'create_time': user.create_time,
        }

        try:  # from UserProfile
            profile = user.profile
            r['description'] = profile.description
            r['gender'] = profile.gender
            r['birthday'] = profile.birthday.strftime('%Y-%m-%d') \
                if profile.birthday else None
        except UserProfile.DoesNotExist:
            r['description'] = ''
            r['gender'] = 0
            r['birthday'] = None

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
            name: 昵称
            description: 个人描述
            email: 邮箱地址
            gender: 性别（0-保密，1-男，2-女）
            birthday: 生日（格式：YYYY-MM-DD）
            location: 位置信息（列表类型）
                [x, y] | [x, None] | [None, None]
            tags: 标签列表
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
                return HttpResponseBadRequest()
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


def user_profile_identification(request):
    @web_service(method='GET')
    def get(request):
        """
        获取当前用户的身份信息

        :return:
            name: 真实姓名
            number: 身份证号
            is_verified: 是否通过验证
        """
        try:
            r = {
                'name': request.user.identification.name,
                'number': request.user.identification.number,
                'is_verified': request.user.identification.is_verified,
            }
        except UserIdentification.DoesNotExist:
            r = {'name': '', 'number': '', 'is_verified': False}

        return JsonResponse(r)

    @web_service()
    def post(request, data):
        """
        修改当前用户的身份信息，若已通过身份认证则无法修改

        :param data:
            name: 真实姓名
            number: 身份证号
        :return: 200 | 400 | 403
        """
        identification, is_created = UserIdentification.objects.get_or_create(
            user=request.user)

        if not is_created and identification.is_verified:
            return HttpResponseForbidden()

        if 'name' in data:
            identification.name = data['name']
        if 'number' in data:
            if data['number'].isdigit() and len(data['number']) == 18:
                identification.number = data['number']
            else:
                return HttpResponseBadRequest()
        identification.save()

        return HttpResponse()

    if request.method == 'GET':
        return get(request)
    elif request.method == 'POST':
        return post(request)
    else:
        return HttpResponseForbidden()


@web_service(method='GET')
def user_profile_identification_verification(request):
    """
    检查用户是否已经通过实名认证

    :return:
        is_verified: true | false
    """
    try:
        return JsonResponse(
            {'is_verified': request.user.identification.is_verified})
    except UserIdentification.DoesNotExist:
        return JsonResponse({'is_verified': False})


def user_profile_student_identification(request):
    @web_service(method='GET')
    def get(request):
        """
        获取当前用户的学生信息

        :return:
            school: 学校名称
            number: 学生证号
        """
        try:
            r = {
                'school': request.user.student_identification.school,
                'number': request.user.student_identification.number,
            }
        except UserStudentIdentification.DoesNotExist:
            r = {'school': '', 'number': ''}

        return JsonResponse(r)

    @web_service()
    def post(request, data):
        """
        设置当前用户的学生信息

        :param data:
            school: 学校名称
            number: 学生证号
        :return: 200 | 400
        """
        student_identification, is_created = \
            UserStudentIdentification.objects.get_or_create(user=request.user)

        if 'school' in data:
            student_identification.school = data['school']
        if 'number' in data:
            if data['number'].isdigit():
                student_identification.number = data['number']
            else:
                return HttpResponseBadRequest()
        student_identification.save()

        return HttpResponse()

    if request.method == 'GET':
        return get(request)
    elif request.method == 'POST':
        return post(request)
    else:
        return HttpResponseForbidden()
