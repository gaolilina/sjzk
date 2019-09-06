from django import forms

from modellib.models import Field
from util.base.view import BaseView
from util.decorator.auth import cms_auth
from util.decorator.param import validate_args, fetch_object
from util.decorator.permission import cms_permission


class FieldList(BaseView):

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
        fields = Field.objects.filter(**filter_param)
        fields = [{
            'name': f.name,
            'id': f.id,
            'enable': f.enable,
        } for f in fields]
        return self.success({
            'count': len(fields),
            'fields': fields
        })

    @cms_auth
    @cms_permission('create_field')
    @validate_args({
        'name': forms.CharField(max_length=20),
        'parent_id': forms.IntegerField(required=False),
    })
    @fetch_object(Field.objects, 'parent', force=False)
    def post(self, request, name, parent=None, **kwargs):
        if Field.objects.filter(name=name).exists():
            return self.fail(-1, '已经存在领域')
        Field.objects.create(name=name, parent=parent)
        return self.success()


class FieldEnable(BaseView):

    @cms_auth
    @cms_permission('enable_field')
    @validate_args({
        'field_id': forms.IntegerField(),
    })
    @fetch_object(Field.objects, 'field')
    def post(self, request, field, **kwargs):
        Field.objects.filter(id=field.id).update(enable=True)
        return self.success()

    @cms_auth
    @cms_permission('disable_field')
    @validate_args({
        'field_id': forms.IntegerField(),
    })
    @fetch_object(Field.objects, 'field')
    def delete(self, request, field, **kwargs):
        Field.objects.filter(id=field.id).update(enable=False)
        return self.success()
