from django.views.generic import View
from django.core.exceptions import ObjectDoesNotExist
from django.http import JsonResponse

from ..models import System as SystemModel
from ..utils import abort


__all__ = ['VersionNumber']


class VersionNumber(View):
    def get(self, request):
        """获取app当前版本号"""

        try:
            num = SystemModel.objects.get(id=1).VERSION_NUMBER
            return JsonResponse({'VERSION_NUMBER': num})
        except ObjectDoesNotExist:
            abort(400)
