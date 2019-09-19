from django import forms

from main.models import Activity, User
from main.models.activity.people import ActivityUserParticipator
from util.base.view import BaseView
from util.decorator.auth import client_auth
from util.decorator.param import validate_args, fetch_object
from web.views.activity import activity_owner


class ActivityAnalysis(BaseView):
    """活动分析"""

    KEY_ROLE = 'role'
    KEY_GENDER = 'gender'
    KEY_PROFESSION = 'profession'
    KEY_PROVINCE = 'province'
    KEY_UNIT = 'unit'

    KEY_OTHER = '其他'
    KEY_EMPTY = '未设置'

    KEY_SCHOOL = '学校'
    KEY_HOSPITAL = '医院'
    KEY_COMPANY = '企业'

    KEY_SCHOOLS = ['学校', '大学', '中学', '小学']
    KEY_HOSPITALS = ['医院']
    KEY_COMPANIES = ['公司']

    @client_auth
    @validate_args({
        'activity_id': forms.IntegerField()
    })
    @fetch_object(Activity.objects, 'activity')
    @activity_owner()
    def get(self, request, activity, **kwargs):
        result = self.__init_result_template()
        users = ActivityUserParticipator.objects.filter(activity=activity)
        for u in users:
            self.__analysis_on_person(u.user, result)
        result['sum'] = users.count()
        return self.success(result)

    def __analysis_on_person(self, user, result):
        # 性别
        result[ActivityAnalysis.KEY_GENDER][User.GENDERS[user.gender]] += 1
        # 角色
        if user.is_role_verified != 2 or not user.role:
            # 未设置
            result[ActivityAnalysis.KEY_ROLE][ActivityAnalysis.KEY_EMPTY] += 1
        elif user.role in result[ActivityAnalysis.KEY_ROLE]:
            result[ActivityAnalysis.KEY_ROLE][user.role] += 1
        else:
            # 其他角色
            result[ActivityAnalysis.KEY_ROLE][ActivityAnalysis.KEY_OTHER] += 1
        # 专业
        if not user.profession:
            result[ActivityAnalysis.KEY_PROFESSION][ActivityAnalysis.KEY_EMPTY] += 1
        elif user.profession in result[ActivityAnalysis.KEY_PROFESSION]:
            result[ActivityAnalysis.KEY_PROFESSION][user.profession] += 1
        else:
            result[ActivityAnalysis.KEY_PROFESSION][user.profession] = 1

        # 地区
        if not user.province:
            result[ActivityAnalysis.KEY_PROVINCE][ActivityAnalysis.KEY_EMPTY] += 1
        elif user.province in result[ActivityAnalysis.KEY_PROVINCE]:
            result[ActivityAnalysis.KEY_PROVINCE][user.province] += 1
        else:
            result[ActivityAnalysis.KEY_PROVINCE][user.province] = 1

        # 组织类型
        result[ActivityAnalysis.KEY_UNIT][self.__get_unit_category(user.unit1)] += 1
        pass

    def __init_result_template(self):
        return {
            ActivityAnalysis.KEY_ROLE: {
                '专家': 0,
                '学生': 0,
                ActivityAnalysis.KEY_OTHER: 0,
                ActivityAnalysis.KEY_EMPTY: 0,
            },
            ActivityAnalysis.KEY_GENDER: {
                '男': 0,
                '女': 0,
                '未知': 0,
            },
            ActivityAnalysis.KEY_PROFESSION: {
                ActivityAnalysis.KEY_EMPTY: 0,
            },
            ActivityAnalysis.KEY_PROVINCE: {},
            ActivityAnalysis.KEY_UNIT: {
                ActivityAnalysis.KEY_SCHOOL: 0,
                ActivityAnalysis.KEY_COMPANY: 0,
                ActivityAnalysis.KEY_HOSPITAL: 0,
                ActivityAnalysis.KEY_OTHER: 0,
                ActivityAnalysis.KEY_EMPTY: 0,
            },
        }

    def __get_unit_category(self, unit):
        if not unit:
            return ActivityAnalysis.KEY_EMPTY
        unit = ''
        # 判断学校
        for k in ActivityAnalysis.KEY_SCHOOLS:
            if k in unit:
                return ActivityAnalysis.KEY_SCHOOL
        # 判断企业
        for k in ActivityAnalysis.KEY_COMPANIES:
            if k in unit:
                return ActivityAnalysis.KEY_COMPANY
        # 判断医院
        for k in ActivityAnalysis.KEY_HOSPITALS:
            if k in unit:
                return ActivityAnalysis.KEY_HOSPITAL
        return ActivityAnalysis.KEY_OTHER
        pass
