from django.http import JsonResponse
from django.views.generic.base import View

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
