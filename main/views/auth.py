from django import forms
from django.db import transaction, IntegrityError
from django.http import JsonResponse
from django.views.generic import View

from ChuangYi.settings import DEFAULT_ICON_URL, SERVER_URL
from main.models import User, UserValidationCode
from rongcloud import RongCloud
from ..utils import abort, identity_verify, get_score_stage, eid_verify, save_uploaded_image
from ..utils.decorators import *
from ..views.user import Profile as Profile_


class Account(View):
    @validate_args({
        'method': forms.CharField(max_length=20),
        'username': forms.RegexField(r'^[a-zA-Z0-9_]{4,15}$', strip=True, required=False),
        'password': forms.CharField(min_length=6, max_length=20, strip=False, required=False),
        'openid': forms.CharField(min_length=28, max_length=28, required=False)
    })
    def get(self, request, method, username=None, password=None, openid=None, **kwargs):
        if method == 'phone':
            try:
                if username.isdigit():
                    user = User.objects.get(phone_number=username)
                else:
                    user = User.objects.get(username=username.lower())
            except User.DoesNotExist:
                abort(401, '用户不存在')
            if not user.check_password(password):
                abort(401, '密码错误')
        elif method == 'wechat':
            try:
                user = User.objects.get(wechat_id=openid)
            except User.DoesNotExist:
                abort(401, '用户不存在')
        else:
            abort(400)
            return
        # 查找到用户
        if not user.is_enabled:
            abort(403, '用户已删除')
        # user.update_token()
        if not user.icon:
            portraitUri = SERVER_URL + user.icon
        else:
            portraitUri = DEFAULT_ICON_URL
        rcloud = RongCloud()
        r = rcloud.User.getToken(
            userId=user.id, name=user.name,
            portraitUri=portraitUri)
        token = r.result['token']
        user.token = token
        user.save()
        return JsonResponse({'token': user.token})

    @validate_args({
        'phone_number': forms.CharField(min_length=11, max_length=11),
        'password': forms.CharField(min_length=6, max_length=32),
        'validation_code': forms.CharField(min_length=6, max_length=6),
        'invitation_code': forms.CharField(required=False),
        'role': forms.CharField(required=False),
        'openid': forms.CharField(max_length=28, min_length=28, required=False),
        'nickname': forms.CharField(max_length=15, required=False),
        'gender': forms.IntegerField(required=False, min_value=0, max_value=2),
        'province': forms.CharField(required=False, max_length=20),
        'city': forms.CharField(required=False, max_length=20),
        'icon': forms.CharField(required=False, max_length=255)
    })
    def post(self, request, method, phone_number, password, validation_code,
             invitation_code=None, role='', icon=None,
             openid=None, nickname=None, gender=0, province=None, city=DEFAULT_ICON_URL):
        """注册，若成功返回用户令牌"""
        if method == 'phone':
            pass
        elif method == 'wechat':
            if openid is None or nickname is None or province is None or city is None:
                abort(400, 'openid 不能为空')
                return
        else:
            abort(400)
            return
        if not UserValidationCode.verify(phone_number, validation_code):
            abort(400, '验证码错误')

        with transaction.atomic():
            try:
                user = User(phone_number=phone_number, role=role, openid=openid, city=city, province=province,
                            gender=gender, icon = icon)
                user.set_password(password)
                # user.update_token()
                if nickname is None:
                    user.save_and_generate_name()
                else:
                    user.name = nickname
                user.create_invitation_code()
                # 注册成功后给融云服务器发送请求获取Token
                rcloud = RongCloud()
                r = rcloud.User.getToken(
                    userId=user.id, name=user.name,
                    portraitUri=icon)
                token = r.result['token']
                user.token = token
                if invitation_code:
                    u = User.enabled.filter(invitation_code=invitation_code)
                    if not u:
                        abort(404, '推荐码错误')
                    user.used_invitation_code = invitation_code
                    u.score_records.create(
                        score=get_score_stage(4), type="活跃度",
                        description="邀请码被使用")
                # 加积分
                user.score += get_score_stage(3)
                user.score_records.create(
                    score=get_score_stage(3), type="初始数据",
                    description="首次手机号注册")
                user.save()
                return JsonResponse({'token': user.token})
            except IntegrityError:
                abort(403, '创建用户失败')


# noinspection PyClassHasNoInit
class IdentityVerificationView(Profile_):
    @require_token
    @validate_args({
        'real_name': forms.CharField(max_length=20),
        'id_number': forms.CharField(min_length=18, max_length=18),
    })
    def post(self, request, **kwargs):
        """实名认证

        :param kwargs:
            real_name: 真实姓名
            id_number: 身份证号码
        """

        if not request.user.id_card:
            abort(403, '请先上传身份证照片')
        id_keys = ('real_name', 'id_number')
        # 调用第三方接口验证身份证的正确性
        res = identity_verify(kwargs['id_number'], kwargs['real_name'])
        if res != 1:
            abort(404, '身份证号和姓名不匹配')

        # 用户未提交实名信息或者等待重新审核
        if request.user.is_verified in [0, 3]:
            for k in id_keys:
                setattr(request.user, k, kwargs[k])
        # 将实名认证状态码改为1表示待审核状态
        request.user.is_verified = 1
        request.user.save()
        abort(200)


# noinspection PyClassHasNoInit
class EidIdentityVerificationView(Profile_):
    @require_token
    @validate_args({
        'real_name': forms.CharField(max_length=20),
        'id_number': forms.CharField(min_length=18, max_length=18),
        'eid_issuer': forms.CharField(max_length=20),
        'eid_issuer_sn': forms.CharField(max_length=20),
        'eid_sn': forms.CharField(max_length=50),
        'data_to_sign': forms.CharField(),
        'eid_sign': forms.CharField(),
        'eid_sign_algorithm': forms.CharField(),
    })
    def post(self, request, **kwargs):
        """eid实名认证

        :param kwargs:
            real_name: 真实姓名
            id_number: 身份证号码
            eid_issuer: eid相关信息
            eid_issuer_sn: eid相关信息
            eid_sn: eid: eid相关信息
            data_to_sign: 待签原文的base64字符串
            eid_sign: eid卡对签名原文的签名结果
            eid_sign_algorithm: eid卡进行签名的类型
        """

        id_keys = ('real_name', 'id_number', 'eid_issuer', 'eid_issuer_sn',
                   'eid_sn')

        # 调用eid接口验证用户信息
        data = {
            'eidIssuer': kwargs['eid_issuer'],
            'eidIssuerSn': kwargs['eid_issuer_sn'],
            'eidSn': kwargs['eid_sn'],
            'idNum': kwargs['id_number'],
            'name': kwargs['real_name'],
            'dataToSign': kwargs['data_to_sign'],
            'eidSign': kwargs['eid_sign'],
            'eidSignAlgorithm': kwargs['eid_sign_algorithm'],
        }
        res = eid_verify(data)
        if res != 1:
            abort(res, 'eid信息与身份证信息不符')

        # 验证成功后，若用户当前的状态时待审核或者审核未通过，则将用户相关信息保存到数据库
        if request.user.is_verified in [0, 3]:
            for k in id_keys:
                if k in kwargs:
                    setattr(request.user, k, kwargs[k])

        # 积分相关
        if not request.user.id_card:
            request.user.score += get_score_stage(5)
            request.user.score_records.create(
                score=get_score_stage(5), type="初始数据",
                description="首次Eid认证")
        # 将实名认证状态码改为4表示EID认证通过
        request.user.is_verified = 4
        request.user.save()
        abort(200)


# noinspection PyClassHasNoInit
class OtherIdentityVerificationView(Profile_):
    @require_token
    @validate_args({
        'role': forms.CharField(max_length=20),
        'unit1': forms.CharField(max_length=20),
    })
    def post(self, request, **kwargs):
        """资格认证

        :param kwargs:
            role: 角色
            unit1: 机构
        """
        checkIdVerified(request.user)
        if not request.user.other_card:
            abort(403, '请先上传照片')

        role_keys = ('role', 'unit1')

        # 用户未提交身份审核信息或者审核未通过
        if request.user.is_role_verified in [0, 3]:
            for k in role_keys:
                if k in kwargs:
                    setattr(request.user, k, kwargs[k])

        # 将身份认证状态设为1表示待审核
        request.user.is_role_verified = 1
        request.user.save()
        abort(200)


class IDCardView(View):
    @require_token
    def get(self, request):
        """检查是否已上传身份证照片"""

        if request.user.id_card:
            abort(200)
        abort(404, '未设置头像')

    @require_token
    def post(self, request):
        """上传身份证照片"""

        # 等待审核或者已通过审核不能上传照片
        if request.user.is_verified in [1, 2]:
            abort(403, '等待审核或已实名认证')
        if request.user.is_verified == 4:
            abort(403, '已通过eid认证')

        id_card = request.FILES.get('image')
        if not id_card:
            abort(400, '图片上传失败')

        filename = save_uploaded_image(id_card, is_private=True)
        if filename:
            if not request.user.id_card:
                request.user.score += get_score_stage(5)
                request.user.score_records.create(
                    score=get_score_stage(5), type="初始数据",
                    description="首次实名认证")
            request.user.id_card = filename
            request.user.save()
            abort(200)
        abort(400, '图片保存失败')


class OtherCardView(View):
    @require_token
    def get(self, request):
        """检查是否已上传其他证件照片"""

        if request.user.other_card:
            abort(200)
        abort(404, '未上传图片')

    @require_token
    def post(self, request):
        """上传其他证件照片"""
        checkIdVerified(request.user)

        if request.user.is_role_verified:
            abort(403, '已经通过认证')

        other_card = request.FILES.get('image')
        if not other_card:
            abort(400, '图片上传失败')

        filename = save_uploaded_image(other_card, is_private=True)
        if filename:
            if not request.user.other_card:
                request.user.score += get_score_stage(5)
                request.user.score_records.create(
                    score=get_score_stage(5), type="初始数据",
                    description="首次身份认证")
            request.user.other_card = filename
            request.user.save()
            abort(200)
        abort(400, '图片保存失败')


def checkIdVerified(user):
    if user.is_verified in [0, 3]:
        abort(403, '请先进行实名认证')
