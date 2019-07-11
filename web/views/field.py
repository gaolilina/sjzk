from django import forms
from django.http import JsonResponse
from django.views.generic.base import View

from main.utils.decorators import validate_args, fetch_object
from modellib.models.independency.field import Field


class FieldList(View):

    def get(self, request):
        count = Field.objects.count()
        fields = None
        if count > 0:
            fields = Field.objects.all()
            fields = [{
                'name': f.name,
                'id': f.id,
            } for f in fields]
        return JsonResponse({
            'count': count,
            'fields': fields
        })

    @validate_args({
        'name': forms.CharField(max_length=20)
    })
    def post(self, request, name, **kwargs):
        if Field.objects.filter(name=name).count() > 0:
            return JsonResponse({
                'code': -1,
                'msg': '已经存在领域'
            })
        Field.objects.create(name=name)
        return JsonResponse({})


class FieldDelete(View):
    @validate_args({
        'field_id': forms.IntegerField()
    })
    @fetch_object(Field.objects, 'field')
    def delete(self, request, field, **kwargs):
        field.delete()
        return JsonResponse({})
