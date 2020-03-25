from django import forms

from cms.util.getWord import getDetail

from modellib.models.comboBox import ComboBox
from util.base.view import BaseView
from util.decorator.param import validate_args
#from util.decorator.auth import cms_auth
#from util.decorator.permission import cms_permission

class comboBox(BaseView):
    '''根据键值获取选项'''

    #@cms_auth
    @validate_args({
        'key': forms.CharField(max_length=254),
    })

    def get(self, request, key, **kwargs):                #根据键值获取选项
        combo = ComboBox.objects.filter(key = key)
        if combo:
            dict = getDetail(combo[0].id, False)
        else:
            return self.fail(code=1, msg='key值不存在')
        return self.success({
            'result' : dict
        })

