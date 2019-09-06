from django import forms

from modellib.models import Skill
from util.base.view import BaseView
from util.decorator.auth import cms_auth
from util.decorator.param import validate_args, fetch_object
from util.decorator.permission import cms_permission


class SkillList(BaseView):

    @cms_auth
    @validate_args({
        'name': forms.CharField(required=False, max_length=20),
        'enable': forms.BooleanField(required=False),
    })
    def get(self, request, name=None, enable=None, **kwargs):
        filter_param = {}
        if enable is not None:
            filter_param['enable'] = enable
        if name:
            filter_param['name__icontains'] = name
        skills = Skill.objects.filter(**filter_param)
        skills = [{
            'name': f.name,
            'id': f.id,
            'enable': f.enable,
        } for f in skills]
        return self.success({
            'count': len(skills),
            'list': skills
        })

    @cms_auth
    @cms_permission('create_skill')
    @validate_args({
        'name': forms.CharField(max_length=20),
        'parent_id': forms.IntegerField(required=False),
    })
    @fetch_object(Skill.objects, 'parent', force=False)
    def post(self, request, name, parent=None, **kwargs):
        if Skill.objects.filter(name=name).exists():
            return self.fail(-1, '已经存在领域')
        Skill.objects.create(name=name, parent=parent)
        return self.success()


class SkillEnable(BaseView):

    @cms_auth
    @cms_permission('enable_skill')
    @validate_args({
        'skill_id': forms.IntegerField(),
    })
    @fetch_object(Skill.objects, 'skill')
    def post(self, request, skill, **kwargs):
        Skill.objects.filter(id=skill.id).update(enable=True)
        return self.success()

    @cms_auth
    @cms_permission('disable_skill')
    @validate_args({
        'skill_id': forms.IntegerField(),
    })
    @fetch_object(Skill.objects, 'skill')
    def delete(self, request, skill, **kwargs):
        Skill.objects.filter(id=skill.id).update(enable=False)
        return self.success()
