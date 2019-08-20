from django import forms
from django.views.generic import View

from util.decorator.auth import app_auth
from util.decorator.param import validate_args
from main.utils import abort, identity_verify, get_score_stage, eid_verify, save_uploaded_image
from main.views.user import Profile as Profile_


# noinspection PyClassHasNoInit
class IdentityVerificationView(Profile_):
    @app_auth
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
    @app_auth
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
    @app_auth
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
    @app_auth
    def get(self, request):
        """检查是否已上传身份证照片"""

        if request.user.id_card:
            abort(200)
        abort(404, '未设置头像')

    @app_auth
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
    @app_auth
    def get(self, request):
        """检查是否已上传其他证件照片"""

        if request.user.other_card:
            abort(200)
        abort(404, '未上传图片')

    @app_auth
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
