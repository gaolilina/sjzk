from django import forms

from modellib.models.comboBox import ComboBox
from util.base.view import BaseView

from util.decorator.param import validate_args
from util.decorator.auth import client_auth

class comboBox(BaseView):
    '''客户端根据键值获取选项'''

    #@client_auth
    @validate_args({
        'key': forms.CharField(max_length=254),
    })
    def get(self, request, key, **kwargs):  # 根据键值获取选项
        combo = ComboBox.objects.filter(key=key)
        if combo.exists():
            dict = getDetail(combo.first().id, False)
        else:
            return self.fail(code=1, msg='key值不存在')
        return self.success(dict)


def getDetail(id, hasId):
    if id == None:
        return
    dict = {}
    combo = ComboBox.objects.filter(id = id)[0]
    if hasId:
        dict['id'] = id
    dict['value'] = combo.value
    for child in combo.children.all():
        if 'child' in dict:
            dict['child'].append(getDetail(child.id, hasId))
        else:
            dict['child'] = []
            dict['child'].append(getDetail(child.id, hasId))

    return dict